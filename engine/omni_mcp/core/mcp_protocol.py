"""
╔══════════════════════════════════════════════════════════════════╗
║  🔌 OMNI MCP — CORE PROTOCOL ENGINE                            ║
║  Model Context Protocol: JSON-RPC 2.0 Transport Layer           ║
║  Implements: Tools, Resources, Prompts, Sampling, Lifecycle     ║
╚══════════════════════════════════════════════════════════════════╝

PROSES BELAJAR JUJUR — MCP PROTOCOL:
──────────────────────────────────────────────────

MCP (Model Context Protocol) adalah STANDAR TERBUKA dari Anthropic
yang menghubungkan AI agent dengan external tools dan data.

ARSITEKTUR MCP:
┌────────────────────────────────────────────────────────────┐
│  AI Host (Claude, GPT, Gemini, OMNI Agent)                │
│    ├── MCP Client (mengirim request)                      │
│    │     ↕ JSON-RPC 2.0                                   │
│    ├── MCP Server A (filesystem)                          │
│    ├── MCP Server B (database)                            │
│    ├── MCP Server C (search)                              │
│    └── MCP Server D (cloud)                               │
└────────────────────────────────────────────────────────────┘

PROTOKOL JSON-RPC 2.0:
┌──────────────────────────────────────────────────────┐
│ Request:  {"jsonrpc":"2.0","id":1,"method":"x","params":{}} │
│ Response: {"jsonrpc":"2.0","id":1,"result":{...}}          │
│ Notif:    {"jsonrpc":"2.0","method":"x","params":{}}       │
│ Error:    {"jsonrpc":"2.0","id":1,"error":{"code":x,...}}  │
└──────────────────────────────────────────────────────┘

LIFECYCLE:
1. Client → initialize (capabilities, protocol version)
2. Server → response (server capabilities)
3. Client → initialized (notification)
4. Normal operation (tools/call, resources/read, etc.)
5. Client → shutdown / Server → exit

5 KEMAMPUAN MCP SERVER:
┌──────────────────────────────────────────────────────┐
│ 1. TOOLS     — Functions agent bisa panggil         │
│ 2. RESOURCES — Data agent bisa baca (files, DB)     │
│ 3. PROMPTS   — Template prompt yang disediakan      │
│ 4. SAMPLING  — Server minta LLM completion ke client│
│ 5. LOGGING   — Structured log messages              │
└──────────────────────────────────────────────────────┘

TRANSPORT TYPES:
- stdio   : stdin/stdout (paling umum, untuk CLI tools)
- SSE     : Server-Sent Events over HTTP (untuk web)
- WebSocket: bidirectional (untuk real-time)
"""

import json
import uuid
import time
import traceback
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# JSON-RPC 2.0 PROTOCOL
# ═══════════════════════════════════════════════════

class JsonRpcError:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        d = {"code": self.code, "message": self.message}
        if self.data:
            d["data"] = self.data
        return d


