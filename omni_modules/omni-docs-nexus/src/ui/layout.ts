// ui/layout.ts
// TS Interface Layer rendering markdown into Neon Dark Mode UI

import { MarkdownParser } from "@omni-bridge/system/markdown";

@html_template("omni_docs_dashboard")
export function RenderDashboard(mdPointer: any, size: number): Uint8Array {
    // 1. Parsing raw memory pointer
    const rawMarkdown = MarkdownParser.fromDirectPointer(mdPointer, size);
    
    // 2. Konversi AST
    const htmlContent = MarkdownParser.toHTML(rawMarkdown);
    
    // 3. Bangun struktur antarmuka OMNI Singularity
    const webDocument = \`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OMNI-NEXUS 🪐 Knowledge Base</title>
        <style>
            :root {
                --omni-bg: #0c0f12;
                --omni-text: #e0e6ed;
                --omni-accent: #00f0ff;
                --omni-border: rgba(0, 240, 255, 0.2);
            }
            body {
                background-color: var(--omni-bg);
                color: var(--omni-text);
                font-family: 'Inter', system-ui, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
            }
            #sidebar {
                width: 300px;
                height: 100vh;
                position: fixed;
                border-right: 1px solid var(--omni-border);
                padding: 2rem;
                overflow-y: auto;
                background: rgba(12, 15, 18, 0.95);
                backdrop-filter: blur(10px);
            }
            #content {
                margin-left: 350px;
                padding: 3rem;
                max-width: 900px;
                line-height: 1.7;
            }
            h1, h2, h3 { color: var(--omni-accent); }
            h1 { text-shadow: 0 0 10px rgba(0, 240, 255, 0.5); }
            a { color: var(--omni-accent); text-decoration: none; }
            a:hover { text-shadow: 0 0 8px var(--omni-accent); }
            pre {
                background: #050608;
                border: 1px solid var(--omni-border);
                border-radius: 8px;
                padding: 1.5rem;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <nav id="sidebar">
            <h2 style="color: #fff">🪐 OMNI-NEXUS</h2>
            <p><strong>2.6 Million Words</strong> of architectural truth.</p>
            <!-- Auto-indexed tree link placeholder via JS Runtime -->
            <div id="tree-root"></div>
        </nav>
        <main id="content">
            \${htmlContent}
        </main>
        <script>
            // Hydrate sidebar navigations
            console.log("OMNI Singularity Engine initialized.");
        </script>
    </body>
    </html>
    \`;

    return TextEncoder.encode(webDocument);
}
