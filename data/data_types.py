from dataclasses import dataclass, field

@dataclass
class DeploymentEnvironment:
    name: str
    endpoint: str
    status: str 
    approver: str = ""

@dataclass
class GitHubData:
    repo_link: str
    branch_name: str
    pr_link: str
    pr_creator: str

@dataclass
class FeatureDetails:
    jira_id: str
    jira_link: str
    description: str
    github_data: GitHubData = field(default_factory=GitHubData)
