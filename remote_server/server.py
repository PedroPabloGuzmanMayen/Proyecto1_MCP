import requests
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("pokemon_mcp")

@mcp.tool()
def get_pokemon_info(name: str) -> dict:
    """
    Use Pokemon DB API to get important information of a Pokemon based on its name.
    """
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"No se encontró el Pokémon '{name}'"}

    data = response.json()

    pokemon_data = {
        "id": data["id"],
        "name": data["name"].capitalize(),
        "height": data["height"],
        "weight": data["weight"],
        "base_experience": data["base_experience"],
        "types": [t["type"]["name"] for t in data["types"]],
        "abilities": [a["ability"]["name"] for a in data["abilities"]],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
    }

    return pokemon_data


if __name__ == "__main__":
    mcp.run()
