# temporal-sdlc 

## Hello! And a Workflow Description 🤖
Welcome to temporal-sdlc! This is a demo of using Temporal to coordinate the Software Development Lifecycle. It shows a lifecycle for the [fancy-app application](https://github.com/lainie-ftw/fancy-app), which is a *very fancy* web page served with NodeJS and set up to deploy to three different "environments" (Docker containers running on different ports).

The workflow does the following:

1. Receive a description of a new feature. 📝
2. Create a new Jira item in the appropriate board. 📋
3. Create a new GitHub branch named feature/[Jira ID] in the fancy-app repository. 🌐
4. Wait for a signal - upon receiving, create a PR. 🔄
5. Wait for a signal for as many environments as are defined in the .env ENV_LIST, and then deploy to each environment. 🚀

## Now...make it MCP! 💡

Included in this repository is a mcp_server.py that will run locally with stdio. It exposes 1) starting the workflow, 2) sending the signal to create the PR, and 3) sending the signal to deploy as tools. This has been tested with Cline using the following configuration, which assumes the local environment is WSL, with the mcp_server.py file located in /home/laine/workspaces/temporal-sdlc.

```json
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
```

## Additional Notes 📝
The MCP server implementation relies on a [custom search attribute](https://docs.temporal.io/search-attribute#custom-search-attribute) called JiraID, which can be set up from the UI if you're using Temporal Cloud and via command line if you're running it locally. This command assumes you're using a namespace called sdlc:

```bash
temporal operator search-attribute create --name JiraID --type Text --namespace sdlc
```

If you don't want to use the MCP server, you can safely comment out the line in `sdlc_workflow.py` that adds the attribute to the workflow.

## LET'S RUN IT, WOO! 🎉

## Environment Variables ⚙️
You can see the environment variables used in `.env.example`. Make a copy of this file to `.env` and complete with your information.

This project uses Poetry as its package manager. 

```bash
# Create the venv in a folder called `.venv`
python3 -m venv .venv

# Activate the venv (for Bash / Linux / macOS)
source .venv/bin/activate

# Install the requirements
poetry install
```

2. **Start Temporal (locally or via Temporal Cloud)**

```bash
temporal server start-dev
```

3. **Run the worker**

```bash
poetry run python worker.py
```

4. **Trigger the workflow**
If you've set up the MCP server from an MCP host, you can trigger the workflow by asking it to create a new SDLC workflow with feature description "[description here]"

You can also start the workflow by running `run_workflow.py` and changing the `start_msg` 

```bash
poetry run python run_workflow.py
```
