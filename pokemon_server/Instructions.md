# MCP Remote server SetUp and usage Instructions

## Prerequisites

1. **Python 3.10 or higher** (as specified in `.pyproject.toml`)
2. **Google Cloud project** (required for deploy)

## installation

### 1. Install Python Dependencies

Using uv (recommended):
```bash
uv install
```

Or using pip:
```bash
pip install aiohttp fastmcp
```

### 2. Configure Google Cloud run

First login into Google Cloud using your credentials and set your project

```bash
gcloud auth login
export PROJECT_ID=<your-project-id>
gcloud config set project $PROJECT_ID
```

### 4. Run locally

If you want to run this project locally, you just have to add this to the `mcp_config.json` of this MCP client:

```bash
{
    "name": "pokemon",
    "type": "stdio",
    "command": "python",
    "args": ["route_to_file/Proyecto_MCP/server.py"]
}
```

If you are not using this client, don´t write the "type" property

### 3. Deploy to the cloud

To deploy this project on the cloud, follow this steps.

1. Run this command on your terminal: 

```bash
gcloud run deploy mcp-server --no-allow-unauthenticated --region=us-central1 --source .
```
This will upload the project to Cloud Build and service will be available in an URL like this:

```bash
https://mcp-server-xxxxxxxx-uc.a.run.app
```
However, this wouldn't work in our case because we requiere authentication to use the service, if you don't want to use it, don't use the flag `--no-allow-unauthenticate` in the first command

2. Create a proxy server in your local machine

Run this on the terminal

```bash
gcloud run services proxy mcp-server --region=us-central1
```

This will create a proxy server in the port 8080 of yur local machine, all the traffic here will now be authenticated and forwarded to our remote MCP server.

Finally, add the project in the config.json like this

```bash
{
    "name": "pokemon",
    "type": "http",
    "url": "http://localhost:8080/mcp"
}
```