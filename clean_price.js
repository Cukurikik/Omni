const fs = require("fs");
const path = require("path");

function walkDir(dir) {
  const results = [];
  const items = fs.readdirSync(dir);
  for (const item of items) {
    const full = path.join(dir, item);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      results.push(...walkDir(full));
    } else if (item === "Omnifile.toml") {
      results.push(full);
    }
  }
  return results;
}

const baseDir = path.join(process.cwd(), "omni-runtime", "omni_modules");
const files = walkDir(baseDir);
let count = 0;

for (const file of files) {
  let content = fs.readFileSync(file, "utf8");
  if (content.includes("price_usd")) {
    // Hapus baris price_usd
    const lines = content.split("\n").filter((l) => !l.includes("price_usd"));
    fs.writeFileSync(file, lines.join("\n"), "utf8");
    count++;
  }
}

console.log(
  `Berhasil membersihkan price_usd dari ${count} file Omnifile.toml!`,
);
