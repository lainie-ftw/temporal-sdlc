import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from temporalio import activity

from data.data_types import DeploymentEnvironment, FeatureDetails, GitHubData

from github import Github

load_dotenv(override=True)

# Initialize GitHub client      
github_instance = Github(os.environ.get('GITHUB_TOKEN'))
repo = github_instance.get_repo(os.environ.get('GITHUB_REPO'))

class Activities:
    def __init__(self):
        pass
    
    # Define the activity interfaces
    @activity.defn
    async def create_jira_issue(self, feature_details: FeatureDetails) -> FeatureDetails:

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
            json=payload,  
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
        return feature_details

    @activity.defn
    async def create_github_branch(self, github_data: GitHubData) -> GitHubData:

        base_branch = repo.get_branch('main')  # Assuming the base branch is 'main'
        repo.create_git_ref(ref=f'refs/heads/{github_data.branch_name}', sha=base_branch.commit.sha)
        github_data.repo_link = f"{os.environ.get('GITHUB_REPO')}/{github_data.branch_name}"
        print(f'Created GitHub branch {github_data.branch_name}')

        return github_data

    @activity.defn
    async def create_github_pr(self, feature_details: FeatureDetails) -> FeatureDetails:
        pr = repo.create_pull(
            title=f'Feature: {feature_details.description}',
            body=f'Pull request for feature {feature_details.jira_id}: {feature_details.description}',
            head=feature_details.github_data.branch_name,
            base='main' 
        )
        feature_details.github_data.pr_link = pr.html_url
        print(f'Created GitHub pull request for feature: {feature_details.jira_id} with link: {feature_details.github_data.pr_link}')
        github_instance.close()  # Close the GitHub instance to release resources
        return feature_details
    
    @activity.defn
    async def deploy_to_environment(self, deployment_environment: DeploymentEnvironment) -> DeploymentEnvironment:
        print(f'Beginning deploy to {deployment_environment.name} environment.')
        await self.run_ssh_commands(deployment_environment.name)
        deployment_environment.status = 'deployed'
        
        print(f'Deployed to {deployment_environment.name} environment.')

        return deployment_environment
    

    async def run_ssh_commands(self, env_name: str) -> None:
        import subprocess
        ssh_pw = os.environ.get('SSH_PW')
        ssh_user = os.environ.get('SSH_USER')
        ssh_ip = os.environ.get('SSH_IP')
        try:
            # Construct the SSH command to execute multiple commands on the remote server
            ssh_command = (
                f"sshpass -p '{ssh_pw}' ssh {ssh_user}@{ssh_ip} "
                f"\"cd fancy-app && git pull && "
                f"export HISTIGNORE='*sudo -S*' && "
                f"echo '{ssh_pw}' | sudo -S ./deploy.sh '{env_name}'\""
            )

            # Run the SSH command
            print(f"Executing ssh command.")
            result = subprocess.run(
                ssh_command,
                timeout=15,
                shell=True,  # Required for command chaining with &&
                check=True,  # Raises an error if the command fails
                capture_output=True,  # Capture stdout and stderr
                text=True  # Return output as strings instead of bytes
            )
            
            if result.stderr:
                print("Errors (if any):")
                print(result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            print(f"Error output: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error: {e}")
