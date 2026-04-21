import urllib.request
import os

repos = [
    "e2b-dev/E2B",
    "tensorzero/tensorzero",
    "JCodesMore/ai-website-cloner-template",
    "microsoft/promptflow",
    "wandb/wandb",
    "getumbrel/llama-gpt",
    "YaoFANGUK/video-subtitle-remover",
    "Arindam200/awesome-ai-apps",
    "Netflix/metaflow"
]

branches = ["main", "master"]

output_dir = ".system_generated/curriculum_batch8"

for repo in repos:
    success = False
    for branch in branches:
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                safe_name = repo.replace("/", "_")
                path = os.path.join(output_dir, f"{safe_name}.md")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[OK] Fetched {repo} ({branch})")
                success = True
                break
        except Exception as e:
            continue
    if not success:
        print(f"[FAIL] Failed to fetch {repo}")