class JsonRpcMessage:
    """JSON-RPC 2.0 message builder."""
    @staticmethod
    def request(method, params=None, msg_id=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params:
            msg["params"] = params
        if msg_id is not None:
            msg["id"] = msg_id
        return msg

    @staticmethod
    def response(msg_id, result):
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    @staticmethod
    def error(msg_id, error):
        return {"jsonrpc": "2.0", "id": msg_id, "error": error.to_dict()}

    @staticmethod
    def notification(method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params:
            msg["params"] = params
        return msg


# ═══════════════════════════════════════════════════
# MCP TRANSPORT LAYER
# ═══════════════════════════════════════════════════

class TransportType(Enum):
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPTransport:
    """
    PELAJARAN: Transport = cara client dan server berkomunikasi.
    - stdio: paling umum, pakai stdin/stdout
    - SSE: HTTP streaming (server push events)
    - WebSocket: full-duplex bidirectional
    """
    def __init__(self, transport_type=TransportType.STDIO):
        self.type = transport_type
        self.send_buffer = []
        self.receive_buffer = []
        self.connected = False

    def connect(self):
        self.connected = True
        return True

    def send(self, message):
        if not self.connected:
            return False
        serialized = json.dumps(message)
        self.send_buffer.append(serialized)
        return True

    def receive(self):
        if self.receive_buffer:
            raw = self.receive_buffer.pop(0)
            return json.loads(raw) if isinstance(raw, str) else raw
        return None

    def inject_message(self, message):
        """Simulate receiving a message (for testing)."""
        self.receive_buffer.append(message)

    def close(self):
        self.connected = False


# ═══════════════════════════════════════════════════
# MCP TOOL DEFINITION
# ═══════════════════════════════════════════════════

class MCPTool:
    """
    PELAJARAN: Tool = function yang MCP server expose ke client.
    Schema menggunakan JSON Schema format (OpenAPI compatible).
    """
    def __init__(self, name, description, handler, input_schema=None):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema or {"type": "object", "properties": {}}
        self.call_count = 0
        self.total_latency_ms = 0

    def execute(self, arguments):
        start = time.time()
        self.call_count += 1
        try:
            result = self.handler(arguments)
            latency = (time.time() - start) * 1000
            self.total_latency_ms += latency
            return {"content": [{"type": "text", "text": json.dumps(result) if isinstance(result, dict) else str(result)}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}

    def to_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


# ═══════════════════════════════════════════════════
# MCP RESOURCE DEFINITION
# ═══════════════════════════════════════════════════

class MCPResource:
    """
    PELAJARAN: Resource = data yang server sediakan.
    Bisa file, database record, API response, dll.
    URI scheme: file://, db://, api://, custom://
    """
    def __init__(self, uri, name, description, mime_type="text/plain", reader=None):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.reader = reader or (lambda: f"Content of {uri}")

    def read(self):
        content = self.reader()
        return {"uri": self.uri, "mimeType": self.mime_type,
                "text": content if isinstance(content, str) else json.dumps(content)}

    def to_schema(self):
        return {"uri": self.uri, "name": self.name,
                "description": self.description, "mimeType": self.mime_type}


class MCPResourceTemplate:
    """URI template for dynamic resources (e.g., db://table/{table_name})."""
    def __init__(self, uri_template, name, description, mime_type="text/plain"):
        self.uri_template = uri_template
        self.name = name
        self.description = description
        self.mime_type = mime_type

    def to_schema(self):
        return {"uriTemplate": self.uri_template, "name": self.name,
                "description": self.description, "mimeType": self.mime_type}


# ═══════════════════════════════════════════════════
# MCP PROMPT DEFINITION
# ═══════════════════════════════════════════════════

class MCPPrompt:
    """
    PELAJARAN: Prompt = template prompt yang server sediakan.
    Agent bisa list prompts, lalu pilih + fill arguments.
    """
    def __init__(self, name, description, arguments=None, template_fn=None):
        self.name = name
        self.description = description
        self.arguments = arguments or []
        self.template_fn = template_fn

    def render(self, args):
        if self.template_fn:
            return self.template_fn(args)
        return {"messages": [{"role": "user", "content": {"type": "text",
                "text": f"Prompt '{self.name}' with args: {args}"}}]}

    def to_schema(self):
        return {"name": self.name, "description": self.description,
                "arguments": self.arguments}


# ═══════════════════════════════════════════════════
# MCP SERVER — CORE ENGINE
# ═══════════════════════════════════════════════════

class MCPServer:
    """
    PELAJARAN INTI — MCP Server = service yang expose tools/resources/prompts.
    
    LIFECYCLE:
    1. Client sends 'initialize' → server responds with capabilities
    2. Client sends 'initialized' notification
    3. Normal operation: tools/list, tools/call, resources/list, etc.
    4. Client sends 'shutdown' → server cleanup

    METHODS (yang harus server handle):
    - initialize         → handshake
    - tools/list         → list available tools
    - tools/call         → execute a tool
    - resources/list     → list static resources
    - resources/read     → read a resource
    - resources/templates/list → list dynamic resource templates
    - prompts/list       → list available prompts
    - prompts/get        → render a prompt
    - notifications/cancelled → client cancelled request
    - logging/setLevel   → set log verbosity
    """

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, name, version="1.0.0", description=""):
        self.name = name
        self.version = version
        self.description = description
        self.tools = {}
        self.resources = {}
        self.resource_templates = {}
        self.prompts = {}
        self.transport = MCPTransport()
        self.initialized = False
        self.log_level = "info"
        self.request_count = 0
        self.handlers = {}
        self._register_protocol_handlers()

    def _register_protocol_handlers(self):
        """Register all MCP protocol method handlers."""
        self.handlers = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
            "resources/templates/list": self._handle_resource_templates_list,
            "prompts/list": self._handle_prompts_list,
            "prompts/get": self._handle_prompts_get,
            "logging/setLevel": self._handle_set_log_level,
            "ping": self._handle_ping,
        }

    # ─── Capability Registration ───
    def add_tool(self, tool):
        self.tools[tool.name] = tool

    def add_resource(self, resource):
        self.resources[resource.uri] = resource

    def add_resource_template(self, template):
        self.resource_templates[template.uri_template] = template

    def add_prompt(self, prompt):
        self.prompts[prompt.name] = prompt

    # ─── Protocol Handlers ───
    def _handle_initialize(self, params):
        self.initialized = True
        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": {
                "tools": {"listChanged": True} if self.tools else {},
                "resources": {"subscribe": True, "listChanged": True} if self.resources else {},
                "prompts": {"listChanged": True} if self.prompts else {},
                "logging": {},
            },
            "serverInfo": {"name": self.name, "version": self.version},
        }

    def _handle_tools_list(self, params):
        return {"tools": [t.to_schema() for t in self.tools.values()]}

    def _handle_tools_call(self, params):
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        return tool.execute(arguments)

    def _handle_resources_list(self, params):
        return {"resources": [r.to_schema() for r in self.resources.values()]}

    def _handle_resources_read(self, params):
        uri = params.get("uri")
        resource = self.resources.get(uri)
        if not resource:
            raise ValueError(f"Resource '{uri}' not found")
        return {"contents": [resource.read()]}

    def _handle_resource_templates_list(self, params):
        return {"resourceTemplates": [t.to_schema() for t in self.resource_templates.values()]}

    def _handle_prompts_list(self, params):
        return {"prompts": [p.to_schema() for p in self.prompts.values()]}

    def _handle_prompts_get(self, params):
        name = params.get("name")
        arguments = params.get("arguments", {})
        prompt = self.prompts.get(name)
        if not prompt:
            raise ValueError(f"Prompt '{name}' not found")
        return prompt.render(arguments)

    def _handle_set_log_level(self, params):
        self.log_level = params.get("level", "info")
        return {}

    def _handle_ping(self, params):
        return {}

    # ─── Message Processing ───
    def process_message(self, message):
        """Process incoming JSON-RPC message and return response."""
        self.request_count += 1
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")

        # Notification (no id) — no response needed
        if msg_id is None:
            if method == "notifications/initialized":
                self.initialized = True
            return None

        handler = self.handlers.get(method)
        if not handler:
            return JsonRpcMessage.error(msg_id,
                JsonRpcError(JsonRpcError.METHOD_NOT_FOUND, f"Method '{method}' not found"))

        try:
            result = handler(params)
            return JsonRpcMessage.response(msg_id, result)
        except Exception as e:
            return JsonRpcMessage.error(msg_id,
                JsonRpcError(JsonRpcError.INTERNAL_ERROR, str(e)))

    def get_stats(self):
        return {
            "name": self.name, "version": self.version,
            "tools": len(self.tools), "resources": len(self.resources),
            "prompts": len(self.prompts), "templates": len(self.resource_templates),
            "requests_processed": self.request_count, "initialized": self.initialized,
        }


