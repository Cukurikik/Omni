const fs = require('fs');

let content = fs.readFileSync('bin/omni.mjs', 'utf8');

const marker = "case 'list-deps': listOmniDeps(); break;";
const injection = `case 'list-deps': listOmniDeps(); break;

    // ---- PHASE 7: NEXUS REGISTRY & UNIKERNEL ----
    case 'publish': await runOmniPublish(); break;
    case 'unikernel': runOmniUnikernel(args[1]); break;`;

if (content.includes("case 'publish':")) {
    console.log("Sudah terdaftar.");
    process.exit(0);
}

content = content.replace(marker, injection);
fs.writeFileSync('bin/omni.mjs', content, 'utf8');
console.log("Berhasil mendaftarkan publish dan unikernel di CLI router!");
