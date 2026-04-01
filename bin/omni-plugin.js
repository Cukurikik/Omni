#!/usr/bin/env node

const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');

program.version('1.0.0').description('Omni-Tool Plugin SDK CLI');

// Task 94: CLI init
program
  .command('init <pluginId>')
  .description('Membuat struktur boilerplate plugin baru')
  .action((pluginId) => {
    const targetDir = path.join(process.cwd(), pluginId);
    if (fs.existsSync(targetDir)) {
      console.error(`Error: Folder ${pluginId} sudah ada.`);
      process.exit(1);
    }
    
    fs.mkdirSync(targetDir);
    
    const manifest = {
      id: pluginId,
      name: `Plugin ${pluginId}`,
      version: '1.0.0',
      description: 'Deskripsi lengkap plugin',
      author: 'Author Name',
      main: 'index.js',
      permissions: ['read:local_files']
    };
    
    const indexJs = `
module.exports = {
  // Dipanggil oleh execution-engine
  run: async (payload, api) => {
    api.emitProgress(10);
    // Plugin logic here
    api.emitProgress(100);
    return { success: true, message: "Hello from Omni-Tool Plugin!" };
  }
};
    `;
    
    fs.writeFileSync(path.join(targetDir, 'plugin.json'), JSON.stringify(manifest, null, 2));
    fs.writeFileSync(path.join(targetDir, 'index.js'), indexJs.trim());
    
    console.log(`✅ Plugin ${pluginId} berhasil dibuat. Silakan modifikasi plugin.json dan index.js`);
  });

// Task 95: Local Plugin Bundler
program
  .command('build <pluginDir>')
  .description('Mem-bundle plugin menjadi file .zip siap rilis')
  .action((pluginDir) => {
    const targetDir = path.resolve(pluginDir);
    if (!fs.existsSync(targetDir) || !fs.existsSync(path.join(targetDir, 'plugin.json'))) {
      console.error(`Error: Folder tidak valid atau plugin.json hilang.`);
      process.exit(1);
    }
    
    const zip = new AdmZip();
    zip.addLocalFolder(targetDir);
    
    const outPath = path.join(process.cwd(), `${path.basename(pluginDir)}-release.zip`);
    zip.writeZip(outPath);
    console.log(`✅ Plugin dibundle ke ${outPath}. Siap diupload! (Integrity Signature: Skipped in Dev Mode)`);
  });

program.parse(process.argv);
