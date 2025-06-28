from temporalio import worker
from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from sdlc_workflow import SDLCWorkflow
from activities.activities import Activities

async def main():
    # Connect to the Temporal server
    client = await get_temporal_client()
    activity_list = Activities()

    # Create a worker that will run the workflow and activities
    w = worker.Worker(
        client,
        task_queue=TEMPORAL_TASK_QUEUE,
        workflows=[SDLCWorkflow],
        activities=[
            activity_list.create_jira_issue,
            activity_list.create_github_branch,
            activity_list.create_github_pr,
            activity_list.deploy_to_environment,
        ],
    )

    # Run the worker
    await w.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
