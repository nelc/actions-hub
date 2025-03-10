# NELC Actions Hub

A centralized spot for all your reusable GitHub Actions workflows and custom actions in the NELC organization. We aim to standardize CI/CD processes across multiple projects.

## Available Actions & Workflows

| Name                         | Description                                                          | File Path                                                       |
|------------------------------|----------------------------------------------------------------------|-----------------------------------------------------------------|
| **Strain Repo Dispatch**     | Kicks off strain updates whenever certain repository events happen.  | [strain-repo-dispatch/action.yml](strain-repo-dispatch/action.yml) |

## Using Actions from Organization Repositories

### Reference Actions Using Full Path

If you’d like to use these actions in your own workflows within the same organization:

```yaml
- name: Run an Action from Actions Hub
  uses: nelc/actions-hub/<action-folder>/action.yml@v1.0.0
```

### Referencing Specific Versions

You can point to a reusable action or workflow by tag, branch, or commit SHA:

```yaml
# Using a version tag
uses: nelc/actions-hub/<action-folder>/action.yml@v1.0.0

# Using a commit SHA
uses: nelc/actions-hub/<action-folder>/action.yml@7a6bcc1234f
```

### Authentication Considerations

If you’re working with actions in a private repo, make sure your workflow has the right permissions. For example:

```yaml
jobs:
  my-job:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Use Reusable Workflow
        uses: nelc-actions-hub/<action-folder>/action.yml@main
```

## Recommendations for Calling Reusable Workflows

- **Use Descriptive Tags or SHAs:**  
  Stick to a specific release tag (e.g., `@v1.0.0`) or commit SHA so your workflow won’t break if things change upstream.

- **Manage Secrets Securely:**  
  Store credentials (like AWS keys, PATs, etc.) in your repo or org secrets. Then reference them using `secrets:` in your workflow.

- **Check Permissions:**  
  If your actions or workflows live in private repositories, confirm that the calling repo has proper read access or uses a valid token.