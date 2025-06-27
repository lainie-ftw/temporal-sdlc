from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from data.data_types import FeatureDetails, DeploymentEnvironment, GitHubData
    from activities.activities import Activities


# Define the workflow interface
# This workflow demonstrates a simple SDLC process using Temporal workflows and activities.
@workflow.defn
class SDLCWorkflow:

    def __init__(self):
        # Store feature details
        self.feature_details = FeatureDetails(
            jira_id="",
            jira_link="",
            feature_branch_name="",
            description=""
        )

        # Store deployment environment information
        self.deployment_environments = [
            DeploymentEnvironment(name="test", endpoint="http://test.example.com", deploy_script="deploy_to_test.sh", status="pending"),
            DeploymentEnvironment(name="preprod", endpoint="http://preprod.example.com", deploy_script="deploy_to_preprod.sh", status="pending"),
            DeploymentEnvironment(name="prod", endpoint="http://prod.example.com", deploy_script="deploy_to_prod.sh", status="pending"),
        ]

        self.github_data = GitHubData(
            repo_link="",
            pr_link="",
            pr_creator=""
        )  # Store GitHub repository information

    @workflow.run
    async def run(self, feature_details: str) -> None:
        self.feature_details.description = feature_details
        workflow.logger.info(f"Starting SDLC workflow for feature: {feature_details}")

        await workflow.execute_activity(Activities.create_jira_issue, self.feature_details, start_to_close_timeout=timedelta(seconds=30))
        await workflow.execute_activity(Activities.create_github_branch, self.github_data, start_to_close_timeout=timedelta(seconds=30))

        # Wait for a signal to create the PR
        await workflow.wait_condition(
            lambda: self.github_data.pr_creator != "",
            timeout=timedelta(days=5),
        )
        await workflow.execute_activity(Activities.create_github_pr, feature_details, start_to_close_timeout=timedelta(seconds=30))

        # Wait for approval to deploy to Test
        await workflow.wait_condition(
            lambda: any(env.status == "approved" for env in self.deployment_environments if env.name == "test"),
            timeout=timedelta(days=5),
        )
        await workflow.execute_activity(Activities.deploy_to_test_env, feature_details, start_to_close_timeout=timedelta(seconds=30))

        # Wait for approval to deploy to Preprod
        await workflow.wait_condition(
            lambda: any(env.status == "approved" for env in self.deployment_environments if env.name == "preprod"),
            timeout=timedelta(days=5),
        )
        await workflow.execute_activity(Activities.deploy_to_preprod_env, feature_details, start_to_close_timeout=timedelta(seconds=30))

        # Wait for approval to deploy to Prod
        await workflow.wait_condition(
            lambda: any(env.status == "approved" for env in self.deployment_environments if env.name == "prod"),
            timeout=timedelta(days=5),
        )
        await workflow.execute_activity(Activities.deploy_to_prod_env, feature_details, start_to_close_timeout=timedelta(seconds=30))

    @workflow.signal
    async def create_PR(self, approver: str):
        """Signal to receive a prompt from the user."""
        workflow.logger.warning(f"Got signal to create the PR, approver is {approver}")
        self.github_data.pr_creator = approver

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

    @workflow.query
    def get_deployment_environments(self) -> any:
        """Query handler to retrieve the list of prompts."""
        return self.deployment_environments