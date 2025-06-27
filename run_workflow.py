import asyncio
import uuid

from shared.config import TEMPORAL_TASK_QUEUE, get_temporal_client
from sdlc_workflow import SDLCWorkflow

async def main():
    # Create client connected to server at the given address
    client = await get_temporal_client()

    # Start the workflow with a description of the feature
    start_msg = "Henlo, am feature for FANCY APP O YEAH BOOM!"
    handle = await client.start_workflow(
        SDLCWorkflow.run,
        start_msg,
        id=f"sdlc-{uuid.uuid4()}",
        task_queue=TEMPORAL_TASK_QUEUE,
    )
    print(f"Workflow started with ID: {handle.id}")


if __name__ == "__main__":
    asyncio.run(main())