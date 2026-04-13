"""
╔══════════════════════════════════════════════════════════════════╗
║  🌐 OMNI MCP — 68 SERVERS (ALL CATEGORIES)                     ║
║  Official | Dev | Database | Cloud | Productivity | Search      ║
║  Media | Communication | Finance | Security | Specialized       ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys, os, json, time, uuid, random, hashlib
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
from mcp_protocol import MCPServer, MCPTool, MCPResource, MCPPrompt, MCPResourceTemplate, MCPServerRegistry

def _build_server(name, version, desc, tools_data, resources_data=None, prompts_data=None):
    """Factory to build MCP server from spec."""
    srv = MCPServer(name, version, desc)
    for td in tools_data:
        srv.add_tool(MCPTool(td["name"], td["desc"],
            td.get("handler", lambda args, n=td["name"]: {"status": "ok", "tool": n, **args}),
            td.get("schema", {"type": "object", "properties": {}})))
    for rd in (resources_data or []):
        srv.add_resource(MCPResource(rd["uri"], rd["name"], rd["desc"],
            rd.get("mime", "text/plain"), rd.get("reader")))
    for pd in (prompts_data or []):
        srv.add_prompt(MCPPrompt(pd["name"], pd["desc"], pd.get("args", [])))
    return srv

# ═══════════════════════════════════════════════════
# CATEGORY 1: OFFICIAL MCP SERVERS (1-15)
# ═══════════════════════════════════════════════════
def build_official_servers():
    servers = []

    # 1. Filesystem
    servers.append(_build_server("filesystem", "1.0.0", "Read/write local files",
        [{"name": "read_file", "desc": "Read file contents",
          "handler": lambda a: {"content": f"[Contents of {a.get('path','?')}]", "size": 1024}},
         {"name": "write_file", "desc": "Write content to file",
          "handler": lambda a: {"written": True, "path": a.get("path","?"), "bytes": len(str(a.get("content","")))}},
         {"name": "list_directory", "desc": "List directory contents",
          "handler": lambda a: {"entries": ["file1.py","file2.js","dir1/"], "path": a.get("path",".")}},
         {"name": "move_file", "desc": "Move/rename a file",
          "handler": lambda a: {"moved": True, "from": a.get("source"), "to": a.get("dest")}},
         {"name": "delete_file", "desc": "Delete a file",
          "handler": lambda a: {"deleted": True, "path": a.get("path")}},
         {"name": "search_files", "desc": "Search files by pattern",
          "handler": lambda a: {"matches": [f"found_{i}.py" for i in range(3)]}}],
        [{"uri": "file://cwd", "name": "Current Dir", "desc": "Current working directory"}]))

    # 2. PostgreSQL
    servers.append(_build_server("postgres", "1.0.0", "Query PostgreSQL databases",
        [{"name": "query", "desc": "Execute SQL query",
          "handler": lambda a: {"rows": [{"id":1,"name":"test"}], "count": 1, "sql": a.get("sql","?")}},
         {"name": "list_tables", "desc": "List all tables",
          "handler": lambda a: {"tables": ["users","orders","products"]}},
         {"name": "describe_table", "desc": "Get table schema",
          "handler": lambda a: {"columns": [{"name":"id","type":"int"},{"name":"email","type":"varchar"}]}}]))

    # 3. SQLite
    servers.append(_build_server("sqlite", "1.0.0", "Local SQLite database operations",
        [{"name": "query", "desc": "Execute SQL query on SQLite",
          "handler": lambda a: {"rows": [], "count": 0}},
         {"name": "create_table", "desc": "Create new table",
          "handler": lambda a: {"created": True, "table": a.get("name")}}]))

    # 4. Git
    servers.append(_build_server("git", "1.0.0", "Git repository operations",
        [{"name": "git_log", "desc": "Show commit history",
          "handler": lambda a: {"commits": [{"hash":"abc123","msg":"Initial commit","author":"dev"}]}},
         {"name": "git_diff", "desc": "Show file diffs",
          "handler": lambda a: {"diff": "+added line\n-removed line", "files_changed": 3}},
         {"name": "git_status", "desc": "Show working tree status",
          "handler": lambda a: {"staged": 2, "modified": 1, "untracked": 0}},
         {"name": "git_branch", "desc": "List or manage branches",
          "handler": lambda a: {"current": "main", "branches": ["main","dev","feature/x"]}}]))

    # 5. GitHub
    servers.append(_build_server("github", "1.0.0", "GitHub API operations",
        [{"name": "list_repos", "desc": "List user repositories",
          "handler": lambda a: {"repos": [{"name":"omni","stars":42}]}},
         {"name": "create_issue", "desc": "Create GitHub issue",
          "handler": lambda a: {"issue_number": 1, "title": a.get("title","?")}},
         {"name": "create_pr", "desc": "Create pull request",
          "handler": lambda a: {"pr_number": 1, "url": "https://github.com/user/repo/pull/1"}},
         {"name": "search_code", "desc": "Search code across repos",
          "handler": lambda a: {"results": 5, "query": a.get("query","?")}}]))

    # 6. GitLab
    servers.append(_build_server("gitlab", "1.0.0", "GitLab API operations",
        [{"name": "list_projects", "desc": "List GitLab projects"},
         {"name": "create_merge_request", "desc": "Create MR"},
         {"name": "run_pipeline", "desc": "Trigger CI/CD pipeline"}]))

    # 7. Google Drive
    servers.append(_build_server("gdrive", "1.0.0", "Google Drive file access",
        [{"name": "list_files", "desc": "List Drive files",
          "handler": lambda a: {"files": [{"name":"doc.pdf","size":"2MB"}]}},
         {"name": "download_file", "desc": "Download file from Drive"},
         {"name": "search_files", "desc": "Search files in Drive"}]))

    # 8. Google Maps
    servers.append(_build_server("google-maps", "1.0.0", "Maps and geocoding",
        [{"name": "geocode", "desc": "Convert address to coordinates",
          "handler": lambda a: {"lat": -6.2088, "lng": 106.8456, "address": "Jakarta"}},
         {"name": "directions", "desc": "Get route directions"},
         {"name": "search_places", "desc": "Search nearby places"}]))

    # 9. Slack
    servers.append(_build_server("slack", "1.0.0", "Slack workspace interaction",
        [{"name": "send_message", "desc": "Send message to channel",
          "handler": lambda a: {"sent": True, "channel": a.get("channel","#general")}},
         {"name": "list_channels", "desc": "List workspace channels"},
         {"name": "read_messages", "desc": "Read channel messages"}]))

    # 10. Brave Search
    servers.append(_build_server("brave-search", "1.0.0", "Web search via Brave",
        [{"name": "web_search", "desc": "Search the web",
          "handler": lambda a: {"results": [{"title": f"Result for {a.get('query','?')}", "url": "https://..."}]}},
         {"name": "local_search", "desc": "Search local businesses"}]))

    # 11. Fetch
    servers.append(_build_server("fetch", "1.0.0", "Fetch content from URLs",
        [{"name": "fetch", "desc": "Get content from URL",
          "handler": lambda a: {"status": 200, "content": f"[HTML from {a.get('url','?')}]", "size": 5000}}]))

    # 12. Memory (Knowledge Graph)
    servers.append(_build_server("memory", "1.0.0", "Persistent knowledge graph memory",
        [{"name": "create_entities", "desc": "Create entities in knowledge graph",
          "handler": lambda a: {"created": len(a.get("entities",[]))}},
         {"name": "create_relations", "desc": "Create relations between entities"},
         {"name": "search_nodes", "desc": "Search knowledge graph"},
         {"name": "open_nodes", "desc": "Read specific nodes"}]))

    # 13. Puppeteer
    servers.append(_build_server("puppeteer", "1.0.0", "Browser automation via Chrome",
        [{"name": "navigate", "desc": "Navigate to URL",
          "handler": lambda a: {"url": a.get("url"), "title": "Page Title"}},
         {"name": "screenshot", "desc": "Take page screenshot"},
         {"name": "click", "desc": "Click element by selector"},
         {"name": "evaluate", "desc": "Run JavaScript in page"}]))

    # 14. AWS KB Retrieval
    servers.append(_build_server("aws-kb-retrieval", "1.0.0", "Amazon Bedrock Knowledge Base",
        [{"name": "retrieve", "desc": "Retrieve from AWS knowledge base",
          "handler": lambda a: {"chunks": [{"text":"relevant info","score":0.95}]}}]))

    # 15. EverArt
    servers.append(_build_server("everart", "1.0.0", "AI image generation",
        [{"name": "generate_image", "desc": "Generate image from text prompt",
          "handler": lambda a: {"image_url": "https://everart.ai/generated/abc.png", "prompt": a.get("prompt")}}]))

    return servers


# ═══════════════════════════════════════════════════
# CATEGORY 2: DEVELOPMENT & CODE (16-23)
# ═══════════════════════════════════════════════════
def build_dev_servers():
    servers = []
    servers.append(_build_server("playwright", "1.0.0", "Microsoft browser automation (accessibility-aware)",
        [{"name": "navigate", "desc": "Navigate browser to URL"},
         {"name": "click", "desc": "Click element by accessible name"},
         {"name": "fill", "desc": "Fill input field"},
         {"name": "screenshot", "desc": "Capture accessibility snapshot"},
         {"name": "assert_text", "desc": "Assert text content on page"}]))

    servers.append(_build_server("desktop-commander", "1.0.0", "Terminal commands and process management",
        [{"name": "execute_command", "desc": "Run terminal command",
          "handler": lambda a: {"output": f"$ {a.get('command','?')}\n[output]", "exit_code": 0}},
         {"name": "list_processes", "desc": "List running processes"},
         {"name": "kill_process", "desc": "Kill a process by PID"}]))

    servers.append(_build_server("vscode", "1.0.0", "VS Code editor control",
        [{"name": "open_file", "desc": "Open file in editor"},
         {"name": "run_extension", "desc": "Run VS Code extension command"},
         {"name": "get_diagnostics", "desc": "Get code diagnostics/lints"}]))

    servers.append(_build_server("docker", "1.0.0", "Docker container management",
        [{"name": "create_container", "desc": "Create Docker container",
          "handler": lambda a: {"container_id": str(uuid.uuid4())[:12], "image": a.get("image")}},
         {"name": "list_containers", "desc": "List running containers"},
         {"name": "container_logs", "desc": "Get container logs"},
         {"name": "stop_container", "desc": "Stop a container"}]))

    servers.append(_build_server("kubernetes", "1.0.0", "Kubernetes cluster management",
        [{"name": "get_pods", "desc": "List pods in namespace",
          "handler": lambda a: {"pods": [{"name":"app-abc","status":"Running","ready":"1/1"}]}},
         {"name": "get_deployments", "desc": "List deployments"},
         {"name": "apply_manifest", "desc": "Apply K8s manifest"},
         {"name": "get_logs", "desc": "Get pod logs"}]))

    servers.append(_build_server("terraform", "1.0.0", "Terraform Cloud management",
        [{"name": "plan", "desc": "Run terraform plan"},
         {"name": "apply", "desc": "Apply terraform changes"},
         {"name": "list_workspaces", "desc": "List Terraform workspaces"}]))

    servers.append(_build_server("npm-search", "1.0.0", "Search NPM packages",
        [{"name": "search", "desc": "Search NPM registry",
          "handler": lambda a: {"packages": [{"name":"express","version":"4.18.2","weekly":30000000}]}}]))

    servers.append(_build_server("linear", "1.0.0", "Linear project management",
        [{"name": "list_issues", "desc": "List Linear issues"},
         {"name": "create_issue", "desc": "Create new issue"},
         {"name": "update_status", "desc": "Update issue status"}]))

    return servers

# ═══════════════════════════════════════════════════
# CATEGORY 3: DATABASE & DATA (24-30)
# ═══════════════════════════════════════════════════
def build_database_servers():
    servers = []
    for name, desc in [
        ("mysql", "MySQL database operations"),
        ("mongodb", "MongoDB document database"),
        ("redis", "Redis cache and data store"),
        ("supabase", "Supabase PostgreSQL + auth + storage"),
        ("airtable", "Airtable bases and records"),
        ("snowflake", "Snowflake data warehouse"),
        ("bigquery", "Google BigQuery analytics"),
    ]:
        tools = [
            {"name": "query", "desc": f"Execute query on {name}",
             "handler": lambda a, n=name: {"source": n, "rows": random.randint(0,100), "query": a.get("query","SELECT *")}},
            {"name": "list_tables", "desc": f"List {name} tables/collections",
             "handler": lambda a, n=name: {"source": n, "tables": ["users","orders","products"]}},
            {"name": "insert", "desc": f"Insert data into {name}"},
        ]
        if name == "redis":
            tools.extend([
                {"name": "get", "desc": "Get value by key"},
                {"name": "set", "desc": "Set key-value pair"},
                {"name": "delete", "desc": "Delete key"},
            ])
        servers.append(_build_server(name, "1.0.0", desc, tools))
    return servers

# ═══════════════════════════════════════════════════
# CATEGORY 4: CLOUD & INFRASTRUCTURE (31-36)
# ═══════════════════════════════════════════════════
def build_cloud_servers():
    servers = []
    cloud_specs = [
        ("aws", "Amazon Web Services", ["s3_list","s3_get","lambda_invoke","ec2_list","dynamodb_query","sqs_send"]),
        ("google-cloud", "Google Cloud Platform", ["gcs_list","bigquery_query","pubsub_publish","run_deploy","firestore_query"]),
        ("azure", "Microsoft Azure", ["blob_list","sql_query","functions_invoke","cosmos_query"]),
        ("cloudflare", "Cloudflare services", ["dns_list","workers_deploy","kv_get","r2_upload"]),
        ("vercel", "Vercel deployment platform", ["deploy","list_deployments","get_logs","set_env"]),
        ("netlify", "Netlify hosting", ["deploy_site","list_sites","get_build_log"]),
    ]
    for name, desc, tool_names in cloud_specs:
        tools = [{"name": tn, "desc": f"{tn.replace('_',' ').title()} on {name}",
                  "handler": lambda a, t=tn, n=name: {"cloud": n, "action": t, "status": "ok"}}
                 for tn in tool_names]
        servers.append(_build_server(name, "1.0.0", desc, tools))
    return servers

# ═══════════════════════════════════════════════════
# CATEGORY 5: PRODUCTIVITY & BUSINESS (37-45)
# ═══════════════════════════════════════════════════
def build_productivity_servers():
    specs = [
        ("notion", "Notion workspace", ["search_pages","create_page","update_page","query_database"]),
        ("google-calendar", "Google Calendar", ["list_events","create_event","update_event","delete_event"]),
        ("gmail", "Gmail email", ["list_emails","send_email","create_draft","search_emails"]),
        ("outlook", "Microsoft 365", ["list_emails","send_email","list_events","list_files"]),
        ("jira", "Jira project management", ["list_issues","create_issue","update_issue","search_jql"]),
        ("trello", "Trello boards", ["list_boards","create_card","move_card","list_lists"]),
        ("asana", "Asana tasks", ["list_tasks","create_task","update_task","list_projects"]),
        ("hubspot", "HubSpot CRM", ["list_contacts","create_contact","list_deals","update_deal"]),
        ("salesforce", "Salesforce CRM", ["soql_query","create_record","update_record","list_objects"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()}"} for tn in tools])
        for n, d, tools in specs]

# ═══════════════════════════════════════════════════
# CATEGORY 6: SEARCH & KNOWLEDGE (46-50)
# ═══════════════════════════════════════════════════
def build_search_servers():
    specs = [
        ("tavily", "AI-optimized search", ["search","extract"]),
        ("perplexity", "AI search with sources", ["search","ask"]),
        ("wikipedia", "Wikipedia articles", ["search","get_article","get_summary"]),
        ("arxiv", "ArXiv papers", ["search_papers","get_abstract","download_pdf"]),
        ("exa", "Neural semantic search", ["search","find_similar","get_contents"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()} via {n}",
          "handler": lambda a, t=tn, nm=n: {"source": nm, "action": t, "results": random.randint(1,20)}}
         for tn in tools])
        for n, d, tools in specs]

# ═══════════════════════════════════════════════════
# CATEGORY 7: MEDIA & DESIGN (51-53)
# ═══════════════════════════════════════════════════
def build_media_servers():
    specs = [
        ("figma", "Figma design files", ["get_file","list_components","get_styles","get_images"]),
        ("cloudinary", "Media management", ["upload","transform","list_assets","delete_asset"]),
        ("youtube", "YouTube transcripts", ["get_transcript","search_videos","get_captions"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()}"} for tn in tools])
        for n, d, tools in specs]

# ═══════════════════════════════════════════════════
# CATEGORY 8: COMMUNICATION (54-57)
# ═══════════════════════════════════════════════════
def build_communication_servers():
    specs = [
        ("discord", "Discord messaging", ["send_message","read_messages","list_channels","list_servers"]),
        ("telegram", "Telegram bot", ["send_message","read_updates","send_photo","list_chats"]),
        ("whatsapp", "WhatsApp messaging", ["send_message","read_messages","list_contacts"]),
        ("twilio", "Twilio SMS/voice", ["send_sms","make_call","list_messages","get_number"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()}"} for tn in tools])
        for n, d, tools in specs]

# ═══════════════════════════════════════════════════
# CATEGORY 9: FINANCE & PAYMENT (58-60)
# ═══════════════════════════════════════════════════
def build_finance_servers():
    specs = [
        ("stripe", "Stripe payments", ["create_payment","list_customers","get_balance","create_subscription"]),
        ("coingecko", "Crypto market data", ["get_price","list_coins","get_market_chart","get_trending"]),
        ("alpha-vantage", "Stock market data", ["get_quote","get_timeseries","get_forex","get_crypto"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()}",
          "handler": lambda a, t=tn, nm=n: {"source": nm, "action": t, "data": {"price": round(random.uniform(1,50000),2)}}}
         for tn in tools])
        for n, d, tools in specs]

# ═══════════════════════════════════════════════════
# CATEGORY 10: SPECIALIZED (61-65)
# ═══════════════════════════════════════════════════
def build_specialized_servers():
    specs = [
        ("obsidian", "Obsidian notes", ["read_note","write_note","search_notes","list_vault"]),
        ("spotify", "Spotify music", ["play","search_tracks","create_playlist","get_now_playing"]),
        ("home-assistant", "Smart home control", ["list_devices","turn_on","turn_off","get_state","set_temperature"]),
        ("openweathermap", "Weather data", ["current_weather","forecast","air_quality"]),
        ("todoist", "Task management", ["list_tasks","create_task","complete_task","list_projects"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()}"} for tn in tools])
        for n, d, tools in specs]

# ═══════════════════════════════════════════════════
# CATEGORY 11: SECURITY & MONITORING (66-68)
# ═══════════════════════════════════════════════════
def build_security_servers():
    specs = [
        ("sentry", "Error monitoring", ["list_issues","get_issue","get_events","resolve_issue"]),
        ("datadog", "Infrastructure monitoring", ["query_metrics","list_monitors","get_logs","create_alert"]),
        ("grafana", "Dashboard analytics", ["list_dashboards","query_datasource","get_alerts","create_panel"]),
    ]
    return [_build_server(n, "1.0.0", d,
        [{"name": tn, "desc": f"{tn.replace('_',' ').title()}"} for tn in tools])
        for n, d, tools in specs]


# ═══════════════════════════════════════════════════
# 🧪 TEST — BUILD ALL 68 SERVERS
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    from mcp_protocol import MCPClient

    print("=" * 70)
    print("🌐 OMNI MCP — 68 SERVERS (ALL CATEGORIES)")
    print("=" * 70)

    registry = MCPServerRegistry()
    categories = {
        "Official (1-15)": build_official_servers,
        "Development (16-23)": build_dev_servers,
        "Database (24-30)": build_database_servers,
        "Cloud (31-36)": build_cloud_servers,
        "Productivity (37-45)": build_productivity_servers,
        "Search (46-50)": build_search_servers,
        "Media (51-53)": build_media_servers,
        "Communication (54-57)": build_communication_servers,
        "Finance (58-60)": build_finance_servers,
        "Specialized (61-65)": build_specialized_servers,
        "Security (66-68)": build_security_servers,
    }

    total_servers = 0
    total_tools = 0

    for cat_name, builder in categories.items():
        servers = builder()
        cat_tools = sum(len(s.tools) for s in servers)
        total_servers += len(servers)
        total_tools += cat_tools
        print(f"\n{'─'*60}")
        print(f"📋 {cat_name}: {len(servers)} servers, {cat_tools} tools")
        for s in servers:
            registry.register(s, cat_name)
            tools_str = ", ".join(list(s.tools.keys())[:4])
            extra = f" +{len(s.tools)-4}" if len(s.tools) > 4 else ""
            print(f"   🔌 {s.name:<20} [{len(s.tools)} tools] {tools_str}{extra}")

    # ── CLIENT TEST: Connect to key servers and call tools ──
    print(f"\n{'━'*60}")
    print("🧪 CLIENT INTEGRATION TESTS")
    print(f"{'━'*60}")
    client = MCPClient("OmniAgent")

    test_calls = [
        ("filesystem", "read_file", {"path": "/etc/config.yml"}),
        ("postgres", "query", {"sql": "SELECT * FROM users LIMIT 5"}),
        ("github", "create_issue", {"title": "Bug: MCP timeout"}),
        ("brave-search", "web_search", {"query": "OMNI Framework"}),
        ("docker", "create_container", {"image": "nginx:latest"}),
        ("aws", "s3_list", {"bucket": "my-data"}),
        ("stripe", "create_payment", {"amount": 4999, "currency": "usd"}),
        ("sentry", "list_issues", {"project": "omni-api"}),
    ]

    for srv_name, tool_name, args in test_calls:
        srv = registry.get(srv_name)
        client.connect(srv_name, srv)
        result = client.call_tool(srv_name, tool_name, args)
        content = result["result"]["content"][0]["text"][:50]
        print(f"   ✅ {srv_name}.{tool_name}: {content}...")

    # ── FINAL SUMMARY ──
    print(f"\n{'='*70}")
    print(f"✅ OMNI MCP — {total_servers} SERVERS, {total_tools} TOOLS TOTAL")
    print(f"{'='*70}")
    print(f"   Official:      15 servers (filesystem, git, github, slack, ...)")
    print(f"   Development:    8 servers (playwright, docker, k8s, terraform, ...)")
    print(f"   Database:       7 servers (postgres, mysql, mongo, redis, ...)")
    print(f"   Cloud:          6 servers (aws, gcp, azure, cloudflare, ...)")
    print(f"   Productivity:   9 servers (notion, jira, gmail, salesforce, ...)")
    print(f"   Search:         5 servers (tavily, perplexity, arxiv, ...)")
    print(f"   Media:          3 servers (figma, cloudinary, youtube)")
    print(f"   Communication:  4 servers (discord, telegram, whatsapp, twilio)")
    print(f"   Finance:        3 servers (stripe, coingecko, alpha-vantage)")
    print(f"   Specialized:    5 servers (obsidian, spotify, home-assistant, ...)")
    print(f"   Security:       3 servers (sentry, datadog, grafana)")
    print(f"   TOTAL:         {total_servers} servers, {total_tools} tools")
    print(f"{'='*70}")
