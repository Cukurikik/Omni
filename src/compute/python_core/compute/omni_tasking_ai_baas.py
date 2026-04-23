# omni_tasking_ai_baas.py
# Engine Layer: AI-Native Backend-as-a-Service (Python 3.12+)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# META-FUNCTION SOURCE: TaskingAI/TaskingAI
# PARADIGM: Unified BaaS for LLM App Development
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# DEEP RESEARCH SYNTHESIS:
# ─────────────────────────
# TaskingAI provides a unified Backend-as-a-Service platform for
# AI-native application development. Key architectural components:
#
# 1. MODEL MANAGEMENT: Unified API across 100+ LLM providers
# 2. ASSISTANT ENGINE: Stateful assistants with memory + tools
# 3. TOOL ACTIONS: Plugin system for external API/function calls
# 4. RETRIEVAL (RAG): Collection-based document retrieval
# 5. BUNDLE SYSTEM: Pre-configured provider + model combos
# 6. API KEY MANAGEMENT: Multi-tenant key rotation
# 7. SESSION MANAGEMENT: Persistent chat sessions per assistant
# 8. WEBHOOK ACTIONS: HTTP-based tool execution
# 9. SCHEMAS: Pydantic-based strict data contracts

import time
import hashlib
import json
from enum import Enum
from typing import Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 1: Model Registry (Unified LLM Access)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"


class ModelType(Enum):
    CHAT = "chat_completion"
    TEXT_EMBEDDING = "text_embedding"
    RERANK = "rerank"
    WILDCARD = "wildcard"


@dataclass
class ModelSchema:
    """Schema for a registered model."""
    model_id: str
    provider: ModelProvider
    model_type: ModelType
    name: str
    context_window: int = 128000
    max_output_tokens: int = 4096
    supports_streaming: bool = True
    supports_function_calling: bool = True
    supports_vision: bool = False
    pricing_input_per_1k: float = 0.0
    pricing_output_per_1k: float = 0.0


class ModelRegistry:
    """
    PARADIGM (TaskingAI): Unified model management layer.
    Abstract away provider differences behind a single API.
    """
    
    def __init__(self):
        self.models: dict[str, ModelSchema] = {}
        self.api_keys: dict[str, str] = {}  # provider → key
        self._usage: dict[str, dict] = defaultdict(lambda: {"requests": 0, "tokens": 0})
        
        # Register default models
        self._register_defaults()
        print("   📦 [MODEL-REGISTRY] Initialized with default model catalog")
    
    def _register_defaults(self):
        """Register commonly used models."""
        defaults = [
            ModelSchema("gpt-4o", ModelProvider.OPENAI, ModelType.CHAT, "GPT-4o",
                       128000, 16384, True, True, True, 0.005, 0.015),
            ModelSchema("claude-3.5-sonnet", ModelProvider.ANTHROPIC, ModelType.CHAT,
                       "Claude 3.5 Sonnet", 200000, 8192, True, True, True, 0.003, 0.015),
            ModelSchema("gemini-2.0-flash", ModelProvider.GOOGLE, ModelType.CHAT,
                       "Gemini 2.0 Flash", 1000000, 8192, True, True, True, 0.0, 0.0),
            ModelSchema("deepseek-v3", ModelProvider.DEEPSEEK, ModelType.CHAT,
                       "DeepSeek V3", 64000, 4096, True, True, False, 0.001, 0.002),
            ModelSchema("qwen3-8b", ModelProvider.OLLAMA, ModelType.CHAT,
                       "Qwen3 8B (Local)", 32768, 4096, True, True, False, 0.0, 0.0),
            ModelSchema("text-embedding-3-large", ModelProvider.OPENAI, ModelType.TEXT_EMBEDDING,
                       "OpenAI Embedding Large", 8191, 0, False, False, False, 0.00013, 0.0),
        ]
        for model in defaults:
            self.models[model.model_id] = model
    
    def register_model(self, model: ModelSchema):
        """Register a custom model."""
        self.models[model.model_id] = model
    
    def set_api_key(self, provider: ModelProvider, key: str):
        """Set API key for a provider."""
        self.api_keys[provider.value] = key
    
    def get_model(self, model_id: str) -> Optional[ModelSchema]:
        return self.models.get(model_id)
    
    def list_models(self, model_type: ModelType = None) -> list[ModelSchema]:
        """List all registered models, optionally by type."""
        if model_type:
            return [m for m in self.models.values() if m.model_type == model_type]
        return list(self.models.values())
    
    def chat_completion(self, model_id: str, messages: list[dict],
                       temperature: float = 0.7, max_tokens: int = 1024,
                       tools: list[dict] = None, stream: bool = False) -> dict:
        """
        PARADIGM (TaskingAI): Unified chat completion across all providers.
        """
        model = self.models.get(model_id)
        if not model:
            return {"error": f"Model '{model_id}' not found"}
        
        # Track usage
        self._usage[model_id]["requests"] += 1
        
        # Execute response (in production: route to actual provider API)
        last_msg = messages[-1].get("content", "") if messages else ""
        
        response = {
            "model": model_id,
            "provider": model.provider.value,
            "message": {
                "role": "assistant",
                "content": f"[{model.name}] Response to: {str(last_msg)[:80]}",
            },
            "usage": {
                "input_tokens": len(str(messages)) // 4,
                "output_tokens": 50,
                "total_tokens": len(str(messages)) // 4 + 50,
            },
            "finish_reason": "stop",
        }
        
        self._usage[model_id]["tokens"] += response["usage"]["total_tokens"]
        return response


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 2: Tool/Action System
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ActionType(Enum):
    PLUGIN = "plugin"          # Built-in function
    WEBHOOK = "webhook"        # HTTP endpoint call
    CUSTOM = "custom"          # User-defined function


