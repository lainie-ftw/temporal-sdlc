from datetime import timedelta
from typing import List
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from data.data_types import FeatureDetails, DeploymentEnvironment, GitHubData
    from activities.activities import Activities
    import os

ENV_LIST = os.environ.get('ENV_LIST', 'dev').split(',')

# This workflow demonstrates a simple SDLC process using Temporal workflows and activities.
@workflow.defn
class SDLCWorkflow:

    def __init__(self):
        # Store feature details
        self.feature_details = FeatureDetails(
            jira_id="",
            jira_link="",
            description="",
            github_data = GitHubData(
                repo_link="",
                branch_name="",
                pr_link="",
                pr_creator=""
            )
        )

        # Store deployment environment information
        self.deployment_environments = []

        self.status = "new"  # Human-friendly workflow status

    @workflow.run
    async def run(self, feature_details: str) -> None:
        self.feature_details.description = feature_details
        workflow.logger.info(f"Starting SDLC workflow for feature: {feature_details}")

        # Initialize deployment environments
        for env_name in ENV_LIST:
            env = DeploymentEnvironment(
                name=env_name.strip(),
                endpoint=f"http://fancy-app-{env_name.strip()}.lab",
                status="pending"
            )
            if env_name.strip() == "prod":
                env.endpoint = "http://fancy-app.lab"  # Production endpoint
            self.deployment_environments.append(env)

        self.feature_details = await workflow.execute_activity(Activities.create_jira_issue, self.feature_details, start_to_close_timeout=timedelta(seconds=30))

        workflow.upsert_search_attributes({"JiraIDFull": [f"{self.feature_details.jira_id.lower()}"]})
        self.status = f"Jira issue created: {self.feature_details.jira_id}"
        
        self.feature_details.github_data.branch_name = f"feature/{self.feature_details.jira_id.lower()}"
        self.feature_details.github_data = await workflow.execute_activity(Activities.create_github_branch, self.feature_details.github_data, start_to_close_timeout=timedelta(seconds=30))
        self.status = f"GitHub branch created: {self.feature_details.github_data.branch_name}"

        # Wait for a signal to create the PR
        await workflow.wait_condition(
            lambda: self.feature_details.github_data.pr_creator != "",
        )
        self.feature_details = await workflow.execute_activity(Activities.create_github_pr, self.feature_details, start_to_close_timeout=timedelta(seconds=30))
        self.status = f"GitHub PR created: {self.feature_details.github_data.pr_link}"

        #For each deployment environment, wait for approval and then deploy
        for env in self.deployment_environments:
            workflow.logger.info(f"Waiting for approval to deploy to {env.name} environment.")
            # Wait for approval to deploy to the environment
            await workflow.wait_condition(
                lambda: env.status == "approved",
            )
            # Execute the deployment activity
            env = await workflow.execute_activity(Activities.deploy_to_environment, env, start_to_close_timeout=timedelta(seconds=300))
            self.status = f"Deployed to {env.name} environment"

        workflow.logger.info("SDLC workflow completed successfully.") 
        self.status = "Complete!"                         

    # ----- Signals -----
    @workflow.signal
    async def create_PR(self, approver: str):
        """Signal to receive a prompt from the user."""
        workflow.logger.warning(f"Got signal to create the PR, approver is {approver}")
        self.feature_details.github_data.pr_creator = approver

    @workflow.signal
    async def deploy(self, environment: str):
        """Signal to deploy to a specific environment."""
        workflow.logger.warning(f"Got signal to deploy to {environment}.")
        for env in self.deployment_environments:
            if env.name == environment:
                env.status = "approved"
               # env.approver = approver
                break
        else:
            workflow.logger.error(f"Environment {environment} not found in deployment environments.")

    # ----- Queries -----
    @workflow.query
    def get_deployment_environments(self) -> List[DeploymentEnvironment]:
        """Query handler to retrieve deployment environment information."""
        return self.deployment_environments
    
    @workflow.query
    def get_feature_details(self) -> FeatureDetails:
        """Query handler to retrieve feature details."""
        return self.feature_details
    
    @workflow.query
    def get_status(self) -> str:
        """Query handler to retrieve the current status of the workflow."""
        return self.status
