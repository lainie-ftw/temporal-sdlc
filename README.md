# temporal-sdlc

# Deployment Notes
git pull (if dev)
docker compose build [env] --no-cache
docker compose up [env]

# TODO
- deploy fancy app to optiplex2
- connect deployment functionality
- add haproxy to optiplex2
-- add redirect for 3000 = prod, 3001 = dev, 3002 = preprod
-- add redirect for Temporal
- make this MCP'd
-- add to AI agent demo
-- add to Cline

# Setup
temporal operator search-attribute create --name JiraID --type Text --namespace sdlc --env lab

To start MCP:
{
  "mcpServers": {
    "sdlc_workflow": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "wsl.exe",
      "args": [
        "--cd",
        "/home/laine/workspaces/temporal-sdlc",
        "--",
        "poetry",
        "run",
        "python",
        "mcp_server.py"
      ]
    }
}

To run:
start mcp_server.py
start a worker
either trigger from Cline or run run_workflow.py