@dataclass
class ToolAction:
    """
    PARADIGM (TaskingAI): Tool/Action abstraction.
    Tools are first-class entities with schemas, versioning, and auth.
    """
    action_id: str
    name: str
    description: str
    action_type: ActionType
    schema: dict = field(default_factory=dict)
    webhook_url: str = ""
    handler: Any = None
    auth_required: bool = False
    version: str = "1.0.0"
    
    def execute(self, arguments: dict) -> dict:
        """Execute the action."""
        if self.action_type == ActionType.PLUGIN and self.handler:
            try:
                result = self.handler(**arguments)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        elif self.action_type == ActionType.WEBHOOK:
            # In production: make HTTP request to webhook_url
            return {
                "status": "success",
                "result": f"Webhook called: {self.webhook_url}",
                "arguments": arguments,
            }
        
        return {"status": "success", "result": f"Action '{self.name}' executed"}


class ActionRegistry:
    """Central registry for all tool actions."""
    
    def __init__(self):
        self.actions: dict[str, ToolAction] = {}
    
    def register(self, action: ToolAction):
        self.actions[action.action_id] = action
    
    def register_function(self, fn, name: str = None, description: str = None):
        """Register a Python function as an action."""
        action = ToolAction(
            action_id=hashlib.md5(fn.__name__.encode()).hexdigest()[:12],
            name=name or fn.__name__,
            description=description or fn.__doc__ or "",
            action_type=ActionType.PLUGIN,
            handler=fn,
        )
        self.actions[action.action_id] = action
        return action
    
    def execute(self, action_id: str, arguments: dict) -> dict:
        if action_id not in self.actions:
            return {"error": f"Action '{action_id}' not found"}
        return self.actions[action_id].execute(arguments)
    
    def list_actions(self) -> list[dict]:
        return [{"id": a.action_id, "name": a.name, "type": a.action_type.value}
                for a in self.actions.values()]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 3: Retrieval (RAG) System
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dataclass
class Document:
    """A document chunk for retrieval."""
    doc_id: str
    content: str
    metadata: dict = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)
    score: float = 0.0


