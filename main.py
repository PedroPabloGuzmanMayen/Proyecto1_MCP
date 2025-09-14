import asyncio
import json
from typing import Optional, Dict, Tuple, Any, List
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client 

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class Client:
    """
    An MCP Client that:
      - Read a json file contaning mcp servers to use (stdio/http)
      - Can connect to several servers and adds its tools
      - Expose the tools to Claude with unique names: <servr>__<tool>
      - Routes each tool_use to the corresponding server session
    """
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

        # Multiple sessions, we can access them using server name
        self.sessions: Dict[str, ClientSession] = {}
        # We also store transports to keep them alive in the exit_stack
        self._transports: List[Any] = []

        # Index of quealified tool -> (server_name, tool_name, schema, description)
        self.tool_index: Dict[str, Tuple[str, str, Any, Optional[str]]] = {}

        self.messages = [] #To keep context along all conversation

    #Server connection
    async def connect_from_json(self, json_path: str):
        """Connects all servers defined in the mcp_config json file"""
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        servers = config.get("servers", [])
        if not servers:
            raise ValueError("JSON file do not have mcp servers")

        for entry in servers:
            name = entry["name"]
            stype = entry["type"]

            if stype == "stdio":
                params = StdioServerParameters(
                    command=entry.get("command", "python"),
                    args=entry.get("args", []),
                    env=entry.get("env", None),
                )
                read, write = await self.exit_stack.enter_async_context(stdio_client(params))
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))

            elif stype in ("http", "streamable_http", "url"):
                url = entry["url"]
                headers = entry.get("headers", None)
                # Returns read, write and session info
                read, write, _ = await self.exit_stack.enter_async_context(
                    streamablehttp_client(url=url, headers=headers)
                )
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))

            else:
                raise ValueError(f"Server type not supported: {stype}")

            # Keeps references and open sessions
            self._transports.append((name, read, write))
            await session.initialize()
            self.sessions[name] = session

        # Build tools catalog
        await self._refresh_tool_index()
        print("\nConnected to server:", list(self.sessions.keys()))
        print("Available tools:",
              [qualified for qualified in self.tool_index.keys()])

    async def _refresh_tool_index(self):
        """Rebuilds tool index using all servers"""
        self.tool_index.clear()
        for server_name, session in self.sessions.items():
            resp = await session.list_tools()
            for tool in resp.tools:
                qualified = self._qualify(server_name, tool.name)
                self.tool_index[qualified] = (
                    server_name,
                    tool.name,
                    tool.inputSchema,
                    tool.description,
                )

    @staticmethod
    def _qualify(server: str, tool: str) -> str:
        """Generates a correct name for Anthropic"""
        return f"{server}__{tool}"

    def _route_tool(self, qualified: str) -> Tuple[ClientSession, str]:
        """Resolves session and real name using a qualified name"""
        if qualified not in self.tool_index:
            raise RuntimeError(f"Tool '{qualified}' not in index")
        server_name, tool_name, _, _ = self.tool_index[qualified]
        return self.sessions[server_name], tool_name

    #Query
    async def process_query(self, query: str) -> str:
        """Sends a query to claude"""
        # Prepare all tools
        available_tools = []
        for qualified, (_srv, _tool, schema, desc) in self.tool_index.items():
            available_tools.append({
                "name": qualified,
                "description": desc or f"Tool {qualified}",
                "input_schema": schema
            })

        self.messages.append({"role": "user", "content": query})
        final_text_chunks: List[str] = []

        while True:
            resp = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=self.messages,
                tools=available_tools
            )

            # Accumulates texts and process tools in order
            tool_uses = []
            for block in resp.content:
                if block.type == "text":
                    final_text_chunks.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            if not tool_uses:
                # If we don't have more tool calls, we finsihN
                break

            # Execute each tool in order and return tool_result to claude
            assistant_msg_content = []
            for block in resp.content:
                # Add assistant content to history
                assistant_msg_content.append(block)

            self.messages.append({
                "role": "assistant",
                "content": assistant_msg_content
            })

            # Execute tool_uses and return reslts
            tool_results_content = []
            for tu in tool_uses:
                qualified_name = tu.name
                args = tu.input or {}

                session, real_tool = self._route_tool(qualified_name)
                result = await session.call_tool(real_tool, arguments=args)

                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": result.content,
                })

                final_text_chunks.append(f"[{qualified_name} executed with {args}]")

            self.messages.append({
                "role": "user",
                "content": tool_results_content
            })


        return "\n".join(final_text_chunks)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Write a query or quit to exit!")
        while True:
            try:
                q = input("\nQuery: ").strip()
                if q.lower() == "quit":
                    break
                print("\n" + (await self.process_query(q)))
            except Exception as e:
                print(f"\nError: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    import sys
    if len(sys.argv) < 2:
        print("Use: python client.py servers.json")
        raise SystemExit(2)

    client = Client()
    try:
        await client.connect_from_json(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
