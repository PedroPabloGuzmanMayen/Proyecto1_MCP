# MCP Client Setup and Usage Instructions

## Prerequisites

1. **Python 3.10 or higher** (as specified in `.python-version`)
2. **Node.js and npm** (required for MCP servers)
3. **Anthropic API Key** (for Claude access)

## Installation

### 1. Install Python Dependencies

Using uv (recommended):
```bash
uv install
```

Or using pip:
```bash
pip install anthropic asyncio python-dotenv mcp
```

### 2. Set up Environment Variables

Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Configure MCP Servers

The `mcp_config.json` file defines the MCP servers to connect to. You'll need to:

- **For GitHub server**: Replace `"TOKEN"` with your actual GitHub Personal Access Token
- **For filesystem server**: Update the path `/home/ppguz` to your desired directory
- **For Spotify server**: Ensure the path `../MCP_server/dist/main.js` points to your Spotify MCP server
- **For Pokemon server**: Make sure the HTTP server is running on `http://localhost:8080/mcp`

## Running the Program

### Basic Usage

```bash
python main.py mcp_config.json
```

### Interactive Session

Once started, you'll see:
```
MCP Client Started!
Write a query or quit to exit!

Query: 
```

You can then:
- Type your queries to interact with Claude and the connected MCP servers
- Type `quit` to exit the program

## Available MCP Servers

Based on your configuration, the following servers will be available:

1. **filesystem**: File system operations (read, write, list files)
2. **github**: GitHub repository operations  
3. **spotify**: Custom Spotify server functionality
4. **pokemon**: Pokemon-related operations via HTTP

## Tool Usage

Tools are automatically prefixed with their server name:
- `filesystem__read_file`
- `github__create_issue` 
- `spotify__search_track`
- `pokemon__get_pokemon`

Claude will automatically discover and use these tools based on your queries.

## Logs

The application logs activities to `mcp_client.log` for debugging purposes.

## Troubleshooting

1. **Missing dependencies**: Ensure all Python packages are installed
2. **API key issues**: Check your `.env` file and Anthropic API key
3. **MCP server connection failures**: Verify server configurations and paths in `mcp_config.json`
4. **Node.js servers**: Make sure npm packages are available globally or in the correct paths

## Example Queries

- "List files in my directory"
- "Create a GitHub issue for bug tracking"
- "Search for a song on Spotify"
- "Get information about Pikachu"

The client will route your requests to the appropriate MCP servers and return combined results through Claude.