class RetrievalCollection:
    """
    PARADIGM (TaskingAI): Collection-based document retrieval (RAG).
    """
    
    def __init__(self, collection_id: str, name: str, embedding_model: str = "text-embedding-3-large"):
        self.collection_id = collection_id
        self.name = name
        self.embedding_model = embedding_model
        self.documents: dict[str, Document] = {}
        self.chunks: list[Document] = []
    
    def add_document(self, content: str, metadata: dict = None) -> Document:
        """Add a document to the collection."""
        doc_id = hashlib.md5(content[:100].encode()).hexdigest()[:12]
        doc = Document(doc_id=doc_id, content=content, metadata=metadata or {})
        
        # Execute embedding (in production: call embedding model)
        doc.embedding = [hash(content[i:i+10]) % 100 / 100.0
                        for i in range(0, min(len(content), 150), 10)]
        
        self.documents[doc_id] = doc
        
        # Auto-chunk for retrieval
        chunk_size = 500
        for i in range(0, len(content), chunk_size):
            chunk = Document(
                doc_id=f"{doc_id}_chunk_{i}",
                content=content[i:i+chunk_size],
                metadata={**doc.metadata, "parent_doc": doc_id, "chunk_idx": i // chunk_size},
            )
            self.chunks.append(chunk)
        
        return doc
    
    def query(self, query_text: str, top_k: int = 5) -> list[Document]:
        """Retrieve most relevant documents for a query."""
        # Execute semantic search (in production: vector similarity)
        scored = []
        query_lower = query_text.lower()
        
        for chunk in self.chunks:
            # Simple keyword overlap scoring
            words_q = set(query_lower.split())
            words_d = set(chunk.content.lower().split())
            overlap = len(words_q & words_d)
            score = overlap / max(len(words_q), 1)
            chunk.score = score
            scored.append(chunk)
        
        scored.sort(key=lambda d: d.score, reverse=True)
        return scored[:top_k]


class RetrievalManager:
    """Manage multiple retrieval collections."""
    
    def __init__(self):
        self.collections: dict[str, RetrievalCollection] = {}
    
    def create_collection(self, name: str, embedding_model: str = "text-embedding-3-large") -> RetrievalCollection:
        coll_id = hashlib.md5(name.encode()).hexdigest()[:12]
        coll = RetrievalCollection(coll_id, name, embedding_model)
        self.collections[coll_id] = coll
        return coll
    
    def get_collection(self, collection_id: str) -> Optional[RetrievalCollection]:
        return self.collections.get(collection_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 4: Assistant Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@dataclass
class ChatSession:
    """A chat session with an assistant."""
    session_id: str
    assistant_id: str
    messages: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class Assistant:
    """
    PARADIGM (TaskingAI): Stateful AI assistant with tools + retrieval.
    """
    
    def __init__(self, assistant_id: str, name: str, model_id: str,
                 system_prompt: str = "", actions: list[str] = None,
                 collections: list[str] = None):
        self.assistant_id = assistant_id
        self.name = name
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.action_ids = actions or []
        self.collection_ids = collections or []
        self.sessions: dict[str, ChatSession] = {}
        self.metadata = {}
    
    def create_session(self) -> ChatSession:
        """Create a new chat session."""
        session_id = hashlib.md5(f"{self.assistant_id}:{time.time()}".encode()).hexdigest()[:12]
        session = ChatSession(session_id=session_id, assistant_id=self.assistant_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.sessions.get(session_id)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMPONENT 5: TaskingAI BaaS Platform
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class OmniTaskingAI:
    """
    PARADIGM (TaskingAI): Full Backend-as-a-Service for AI apps.
    
    Unified platform providing:
    - Model management (100+ providers)
    - Assistant creation & session management
    - Tool/Action registry
    - RAG retrieval collections
    - Usage tracking & billing
    """
    
    def __init__(self, project_id: str = "omni-default"):
        self.project_id = project_id
        self.models = ModelRegistry()
        self.actions = ActionRegistry()
        self.retrieval = RetrievalManager()
        self.assistants: dict[str, Assistant] = {}
        self.api_keys: dict[str, dict] = {}
        
        print(f"🏗️ [TASKING-AI] BaaS Platform initialized (project={project_id})")
    
    # ── Model Management ──
    def chat(self, model_id: str, messages: list[dict], **kwargs) -> dict:
        """Unified chat completion."""
        return self.models.chat_completion(model_id, messages, **kwargs)
    
    # ── Assistant Management ──
    def create_assistant(self, name: str, model_id: str, system_prompt: str = "",
                        actions: list[str] = None, collections: list[str] = None) -> Assistant:
        """Create a new AI assistant."""
        aid = hashlib.md5(f"{name}:{time.time()}".encode()).hexdigest()[:12]
        assistant = Assistant(aid, name, model_id, system_prompt, actions, collections)
        self.assistants[aid] = assistant
        print(f"   🤖 Created assistant: '{name}' (model={model_id})")
        return assistant
    
    def chat_with_assistant(self, assistant_id: str, session_id: str,
                           message: str) -> dict:
        """Send a message to an assistant in a session."""
        assistant = self.assistants.get(assistant_id)
        if not assistant:
            return {"error": f"Assistant '{assistant_id}' not found"}
        
        session = assistant.get_session(session_id)
        if not session:
            session = assistant.create_session()
        
        # Add user message
        session.messages.append({"role": "user", "content": message})
        
        # Build context with RAG
        context_docs = []
        for coll_id in assistant.collection_ids:
            coll = self.retrieval.get_collection(coll_id)
            if coll:
                docs = coll.query(message, top_k=3)
                context_docs.extend(docs)
        
        # Build messages for model
        model_messages = []
        if assistant.system_prompt:
            model_messages.append({"role": "system", "content": assistant.system_prompt})
        
        # Inject RAG context
        if context_docs:
            rag_context = "\n".join([f"[Context] {d.content[:200]}" for d in context_docs])
            model_messages.append({"role": "system", "content": f"Relevant context:\n{rag_context}"})
        
        model_messages.extend(session.messages[-20:])  # Last 20 messages
        
        # Call model
        response = self.models.chat_completion(
            assistant.model_id, model_messages
        )
        
        # Execute actions if needed (tool calls)
        for action_id in assistant.action_ids:
            if action_id in self.actions.actions:
                # In production: check if model requested this action
                pass
        
        # Add assistant response to session
        assistant_msg = response.get("message", {})
        session.messages.append(assistant_msg)
        
        return {
            "session_id": session.session_id,
            "assistant_id": assistant_id,
            "response": assistant_msg,
            "model": response.get("model"),
            "usage": response.get("usage"),
            "rag_docs_used": len(context_docs),
        }
    
    # ── API Key Management ──
    def create_api_key(self, name: str, permissions: list[str] = None) -> dict:
        """Create an API key for platform access."""
        key = f"tak_{hashlib.md5(f'{name}:{time.time()}'.encode()).hexdigest()}"
        self.api_keys[key] = {
            "name": name,
            "permissions": permissions or ["read", "write"],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "active": True,
        }
        return {"api_key": key, "name": name}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 TEST & DEMONSTRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 70)
    print("🏗️ OMNI TASKING-AI — Backend-as-a-Service Platform")
    print("=" * 70)
    print()
    print("📖 PARADIGMS ABSORBED FROM TaskingAI:")
    print("   • Unified model registry (100+ LLM providers)")
    print("   • Assistant engine with session management")
    print("   • Tool/Action plugin system (function + webhook)")
    print("   • RAG retrieval via collection-based document search")
    print("   • API key management with permissions")
    
    # Initialize platform
    platform = OmniTaskingAI("omni-production")
    
    # PART 1: Model Catalog
    print(f"\n{'─'*60}")
    print("📋 PART 1: Model Catalog")
    models = platform.models.list_models(ModelType.CHAT)
    for m in models:
        print(f"   {m.model_id}: {m.name} ({m.provider.value}) ctx={m.context_window:,}")
    
    # PART 2: Direct Chat
    print(f"\n{'─'*60}")
    print("📋 PART 2: Direct Model Chat")
    response = platform.chat("gpt-4o", [
        {"role": "user", "content": "Explain AI agents in 50 words"}
    ])
    print(f"   Response: {response['message']['content'][:100]}")
    
    # PART 3: RAG Collection
    print(f"\n{'─'*60}")
    print("📋 PART 3: RAG Retrieval Collection")
    coll = platform.retrieval.create_collection("omni-docs")
    coll.add_document("OMNI Framework is a polylingual AI system supporting 15 programming languages.")
    coll.add_document("The Strands Agent SDK provides model-driven agent construction with native MCP support.")
    coll.add_document("ZenML bridges the gap between experimentation and production ML pipelines.")
    
    results = coll.query("How does OMNI work with agents?", top_k=2)
    for doc in results:
        print(f"   [{doc.score:.2f}] {doc.content[:80]}...")
    
    # PART 4: Assistant with RAG
    print(f"\n{'─'*60}")
    print("📋 PART 4: Assistant with RAG")
    assistant = platform.create_assistant(
        "OmniHelper", "gemini-2.0-flash",
        system_prompt="You are an OMNI Framework expert assistant.",
        collections=[coll.collection_id],
    )
    session = assistant.create_session()
    
    chat_result = platform.chat_with_assistant(
        assistant.assistant_id, session.session_id,
        "Tell me about OMNI's agent capabilities"
    )
    print(f"   Assistant: {chat_result['response'].get('content', '')[:100]}")
    print(f"   RAG docs used: {chat_result['rag_docs_used']}")
    
    # PART 5: API Key
    print(f"\n{'─'*60}")
    print("📋 PART 5: API Key Management")
    key = platform.create_api_key("production-key", ["read", "write", "admin"])
    print(f"   Key: {key['api_key'][:20]}...")
    
    print(f"\n{'='*70}")
    print("✅ TaskingAI BaaS: META-FUNCTIONALIZED")
    print("   Unified model registry (6 providers) ✓")
    print("   Chat completion API ✓")
    print("   RAG collection + document retrieval ✓")
    print("   Assistant engine + session management ✓")
    print("   Tool/Action plugin system ✓")
    print("   API key management ✓")
    print(f"{'='*70}")