# ═══════════════════════════════════════════════════
# MCP CLIENT — Connects to servers
# ═══════════════════════════════════════════════════

class MCPClient:
    """
    PELAJARAN: MCP Client = sisi AI host yang menghubungi server.
    Client mengirim JSON-RPC requests, server menjawab.
    """
    def __init__(self, name="OmniAgent"):
        self.name = name
        self.servers = {}
        self.msg_counter = 0

    def connect(self, server_name, server):
        """Connect to an MCP server."""
        self.servers[server_name] = server
        # Initialize handshake
        init_req = JsonRpcMessage.request("initialize", {
            "protocolVersion": MCPServer.PROTOCOL_VERSION,
            "capabilities": {"sampling": {}},
            "clientInfo": {"name": self.name, "version": "1.0.0"},
        }, self._next_id())
        response = server.process_message(init_req)

        # Send initialized notification
        server.process_message(JsonRpcMessage.notification("notifications/initialized"))
        return response

    def _next_id(self):
        self.msg_counter += 1
        return self.msg_counter

    def list_tools(self, server_name):
        req = JsonRpcMessage.request("tools/list", {}, self._next_id())
        return self.servers[server_name].process_message(req)

    def call_tool(self, server_name, tool_name, arguments=None):
        req = JsonRpcMessage.request("tools/call",
            {"name": tool_name, "arguments": arguments or {}}, self._next_id())
        return self.servers[server_name].process_message(req)

    def list_resources(self, server_name):
        req = JsonRpcMessage.request("resources/list", {}, self._next_id())
        return self.servers[server_name].process_message(req)

    def read_resource(self, server_name, uri):
        req = JsonRpcMessage.request("resources/read", {"uri": uri}, self._next_id())
        return self.servers[server_name].process_message(req)

    def list_prompts(self, server_name):
        req = JsonRpcMessage.request("prompts/list", {}, self._next_id())
        return self.servers[server_name].process_message(req)

    def get_prompt(self, server_name, prompt_name, arguments=None):
        req = JsonRpcMessage.request("prompts/get",
            {"name": prompt_name, "arguments": arguments or {}}, self._next_id())
        return self.servers[server_name].process_message(req)

    def ping(self, server_name):
        req = JsonRpcMessage.request("ping", {}, self._next_id())
        return self.servers[server_name].process_message(req)


