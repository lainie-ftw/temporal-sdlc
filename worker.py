from temporalio import worker
from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from sdlc_workflow import SDLCWorkflow, create_jira_issue, create_github_branch, create_github_pr, deploy_to_test_env, deploy_to_preprod_env, deploy_to_prod_env

async def main():
    # Connect to the Temporal server
    client = await get_temporal_client()

    # Create a worker that will run the workflow and activities
    w = worker.Worker(
        client,
        task_queue=TEMPORAL_TASK_QUEUE,
        workflows=[SDLCWorkflow],
        activities=[
            create_jira_issue,
            create_github_branch,
            create_github_pr,
            deploy_to_test_env,
            deploy_to_preprod_env,
            deploy_to_prod_env,
        ],
    )

    # Run the worker
    await w.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
