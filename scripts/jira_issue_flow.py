import argparse
import os
from functools import lru_cache
from typing import Optional

from jira import JIRA
from jira.resources import Issue


@lru_cache(maxsize=1)
def get_jira_client() -> JIRA:
    """
    Returns a cached Jira client instance authenticated with the environment variables.

    Returns:
        JiraClient: An authenticated JIRA client instance.

    Raises:
        KeyError: If required environment variables are missing.
    """
    email = os.environ["MIGRATION_BACKLOG_JIRA_EMAIL"]
    token = os.environ["MIGRATION_BACKLOG_JIRA_TOKEN"]
    url = os.environ["MIGRATION_BACKLOG_JIRA_URL"]

    return JIRA(server=url, basic_auth=(email, token))


def get_jira_issue_by_jql(jql: str, summary: str) -> Optional[Issue]:
    """
    Searches for a Jira issue using a JQL query with an exact summary match.

    Args:
        jql (str): The JQL query string.
        summary (str): The exact summary of the issue to find.

    Returns:
        Optional[Issue]: The matching Jira issue, or None if not found.

    Raises:
        KeyError: If required environment variables are missing.
    """
    issues = get_jira_client().search_issues(jql, maxResults=10)
    for issue in issues:
        if issue.fields.summary == summary:
            return issue

    return None


def create_jira_issue(summary: str, issue_type: str, parent_key: str, description: str = "") -> Issue:
    """
    Creates a Jira issue (Story or Sub-task) in the configured project.

    Args:
        summary (str): The summary of the new issue.
        issue_type (str): The type of issue to create (e.g., "Story", "Sub-task").
        parent_key (str): The key of the Epic (for Story) or Story (for Sub-task).
        description (str): The description of the issue.

    Returns:
        Issue: The newly created Jira issue.

    Raises:
        KeyError: If required environment variables are missing.
    """
    project = os.environ["MIGRATION_BACKLOG_JIRA_PROJECT"]
    epic_link_field = os.environ["MIGRATION_BACKLOG_JIRA_EPIC_LINK_FIELD"]
    fields = {
        "project": {"key": project},
        "summary": summary,
        "issuetype": {"name": issue_type},
        "description": description,
    }

    if issue_type == "Story":
        fields[epic_link_field] = parent_key
    elif issue_type == "Sub-task":
        fields["parent"] = {"key": parent_key}

    return get_jira_client().create_issue(fields=fields)


def get_or_create_jira_issue(summary: str, jql: str, issue_type: str, parent_key, description: str = "") -> Issue:
    """
    Retrieves a Jira issue using a JQL query with an exact summary match, or creates it if not found.

    Args:
        summary (str): The summary of the issue.
        jql (str): The JQL query to search for the issue.
        issue_type (str): The type of issue to create if not found.
        parent_key (Optional[str]): The parent key (Epic or Story) if the issue needs to be linked.
        description (str): The description of the issue.

    Returns:
        Issue: The existing or newly created Jira issue.

    Raises:
        KeyError: If required environment variables are missing.
    """
    if issue := get_jira_issue_by_jql(jql=jql, summary=summary):
        return issue

    return create_jira_issue(summary=summary, issue_type=issue_type, parent_key=parent_key, description=description)


def get_or_create_story(summary: str, epic_key: str, description: str = "") -> Issue:
    """
    Retrieves or creates a Jira Story linked to the specified Epic.

    Args:
        summary (str): The summary of the Story.
        epic_key (str): The key of the Epic.
        description (str): The description of the Story.

    Returns:
        Issue: The existing or newly created Story issue.
    """
    project = os.environ["MIGRATION_BACKLOG_JIRA_PROJECT"]
    jql = f'project = {project} AND summary ~ "{summary}" AND issuetype = Story AND "Epic Link" = "{epic_key}"'

    return get_or_create_jira_issue(
        summary=summary,
        jql=jql,
        issue_type="Story",
        parent_key=epic_key,
        description=description,
    )


def get_or_create_subtask(summary: str, story_key: str, description: str = "") -> Issue:
    """
    Retrieves or creates a Jira Sub-task under the specified Story.

    Args:
        summary (str): The summary of the Sub-task.
        story_key (str): The key of the parent Story.
        description (str): The description of the Sub-task.

    Returns:
        Issue: The existing or newly created Sub-task issue.
    """
    project = os.environ["MIGRATION_BACKLOG_JIRA_PROJECT"]
    jql = f'project = {project} AND summary ~ "{summary}" AND issuetype = Sub-task AND parent = "{story_key}"'

    return get_or_create_jira_issue(
        summary=summary,
        jql=jql,
        issue_type="Sub-task",
        parent_key=story_key,
        description=description,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Jira Story and Sub-task if not present.")
    parser.add_argument("--story-summary", required=True, help="Summary for the story.")
    parser.add_argument("--story-description", default="", help="Description for the story.")
    parser.add_argument("--subtask-summary", required=True, help="Summary for the sub-task.")
    parser.add_argument("--subtask-description", default="", help="Description for the sub-task.")
    args = parser.parse_args()

    epic_key = os.environ["MIGRATION_BACKLOG_JIRA_EPIC_KEY"]

    story = get_or_create_story(
        summary=args.story_summary,
        epic_key=epic_key,
        description=args.story_description,
    )
    get_or_create_subtask(
        summary=args.subtask_summary,
        story_key=story.key,
        description=args.subtask_description,
    )