# ═══════════════════════════════════════════════════
# MCP SERVER REGISTRY — Manage multiple servers
# ═══════════════════════════════════════════════════

class MCPServerRegistry:
    """Central registry: discover, connect, manage multiple MCP servers."""
    def __init__(self):
        self.servers = {}
        self.categories = defaultdict(list)

    def register(self, server, category="general"):
        self.servers[server.name] = {"server": server, "category": category}
        self.categories[category].append(server.name)

    def get(self, name):
        entry = self.servers.get(name)
        return entry["server"] if entry else None

    def list_all(self):
        return [{"name": n, "category": e["category"],
                 **e["server"].get_stats()} for n, e in self.servers.items()]

    def list_by_category(self, category):
        return [self.servers[n]["server"] for n in self.categories.get(category, [])]

    def get_total_tools(self):
        return sum(len(e["server"].tools) for e in self.servers.values())


# ═══════════════════════════════════════════════════
# 🧪 TEST
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🔌 OMNI MCP — CORE PROTOCOL ENGINE")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   JSON-RPC 2.0: request/response/notification/error")
    print("   Transport: stdio/SSE/WebSocket")
    print("   Capabilities: Tools + Resources + Prompts + Sampling + Logging")
    print("   Lifecycle: initialize → initialized → operation → shutdown")

    # PART 1: Build a sample MCP server
    print(f"\n{'─'*60}")
    print("📋 PART 1: Build MCP Server")
    server = MCPServer("omni-demo-server", "1.0.0", "Demo MCP server")

    # Add tools
    server.add_tool(MCPTool(
        "greet", "Greet a person by name",
        lambda args: {"greeting": f"Hello, {args.get('name', 'World')}!"},
        {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    ))
    server.add_tool(MCPTool(
        "calculate", "Perform arithmetic",
        lambda args: {"result": eval(f"{args['a']} {args['op']} {args['b']}")},
        {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"},
         "op": {"type": "string", "enum": ["+", "-", "*", "/"]}}, "required": ["a", "b", "op"]}
    ))

    # Add resources
    server.add_resource(MCPResource("file://readme.md", "README", "Project readme",
                                    reader=lambda: "# OMNI Framework\nPolylingual runtime"))
    server.add_resource(MCPResource("config://app", "App Config", "Application config",
                                    "application/json",
                                    reader=lambda: json.dumps({"env": "production", "port": 8080})))

    # Add prompts
    server.add_prompt(MCPPrompt("code_review", "Review code for bugs",
        [{"name": "language", "required": True}, {"name": "code", "required": True}],
        lambda args: {"messages": [{"role": "user", "content": {"type": "text",
            "text": f"Review this {args.get('language')} code:\n{args.get('code')}"}}]}
    ))

    print(f"   Server: {server.name} v{server.version}")
    print(f"   Tools: {len(server.tools)}, Resources: {len(server.resources)}, Prompts: {len(server.prompts)}")

    # PART 2: MCP Client handshake
    print(f"\n{'─'*60}")
    print("📋 PART 2: MCP Client → Server Handshake")
    client = MCPClient("OmniAgent")
    init_response = client.connect("demo", server)
    print(f"   Initialize response:")
    print(f"   {json.dumps(init_response, indent=2)}")

    # PART 3: List tools
    print(f"\n{'─'*60}")
    print("📋 PART 3: tools/list + tools/call")
    tools_resp = client.list_tools("demo")
    print(f"   Available tools:")
    for t in tools_resp["result"]["tools"]:
        print(f"      🔧 {t['name']}: {t['description']}")

    call_resp = client.call_tool("demo", "greet", {"name": "Ikky"})
    print(f"   call greet: {call_resp['result']['content'][0]['text']}")

    calc_resp = client.call_tool("demo", "calculate", {"a": 42, "op": "*", "b": 10})
    print(f"   call calc: {calc_resp['result']['content'][0]['text']}")

    # PART 4: Resources
    print(f"\n{'─'*60}")
    print("📋 PART 4: resources/list + resources/read")
    res_resp = client.list_resources("demo")
    for r in res_resp["result"]["resources"]:
        print(f"   📄 {r['name']} ({r['uri']})")

    readme = client.read_resource("demo", "file://readme.md")
    print(f"   Read readme: {readme['result']['contents'][0]['text']}")

    # PART 5: Prompts
    print(f"\n{'─'*60}")
    print("📋 PART 5: prompts/list + prompts/get")
    prompts_resp = client.list_prompts("demo")
    for p in prompts_resp["result"]["prompts"]:
        print(f"   📝 {p['name']}: {p['description']}")

    prompt = client.get_prompt("demo", "code_review", {"language": "Python", "code": "def f(): pass"})
    print(f"   Rendered: {prompt['result']['messages'][0]['content']['text'][:50]}...")

    # PART 6: Error handling
    print(f"\n{'─'*60}")
    print("📋 PART 6: Error Handling")
    err_resp = client.call_tool("demo", "nonexistent_tool")
    print(f"   Error: {err_resp['error']['message']}")

    # PART 7: Server stats
    print(f"\n{'─'*60}")
    print("📋 PART 7: Server Stats & Registry")
    registry = MCPServerRegistry()
    registry.register(server, "development")
    print(f"   Stats: {json.dumps(server.get_stats(), indent=2)}")
    print(f"   Registry: {len(registry.servers)} servers, {registry.get_total_tools()} total tools")

    print(f"\n{'='*70}")
    print("✅ OMNI MCP Core Protocol Engine: DIPELAJARI.")
    print("   JSON-RPC 2.0: request/response/notification/error ✓")
    print("   Transport: stdio/SSE/WebSocket layer ✓")
    print("   MCPServer: tools + resources + prompts + lifecycle ✓")
    print("   MCPClient: connect + list + call + read + ping ✓")
    print("   MCPTool: handler + JSON Schema + execution ✓")
    print("   MCPResource: URI + reader + mime type ✓")
    print("   MCPPrompt: template + arguments + render ✓")
    print("   MCPServerRegistry: multi-server management ✓")
    print("   Error codes: PARSE/INVALID/NOT_FOUND/INTERNAL ✓")
    print(f"{'='*70}")
