import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from temporalio import activity

from data.data_types import FeatureDetails, GitHubData

load_dotenv(override=True)

class Activities:
    def __init__(self):
        pass
    
    # Define the activity interfaces
    @activity.defn
    async def create_jira_issue(self, feature_details: FeatureDetails) -> None:

        jira_url = os.environ.get('JIRA_SERVER')
        jira_username = os.environ.get('JIRA_USERNAME')
        jira_api_token = os.environ.get('JIRA_API_TOKEN')
        url = f"{jira_url}/rest/api/3/issue"

        auth = HTTPBasicAuth(jira_username, jira_api_token)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        summary = f"Created from Temporal: {feature_details.description}"
        payload = {
            "fields": {
                "project": {
                    "key": os.environ.get('JIRA_PROJECT_KEY')
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                        "type": "paragraph",
                        "content": [
                            {
                            "type": "text",
                            "text": feature_details.description
                            }
                        ]
                        }
                    ]
                    },
                "issuetype": {
                    "name": "Epic"
                },
                "summary": feature_details.description,
            }
        }
        #            "duedate": "2019-05-11",

        response = requests.post(
            url,
            json=payload,  # Use json instead of data to ensure payload is sent as JSON
            headers=headers,
            auth=auth,
            verify=False
        )

        if response.status_code == 201:
            response_json = response.json()
            feature_details.jira_id = response_json.get("key", "")
            feature_details.jira_link = f"{jira_url}/browse/{feature_details.jira_id}"
            print(f'Created Jira issue {feature_details.jira_id} for feature: {feature_details.description}')
        else:
            print(f'Failed to create Jira issue. Status code: {response.status_code}, Response: {response.text}')

    @activity.defn
    async def create_github_branch(self, github_data: GitHubData) -> None:
        #from github import Github
        #import os

        #g = Github(os.getenv('GITHUB_TOKEN'))
        #repo = g.get_repo(os.getenv('GITHUB_REPO'))
        #branch_name = f'feature/{feature_details.replace(" ", "-").lower()}'
        #base_branch = repo.get_branch('main')  # Assuming the base branch is 'main'
        #repo.create_git_ref(ref=f'refs/heads/{branch_name}', sha=base_branch.commit.sha)
        #print(f'Created GitHub branch {branch_name}')
        print(f'Created GitHub branch for feature: {github_data.repo_link}')

    @activity.defn
    async def create_github_pr(self, feature_details: str) -> None:
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

    async def deploy_to_environment(self, feature_details: str, environment_name: str) -> None:
        #import subprocess

        # Construct the command based on the environment name
        #command = f'deploy_to_{environment_name}.sh {feature_details}'
        #result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        #print(f'Deployed to {environment_name} environment: {result.stdout}')
        print(f'Deployed to {environment_name} environment for feature: {feature_details}')

    @activity.defn
    async def deploy_to_test_env(self, feature_details: str) -> None:
        #await deploy_to_environment(self, feature_details, 'test')
         print(f'Deployed to test environment for feature: {feature_details}')

    @activity.defn
    async def deploy_to_preprod_env(self, feature_details: str) -> None:
        #await deploy_to_environment(self, feature_details, 'preprod')
        print(f'Deployed to preprod environment for feature: {feature_details}')

    @activity.defn
    async def deploy_to_prod_env(self, feature_details: str) -> None:
        #await deploy_to_environment(self, feature_details, 'prod')
         print(f'Deployed to prod environment for feature: {feature_details}')
