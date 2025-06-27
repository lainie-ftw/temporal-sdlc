from datetime import timedelta
from temporalio import workflow, activity

with workflow.unsafe.imports_passed_through():
    from data.data_types import FeatureDetails, DeploymentEnvironment, GitHubData

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
            branch="",
            link="",
            pr_link="",
            pr_approver=""
        )  # Store GitHub repository information

    @workflow.run
    async def run(self, feature_details: str) -> None:
        self.feature_details.description = feature_details
        workflow.logger.info(f"Starting SDLC workflow for feature: {feature_details}")

        await workflow.execute_activity(create_jira_issue, feature_details, start_to_close_timeout=timedelta(seconds=30))
        await workflow.execute_activity(create_github_branch, feature_details, start_to_close_timeout=timedelta(seconds=30))

        # Wait for a signal to create the PR
        await workflow.execute_activity(create_github_pr, feature_details, start_to_close_timeout=timedelta(seconds=30))

        # Wait for approval to deploy to Test
        await workflow.execute_activity(deploy_to_test_env, feature_details, start_to_close_timeout=timedelta(seconds=30))
        # Wait for approval to deploy to Preprod
        await workflow.execute_activity(deploy_to_preprod_env, feature_details, start_to_close_timeout=timedelta(seconds=30))
        # Wait for approval to deploy to Prod
        await workflow.execute_activity(deploy_to_prod_env, feature_details, start_to_close_timeout=timedelta(seconds=30))

    @workflow.signal
    async def create_PR(self, approver: str):
        """Signal to receive a prompt from the user."""
        workflow.logger.warning(f"Got signal to create the PR, approver is {approver}")
        self.github_data.pr_approver = approver

    @workflow.signal
    async def deploy(self, environment: str, approver: str):
        """Signal to deploy to a specific environment."""
        workflow.logger.warning(f"Got signal to deploy to {environment}, approver is {approver}")
        for env in self.deployment_environments:
            if env.name == environment:
                env.status = "approved"
                break
        else:
            workflow.logger.error(f"Environment {environment} not found in deployment environments.")

# Define the activity interfaces
@activity.defn
async def create_jira_issue(feature_details: str) -> None:
#    from jira import JIRA
#    import os
#
#    jira_options = {'server': os.getenv('JIRA_SERVER')}
#    jira = JIRA(options=jira_options, basic_auth=(os.getenv('JIRA_USERNAME'), os.getenv('JIRA_API_TOKEN')))
#
#    issue_dict = {
#        'project': {'key': 'YOUR_PROJECT_KEY'},
#        'summary': f'Feature Deployment: {feature_details}',
#        'description': f'Deployment of feature: {feature_details}',
#        'issuetype': {'name': 'Task'},
#    }
#
#    issue = jira.create_issue(fields=issue_dict)
    #print(f'Created Jira issue {issue.key}')
    print(f'Created Jira issue for feature: {feature_details}')

@activity.defn
async def create_github_branch(feature_details: str) -> None:
    #from github import Github
    #import os

    #g = Github(os.getenv('GITHUB_TOKEN'))
    #repo = g.get_repo(os.getenv('GITHUB_REPO'))
    #branch_name = f'feature/{feature_details.replace(" ", "-").lower()}'
    #base_branch = repo.get_branch('main')  # Assuming the base branch is 'main'
    #repo.create_git_ref(ref=f'refs/heads/{branch_name}', sha=base_branch.commit.sha)
    #print(f'Created GitHub branch {branch_name}')
    print(f'Created GitHub branch for feature: {feature_details}')

@activity.defn
async def create_github_pr(feature_details: str) -> None:
    #from github import Github
    #import os

    #g = Github(os.getenv('GITHUB_TOKEN'))
    #repo = g.get_repo(os.getenv('GITHUB_REPO'))
    #branch_name = f'feature/{feature_details.replace(" ", "-").lower()}'
    #pr = repo.create_pull(
    #    title=f'Feature: {feature_details}',
    #    body=f'Pull request for feature: {feature_details}',
    #    head=branch_name,
    #    base='main'  # Assuming the base branch is 'main'
    #)
    #print(f'Created GitHub pull request #{pr.number}')
    print(f'Created GitHub pull request for feature: {feature_details}')

async def deploy_to_environment(feature_details: str, environment_name: str) -> None:
    #import subprocess

    # Construct the command based on the environment name
    #command = f'deploy_to_{environment_name}.sh {feature_details}'
    #result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    #print(f'Deployed to {environment_name} environment: {result.stdout}')
    print(f'Deployed to {environment_name} environment for feature: {feature_details}')

@activity.defn
async def deploy_to_test_env(feature_details: str) -> None:
    await deploy_to_environment(feature_details, 'test')

@activity.defn
async def deploy_to_preprod_env(feature_details: str) -> None:
    await deploy_to_environment(feature_details, 'preprod')

@activity.defn
async def deploy_to_prod_env(feature_details: str) -> None:
    await deploy_to_environment(feature_details, 'prod')

