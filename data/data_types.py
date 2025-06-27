from dataclasses import dataclass
from typing import Any, Dict, List

# Configuration for MCP servers
@dataclass
class FeatureDetails:
    jira_id: str
    jira_link: str
    feature_branch_name: str
    description: str

@dataclass
class DeploymentEnvironment:
    name: str
    endpoint: str
    deploy_script: str
    status: str 
    approver: str = ""

@dataclass
class GitHubData:
    repo_link: str
    pr_link: str
    pr_creator: str