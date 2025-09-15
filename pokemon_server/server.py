import asyncio
import logging
import os
import aiohttp
from fastmcp import FastMCP 

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("pokemon mcp")

async def get_pokemon_info(name: str) -> dict:
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"error": f"No se encontró el Pokémon '{name}'"}
            data = await response.json()

    return {
        "id": data["id"],
        "name": data["name"].capitalize(),
        "height": data["height"],
        "weight": data["weight"],
        "base_experience": data["base_experience"],
        "types": [t["type"]["name"] for t in data["types"]],
        "abilities": [a["ability"]["name"] for a in data["abilities"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
    }

@mcp.tool()
async def get_pokemon_info_tool(name: str) -> dict:
    return await get_pokemon_info(name)

if __name__ == "__main__":
    logger.info(f" MCP server started on port {8080}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="streamable-http", 
            host="0.0.0.0", 
            port=8080,
        )
    )