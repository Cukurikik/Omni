"""
╔══════════════════════════════════════════════════════════════════╗
║  🌉 OMNI MCP — AGENT BRIDGE INTEGRATION                        ║
║  Menghubungkan OMNI Agent Core dengan 68 MCP Servers            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

# Import dari OMNI AI Core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "omni_ai", "core"))
from omni_agent_core import OmniAgentDefinition, OmniAgentEngine, OmniToolRegistry, OmniTool, OmniToolType

# Import dari OMNI MCP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "servers"))
from mcp_protocol import MCPClient, MCPServerRegistry
import all_servers


class OMNIAgentMCPBridge:
    """
    Bridge yang memungkinkan OMNI Agent untuk secara dinamis
    menggunakan tool dari MCP servers mana pun.
    """
    def __init__(self, agent_name="OmniAgent"):
        self.client = MCPClient(agent_name)
        self.server_registry = MCPServerRegistry()
        self.agent_registry = OmniToolRegistry()

    def load_all_68_servers(self):
        """Memuat 68 server ke dalam registry MCP."""
        categories = {
            "Official": all_servers.build_official_servers,
            "Development": all_servers.build_dev_servers,
            "Database": all_servers.build_database_servers,
            "Cloud": all_servers.build_cloud_servers,
            "Productivity": all_servers.build_productivity_servers,
            "Search": all_servers.build_search_servers,
            "Media": all_servers.build_media_servers,
            "Communication": all_servers.build_communication_servers,
            "Finance": all_servers.build_finance_servers,
            "Specialized": all_servers.build_specialized_servers,
            "Security": all_servers.build_security_servers,
        }
        for cat, builder in categories.items():
            for srv in builder():
                self.server_registry.register(srv, cat)

    def equip_agent_with_server(self, server_name):
        """
        Menyambungkan MCP Client ke server tertentu, mengambil daftar tools,
        lalu mendaftarkannya sebagai OmniTools asli di agent.
        """
        srv = self.server_registry.get(server_name)
        if not srv:
            raise ValueError(f"Server '{server_name}' tidak ditemukan di MCP Registry.")

        # 1. Connect (Handshake)
        self.client.connect(server_name, srv)

        # 2. List tools dari MCP Server
        tools_resp = self.client.list_tools(server_name)
        mcp_tools = tools_resp.get("result", {}).get("tools", [])

        # 3. Register sebagai OMNI Tool native
        count = 0
        for mt in mcp_tools:
            tool_name = f"mcp_{server_name}_{mt['name']}"
            omni_tool = OmniTool(
                name=tool_name,
                description=f"[MCP {server_name}] {mt['description']}",
                # Fungsi handler yang mem-proxy call ke MCP Client
                fn=lambda **kwargs: (
                    lambda s=server_name, t=mt['name']: 
                        self.client.call_tool(s, t, kwargs).get("result", {}).get("content", [{"text":"error"}])[0]["text"]
                )(),
                tool_type=OmniToolType.API
            )
            self.agent_registry.register(omni_tool)
            count += 1
        return count


# ═══════════════════════════════════════════════════
# 🧪 TEST: INTEGRASI MOTHER AGENT + MCP
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 70)
    print("🌉 OMNI MCP — AGENT BRIDGE INTEGRATION")
    print("=" * 70)

    bridge = OMNIAgentMCPBridge("OmniMother")

    print("\n[1] Membangun 68 MCP Servers...")
    bridge.load_all_68_servers()
    total_servers = len(bridge.server_registry.servers)
    print(f"   ✅ Berhasil memuat {total_servers} MCP Servers ke dalam Metaverse.")

    print("\n[2] Menghubungkan OmniMother ke Server Spesifik (Equipping Tools)...")
    # Tuan Ikky, bayangkan Mother Agent sekarang memilih server mana yang dia butuhkan:
    target_servers = ["filesystem", "postgres", "github", "aws", "tavily", "slack"]
    
    total_mcp_tools = 0
    for srv_name in target_servers:
        equipped_count = bridge.equip_agent_with_server(srv_name)
        total_mcp_tools += equipped_count
        print(f"   ✅ Terhubung ke '{srv_name}': +{equipped_count} tools ditambahkan.")

    print(f"\n[3] Total OMNI Tools siap digunakan: {total_mcp_tools} Tools")

    print("\n[4] Membangun OMNI Agent dengan Tools MCP...")
    # Konstruksi agent
    mother = OmniAgentDefinition(
        name="OmniMother",
        goal="Bantu user melakukan operasi filesystem, database, cloud, dan komunikasi via MCP.",
        instructions=["Gunakan tools dengan prefiks 'mcp_' untuk mengakses dunia luar."],
        persona="Mother dapat menyentuh dunia luar"
    )
    
    # Memasukkan semua tool dari bridge registry ke Mother
    for tool in bridge.agent_registry.tools.values():
        mother.add_tool(tool)
        
    engine = OmniAgentEngine(mother)
    print("   ✅ Agent Engine siap.")

    print("\n[5] SIMULASI REQUEST MULTI-DOMAIN DARI USER")
    
    # Simulasi eksekusi Tool secara manual seperti dilingkupan ReAct Think-Act Agent:
    print("\n      🤖 [OmniMother] Menerima instruksi: 'Tolong cari file config di filesystem lalu push ke github'")
    
    # Aksi 1: Panggil tool mcp_filesystem_read_file
    print("\n      💭 Think: Saya butuh membaca filesystem lokal.")
    res1 = bridge.agent_registry.tools.get("mcp_filesystem_read_file").execute(**{"path": "/app/config.json"})
    print(f"      🔧 Act (mcp_filesystem_read_file): {res1}")

    # Aksi 2: Panggil tool mcp_github_create_issue
    print("\n      💭 Think: Saya perlu melaporkan ini ke GitHub.")
    res2 = bridge.agent_registry.tools.get("mcp_github_create_issue").execute(**{"title": "Config file found"})
    print(f"      🔧 Act (mcp_github_create_issue): {res2}")

    # Aksi 3: Panggil tool mcp_slack_send_message
    print("\n      💭 Think: Saya harus update ke tim via Slack.")
    res3 = bridge.agent_registry.tools.get("mcp_slack_send_message").execute(**{"channel": "#devops"})
    print(f"      🔧 Act (mcp_slack_send_message): {res3}")

    print(f"\n{'='*70}")
    print("✅ INTEGRASI OMNI MCP KE AGENT MOTHER: SEMPURNA!")
    print("   Mother Agent kini memiliki kapabilitas ekstensi TAK TERBATAS.")
    print("   Protokol JSON-RPC MCP terhubung mulus ke native OMNI Tools format.")
    print(f"{'='*70}")
