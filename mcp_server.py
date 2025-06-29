import uuid
from typing import Dict

from mcp.server.fastmcp import FastMCP
from temporalio.client import Client

from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from sdlc_workflow import SDLCWorkflow

mcp = FastMCP(name="sdlc_workflow")

@mcp.tool()
async def start(feature_description: str) -> Dict[str, str]:
    """Start the SDLC Workflow with a feature description."""
    client = await get_temporal_client()
    handle = await client.start_workflow(
        SDLCWorkflow.run,
        feature_description,
        id=f"sdlc-{uuid.uuid4()}",
        task_queue=TEMPORAL_TASK_QUEUE,
    )
    return {"workflow_id": handle.id, "run_id": handle.result_run_id}


@mcp.tool()
async def create_pr(jira_id: str) -> str:
    client = await get_temporal_client()
    #get workflow ID with custom search attribute JiraID
    jira_id_lower = jira_id.lower()
    async for workflow in client.list_workflows(query=f'JiraID="{jira_id_lower}"'):
        workflow_id = workflow.id
    
    handle = client.get_workflow_handle(workflow_id=workflow_id)
    await handle.signal("create_PR", "mcp_user")
    return "PR created."


@mcp.tool()
async def deploy(jira_id: str, env: str) -> str:
    """Signal rejection for the invoice workflow."""
    client = await get_temporal_client()
    jira_id_lower = jira_id.lower()
    async for workflow in client.list_workflows(query=f'JiraID="{jira_id_lower}"'):
        workflow_id = workflow.id
    handle = client.get_workflow_handle(workflow_id=workflow_id)
    await handle.signal("deploy_to_environment", env)
    return f"Deployed to {env}."


@mcp.tool()
async def status(jira_id: str) -> str:
    """Return current status of the workflow."""
    client = await get_temporal_client()

    jira_id_lower = jira_id.lower()
    async for workflow in client.list_workflows(query=f'JiraID="{jira_id_lower}"'):
        workflow_id = workflow.id
    
    handle = client.get_workflow_handle(workflow_id=workflow_id)

    desc = await handle.describe()
    feature_details = await handle.query(SDLCWorkflow.get_feature_details)

    return f"Feature {feature_details.jira_id} is totally a thing. " \
           f"Workflow status: {desc.status.name}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
