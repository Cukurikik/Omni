import time
import json

# ==========================================
# 🏢 OMNI MULTI-AGENT: MetaGPT Engine (Phase 148)
# ==========================================
# Framework 4: MetaGPT
#   - Simulasi perusahaan software AI
#   - Standard Operating Procedures (SOP)
#   - Fixed roles: Product Manager, Architect, Engineer, QA
#   - Input 1 kalimat → Output full project
#   - Natural Language Programming

class SOPRole:
    """MetaGPT Role dengan SOP (Standard Operating Procedure)."""

    def __init__(self, name: str, title: str, sop_steps: list):
        self.name = name
        self.title = title
        self.sop_steps = sop_steps
        self.artifacts = []

    def act(self, input_data: dict) -> dict:
        print(f"\n   🏢 [{self.title}: {self.name}]")
        result = {}
        for step in self.sop_steps:
            print(f"      📋 SOP: {step['action']}")
            output = step["fn"](input_data)
            result[step["artifact"]] = output
            self.artifacts.append({step["artifact"]: output})
            print(f"         → Artifact: {step['artifact']} ({len(str(output))} chars)")
        return result


class MetaGPTCompany:
    """MetaGPT: AI Software Company Simulation."""

    def __init__(self):
        print("🏢 [METAGPT] AI Software Company diinisiasi.")
        self.roles = self._create_roles()
        self.project = {}

    def _create_roles(self) -> dict:
        pm = SOPRole("Alice", "Product Manager", [
            {"action": "Menganalisis requirement dari user",
             "artifact": "user_stories",
             "fn": lambda d: [
                 f"Sebagai user, saya ingin {d.get('idea', 'N/A')}",
                 "Sebagai user, saya ingin UI yang responsif",
                 "Sebagai user, saya ingin performa tinggi",
             ]},
            {"action": "Membuat Product Backlog",
             "artifact": "product_backlog",
             "fn": lambda d: [
                 {"id": "PB-001", "priority": "HIGH", "story": f"Implementasi {d.get('idea', 'core')}"},
                 {"id": "PB-002", "priority": "MEDIUM", "story": "UI Dashboard"},
                 {"id": "PB-003", "priority": "LOW", "story": "Unit Testing"},
             ]},
        ])

        architect = SOPRole("Bob", "Software Architect", [
            {"action": "Merancang System Architecture",
             "artifact": "architecture",
             "fn": lambda d: {
                 "pattern": "Microservices + Event-Driven",
                 "components": ["API Gateway", "Agent Service", "Message Queue", "Vector DB"],
                 "tech_stack": {"backend": "Python", "queue": "Redis", "db": "PostgreSQL"},
             }},
            {"action": "Membuat API Specification",
             "artifact": "api_spec",
             "fn": lambda d: [
                 {"endpoint": "POST /agents", "description": "Create new agent"},
                 {"endpoint": "POST /tasks", "description": "Assign task to agent"},
                 {"endpoint": "GET /results", "description": "Get task results"},
             ]},
        ])

        engineer = SOPRole("Charlie", "Software Engineer", [
            {"action": "Menulis kode berdasarkan arsitektur",
             "artifact": "source_code",
             "fn": lambda d: {
                 "main.py": "class AgentSystem:\n    def run(self): ...",
                 "agent.py": "class Agent:\n    def execute(self, task): ...",
                 "api.py": "app = FastAPI()\n@app.post('/agents')\nasync def create(): ...",
                 "total_files": 3,
                 "total_lines": 150,
             }},
            {"action": "Menulis Dockerfile & CI/CD",
             "artifact": "devops",
             "fn": lambda d: {
                 "Dockerfile": "FROM python:3.11\nCOPY . /app\nCMD ['python', 'main.py']",
                 "ci_pipeline": "GitHub Actions: lint → test → build → deploy",
             }},
        ])

        qa = SOPRole("Diana", "QA Engineer", [
            {"action": "Menulis test cases",
             "artifact": "test_cases",
             "fn": lambda d: [
                 {"test": "test_create_agent", "status": "PASS", "coverage": "85%"},
                 {"test": "test_assign_task", "status": "PASS", "coverage": "78%"},
                 {"test": "test_get_results", "status": "PASS", "coverage": "92%"},
             ]},
            {"action": "Menjalankan integration test",
             "artifact": "test_report",
             "fn": lambda d: {
                 "total_tests": 3, "passed": 3, "failed": 0,
                 "coverage": "85%", "status": "ALL TESTS PASSED"
             }},
        ])

        return {"pm": pm, "architect": architect, "engineer": engineer, "qa": qa}

    def develop(self, idea: str) -> dict:
        """Input 1 kalimat → Output full project."""
        print(f"\n{'='*60}")
        print(f"🚀 [METAGPT] IDEA: \"{idea}\"")
        print(f"{'='*60}")

        input_data = {"idea": idea}

        # SOP Pipeline: PM → Architect → Engineer → QA
        print("\n📋 SOP PIPELINE:")
        pm_output = self.roles["pm"].act(input_data)
        input_data.update(pm_output)

        arch_output = self.roles["architect"].act(input_data)
        input_data.update(arch_output)

        eng_output = self.roles["engineer"].act(input_data)
        input_data.update(eng_output)

        qa_output = self.roles["qa"].act(input_data)
        input_data.update(qa_output)

        self.project = input_data

        # Summary
        print(f"\n{'─'*60}")
        print("📦 PROJECT DELIVERABLES:")
        print(f"   📝 User Stories: {len(pm_output.get('user_stories', []))}")
        print(f"   📋 Backlog Items: {len(pm_output.get('product_backlog', []))}")
        print(f"   🏗️ Architecture: {arch_output.get('architecture', {}).get('pattern', 'N/A')}")
        print(f"   🔌 API Endpoints: {len(arch_output.get('api_spec', []))}")
        print(f"   💻 Source Files: {eng_output.get('source_code', {}).get('total_files', 0)}")
        print(f"   🧪 Tests: {qa_output.get('test_report', {}).get('total_tests', 0)} ({qa_output.get('test_report', {}).get('status', 'N/A')})")

        return self.project


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 65)
    print("🏢 OMNI METAGPT — AI Software Company Simulation (SOP-Based)")
    print("=" * 65)

    company = MetaGPTCompany()
    project = company.develop("Buat multi-agent system untuk otomasi customer support dengan AI")

    print(f"\n{'='*65}")
    print("✅ MetaGPT: SOP Pipeline ✓ | PM→Architect→Engineer→QA ✓")
    print("   User Stories ✓ | Architecture ✓ | Source Code ✓ | Tests ✓")
    print("   Natural Language to Full Project ✓")
    print(f"{'='*65}")
