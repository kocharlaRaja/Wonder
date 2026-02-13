from jira import JIRA
from jira.exceptions import JIRAError

# Jira credentials and server

# Connect to Jira
options = {'server': JIRA_SERVER, 'verify': False}
try:
    jira = JIRA(options=options, basic_auth=(EMAIL, API_TOKEN))
    user = jira.current_user()
    print(f"Credentials are valid. Logged in as: {user}")
except JIRAError as e:
    print(f"Failed to authenticate: {e.text}")
    exit(1)

PROJECT_KEY = "KAN"  # Replace with your project key

project = jira.project(PROJECT_KEY)
print(f"Project: {project.key} - {project.name}")
print(f"Description: {project.description}")
print(f"Lead: {project.lead.displayName}")
print(f"Project Type: {project.projectTypeKey}")
print(f"URL: {project.self}")

# Print components
components = jira.project_components(PROJECT_KEY)
print("\nComponents:")
for comp in components:
    print(f"  - {comp.name}: {comp.description}")

# Print versions
versions = jira.project_versions(PROJECT_KEY)
print("\nVersions:")
for ver in versions:
    print(f"  - {ver.name} (Released: {ver.released})")

# Print issues (as before)
print("\nIssues:")
issues = jira.search_issues(f"project = {PROJECT_KEY} ORDER BY created DESC", maxResults=50)
for issue in issues:
    print(f"  - Key: {issue.key}, Summary: {issue.fields.summary}, Status: {issue.fields.status.name}")
