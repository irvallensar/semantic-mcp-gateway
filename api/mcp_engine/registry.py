"""
MCP Tool Registry: Contains 30 enterprise MCP tool definitions.
"""
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MCPTool(BaseModel):
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]


# 30 Production MCP Tool Definitions
ALL_MCP_TOOLS: List[MCPTool] = [
    # --- Category: Database & SQL ---
    MCPTool(
        name="sql_execute_query",
        description="Executes a read-only SQL query against the primary PostgreSQL database and returns records.",
        category="Database",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The SELECT query to execute"}},
            "required": ["query"],
        },
    ),
    MCPTool(
        name="sql_inspect_schema",
        description="Inspects table columns, data types, indexes, and foreign keys for a given SQL database table.",
        category="Database",
        parameters={
            "type": "object",
            "properties": {"table_name": {"type": "string", "description": "Name of the table"}},
            "required": ["table_name"],
        },
    ),
    MCPTool(
        name="redis_cache_get",
        description="Retrieves a cached JSON string or session state by key from Redis.",
        category="Database",
        parameters={
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
    ),
    MCPTool(
        name="redis_cache_set",
        description="Stores a key-value pair in Redis with an optional time-to-live (TTL) in seconds.",
        category="Database",
        parameters={
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "value": {"type": "string"},
                "ttl_seconds": {"type": "integer"},
            },
            "required": ["key", "value"],
        },
    ),

    # --- Category: Git & Version Control ---
    MCPTool(
        name="github_create_pull_request",
        description="Creates a new pull request on GitHub with branch name, title, and Markdown description.",
        category="Git",
        parameters={
            "type": "object",
            "properties": {
                "repo": {"type": "string"},
                "branch": {"type": "string"},
                "title": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["repo", "branch", "title"],
        },
    ),
    MCPTool(
        name="github_fetch_commit_diff",
        description="Fetches the unified git diff between two commit hashes or branches in a repository.",
        category="Git",
        parameters={
            "type": "object",
            "properties": {
                "repo": {"type": "string"},
                "base_ref": {"type": "string"},
                "head_ref": {"type": "string"},
            },
            "required": ["repo", "base_ref", "head_ref"],
        },
    ),
    MCPTool(
        name="github_list_failing_checks",
        description="Lists all failing GitHub Actions CI/CD jobs and step logs for the latest commit on a branch.",
        category="Git",
        parameters={
            "type": "object",
            "properties": {
                "repo": {"type": "string"},
                "commit_sha": {"type": "string"},
            },
            "required": ["repo", "commit_sha"],
        },
    ),

    # --- Category: Cloud, Containers & DevOps ---
    MCPTool(
        name="docker_inspect_container",
        description="Inspects container runtime status, environment variables, healthchecks, and resource limits.",
        category="DevOps",
        parameters={
            "type": "object",
            "properties": {"container_id": {"type": "string"}},
            "required": ["container_id"],
        },
    ),
    MCPTool(
        name="docker_fetch_logs",
        description="Fetches recent stdout/stderr log output from a running or exited Docker container.",
        category="DevOps",
        parameters={
            "type": "object",
            "properties": {
                "container_id": {"type": "string"},
                "tail_lines": {"type": "integer", "default": 100},
            },
            "required": ["container_id"],
        },
    ),
    MCPTool(
        name="aws_s3_upload_file",
        description="Uploads a local artifact or log archive to an AWS S3 bucket with specified ACL.",
        category="DevOps",
        parameters={
            "type": "object",
            "properties": {
                "bucket": {"type": "string"},
                "key": {"type": "string"},
                "file_path": {"type": "string"},
            },
            "required": ["bucket", "key", "file_path"],
        },
    ),
    MCPTool(
        name="k8s_get_pod_status",
        description="Retrieves the deployment status, crash loop indicators, and restarts of a Kubernetes pod.",
        category="DevOps",
        parameters={
            "type": "object",
            "properties": {
                "namespace": {"type": "string"},
                "pod_name": {"type": "string"},
            },
            "required": ["namespace", "pod_name"],
        },
    ),

    # --- Category: Filesystem & Local Workspace ---
    MCPTool(
        name="fs_read_file_content",
        description="Reads the text content of a local file in the sandboxed project workspace.",
        category="Filesystem",
        parameters={
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"],
        },
    ),
    MCPTool(
        name="fs_write_file_patch",
        description="Writes a targeted string replacement or patch to a source code file.",
        category="Filesystem",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["file_path", "content"],
        },
    ),
    MCPTool(
        name="fs_find_files_by_regex",
        description="Searches for files matching a regex or glob pattern across the directory tree.",
        category="Filesystem",
        parameters={
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
        },
    ),

    # --- Category: NLP & Academic Research ---
    MCPTool(
        name="arxiv_search_papers",
        description="Searches arXiv for academic preprints by title, abstract keywords, author, or category.",
        category="Research",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    ),
    MCPTool(
        name="arxiv_download_latex_source",
        description="Downloads and unzips the raw LaTeX source bundle for an arXiv paper ID.",
        category="Research",
        parameters={
            "type": "object",
            "properties": {"paper_id": {"type": "string"}},
            "required": ["paper_id"],
        },
    ),
    MCPTool(
        name="huggingface_search_models",
        description="Queries the Hugging Face Hub for open-weights model cards by task and architecture.",
        category="Research",
        parameters={
            "type": "object",
            "properties": {
                "pipeline_tag": {"type": "string"},
                "search_term": {"type": "string"},
            },
            "required": ["pipeline_tag"],
        },
    ),

    # --- Category: Observability & Telemetry ---
    MCPTool(
        name="datadog_query_metrics",
        description="Queries Datadog for P95 latency, error rates, and CPU utilization over a given time window.",
        category="Observability",
        parameters={
            "type": "object",
            "properties": {
                "metric_name": {"type": "string"},
                "timeframe_minutes": {"type": "integer"},
            },
            "required": ["metric_name"],
        },
    ),
    MCPTool(
        name="sentry_fetch_issue_stacktrace",
        description="Fetches the full Python or JavaScript stacktrace and event metadata for a Sentry issue ID.",
        category="Observability",
        parameters={
            "type": "object",
            "properties": {"issue_id": {"type": "string"}},
            "required": ["issue_id"],
        },
    ),

    # --- Category: Enterprise Communication ---
    MCPTool(
        name="slack_post_channel_alert",
        description="Sends a formatted Markdown alert or incident notification to a specified Slack channel.",
        category="Communication",
        parameters={
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["channel", "message"],
        },
    ),
    MCPTool(
        name="jira_create_incident_ticket",
        description="Creates an urgent incident bug ticket in Jira with severity, component, and reproduction steps.",
        category="Communication",
        parameters={
            "type": "object",
            "properties": {
                "project_key": {"type": "string"},
                "summary": {"type": "string"},
                "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
            },
            "required": ["project_key", "summary", "priority"],
        },
    ),

    # --- Additional Enterprise Mock Tools (Creating Realistic Breadth) ---
    MCPTool(
        name="stripe_get_failed_payments",
        description="Fetches recent failed customer invoices and decline codes from Stripe.",
        category="Billing",
        parameters={"type": "object", "properties": {"customer_id": {"type": "string"}}},
    ),
    MCPTool(
        name="pagerduty_trigger_incident",
        description="Pages the on-call engineer for a critical production outage.",
        category="Observability",
        parameters={"type": "object", "properties": {"service_id": {"type": "string"}}, "required": ["service_id"]},
    ),
    MCPTool(
        name="confluence_search_kb",
        description="Searches Confluence internal engineering documentation and runbooks.",
        category="Knowledge",
        parameters={"type": "object", "properties": {"search_text": {"type": "string"}}, "required": ["search_text"]},
    ),
    MCPTool(
        name="cloudflare_purge_cache",
        description="Purges edge CDN cache by URL or zone ID.",
        category="DevOps",
        parameters={"type": "object", "properties": {"zone_id": {"type": "string"}}, "required": ["zone_id"]},
    ),
    MCPTool(
        name="linear_create_task",
        description="Creates an engineering sprint task in Linear with assignee and cycle.",
        category="Communication",
        parameters={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]},
    ),
    MCPTool(
        name="notion_append_meeting_notes",
        description="Appends bullet points to an existing Notion meeting document.",
        category="Knowledge",
        parameters={"type": "object", "properties": {"page_id": {"type": "string"}, "notes": {"type": "string"}}},
    ),
    MCPTool(
        name="sendgrid_send_transactional_email",
        description="Sends a template-based transactional email to a customer.",
        category="Communication",
        parameters={"type": "object", "properties": {"to_email": {"type": "string"}, "subject": {"type": "string"}}},
    ),
    MCPTool(
        name="launchdarkly_toggle_feature_flag",
        description="Toggles a rollout feature flag state in LaunchDarkly.",
        category="DevOps",
        parameters={"type": "object", "properties": {"flag_key": {"type": "string"}, "state": {"type": "boolean"}}},
    ),
    MCPTool(
        name="vault_read_secret",
        description="Retrieves a rotated database secret or token from HashiCorp Vault.",
        category="Security",
        parameters={"type": "object", "properties": {"secret_path": {"type": "string"}}, "required": ["secret_path"]},
    ),
]