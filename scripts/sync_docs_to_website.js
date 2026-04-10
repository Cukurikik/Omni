const fs = require('fs');
const path = require('path');

const MODULES_DIR = path.join(__dirname, '../omni-runtime/omni_modules');
const DOCS_TARGET_DIR = path.join(__dirname, '../omni-docs-site/docs');
const SOURCE_ROOT_DOC = path.join(__dirname, '../docs/OMNI-KNOWLEDGE-BASE.md');

function copyFolderRecursiveSync(source, target, moduleName) {
    let files = [];
    if (!fs.existsSync(target)) {
        fs.mkdirSync(target, { recursive: true });
    }

    if (fs.lstatSync(source).isDirectory()) {
        files = fs.readdirSync(source);
        files.forEach(function (file) {
            var curSource = path.join(source, file);
            var curTarget = path.join(target, file);
            if (fs.lstatSync(curSource).isDirectory()) {
                copyFolderRecursiveSync(curSource, curTarget, moduleName);
            } else {
                // Read content to prepend frontmatter for Docusaurus
                let content = fs.readFileSync(curSource, 'utf8');
                
                // Extremely simple mapping for filename to sidebar label
                let title = file.replace('.md', '');
                let fm = '---\ntitle: ' + title + '\nsidebar_label: ' + title + '\n---\n\n';
                
                fs.writeFileSync(curTarget, fm + content);
            }
        });
    }
}

async function run() {
    console.log("Emptying target docusaurus docs folder...");
    if (fs.existsSync(DOCS_TARGET_DIR)) {
        fs.rmSync(DOCS_TARGET_DIR, { recursive: true, force: true });
    }
    fs.mkdirSync(DOCS_TARGET_DIR, { recursive: true });

    // Copy Root OMNI-KNOWLEDGE-BASE
    if (fs.existsSync(SOURCE_ROOT_DOC)) {
        console.log("Copying Root Knowledge Base...");
        let content = fs.readFileSync(SOURCE_ROOT_DOC, 'utf8');
        let fm = '---\nid: OMNI-KNOWLEDGE-BASE\ntitle: OMNI KNOWLEDGE BASE\nslug: /OMNI-KNOWLEDGE-BASE\n---\n\n';
        fs.writeFileSync(path.join(DOCS_TARGET_DIR, 'OMNI-KNOWLEDGE-BASE.md'), fm + content);
    }

    console.log("Scanning OMNI modules...");
    const modules = fs.readdirSync(MODULES_DIR).filter(item => {
        const fullPath = path.join(MODULES_DIR, item);
        return fs.statSync(fullPath).isDirectory();
    });

    for (const mod of modules) {
        const sourceDocs = path.join(MODULES_DIR, mod, 'docs');
        const targetDocs = path.join(DOCS_TARGET_DIR, mod);
        
        if (fs.existsSync(sourceDocs)) {
            copyFolderRecursiveSync(sourceDocs, targetDocs, mod);
        }
    }

    console.log('✅ Successfully synchronized ' + modules.length + ' module docs to Docusaurus.');
}

run().catch(console.error);
