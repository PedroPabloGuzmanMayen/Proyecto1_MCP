import asyncio

from fastmcp import Client

async def test_server():
    # Test the MCP server using streamable-http transport.
    # Use "/sse" endpoint if using sse transport.
    async with Client("http://localhost:8080/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        name = 'pikachu'
        for tool in tools:
            print(f">>> Tool found: {tool.name}")
        # Call add tool
        print(">>>  Calling tool for pikachu info")
        result = await client.call_tool("get_pokemon_info_tool", {"name": "pikachu"})
        print(f"<<<  Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_server())