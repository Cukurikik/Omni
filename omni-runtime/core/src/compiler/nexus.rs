use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::fs;
use super::ast::{OmniProgram, Stmt};
use super::lexer::Lexer;
use super::parser::Parser;

pub struct OmniNexus {
    loaded_files: HashSet<PathBuf>,
    visiting_files: HashSet<PathBuf>,
    merged_statements: Vec<Stmt>,
}

impl OmniNexus {
    pub fn new() -> Self {
        Self {
            loaded_files: HashSet::new(),
            visiting_files: HashSet::new(),
            merged_statements: Vec::new(),
        }
    }

    /// Bundles an entry file and all its recursive imports into a single OmniProgram.
    pub fn bundle(&mut self, entry_path: &Path) -> Result<OmniProgram, String> {
        self.load_recursive(entry_path)?;
        Ok(OmniProgram {
            statements: self.merged_statements.clone(),
        })
    }

    fn load_recursive(&mut self, file_path: &Path) -> Result<(), String> {
        let abs_path = fs::canonicalize(file_path)
            .map_err(|e| format!("Gagal menemukan file {}: {}", file_path.display(), e))?;

        if self.loaded_files.contains(&abs_path) {
            return Ok(());
        }

        if self.visiting_files.contains(&abs_path) {
            return Err(format!("Circular dependency detected: {}", abs_path.display()));
        }

        self.visiting_files.insert(abs_path.clone());

        let source = fs::read_to_string(&abs_path)
            .map_err(|e| format!("Gagal membaca file {}: {}", abs_path.display(), e))?;

        let lexer = Lexer::new(&source);
        let mut parser = Parser::new(lexer);
        let program = parser.parse_program();

        // Cari import statements untuk diproses lebih dulu (bundling)
        let mut imports = Vec::new();
        let mut other_stmts = Vec::new();

        for stmt in program.statements {
            if let Stmt::Import { path, .. } = &stmt {
                if path.starts_with(".") || path.starts_with("/") {
                    imports.push(path.clone());
                } else {
                    // External module import, keep it in AST for transpiler/runtime handling
                    other_stmts.push(stmt);
                }
            } else {
                other_stmts.push(stmt);
            }
        }

        // Proses rekursif local imports
        let parent_dir = abs_path.parent().unwrap_or(Path::new("."));
        for imp_path_str in imports {
            let mut imp_path = parent_dir.join(&imp_path_str);
            if imp_path.extension().is_none() {
                imp_path.set_extension("omni");
            }

            self.load_recursive(&imp_path)?;
        }

        // Tambahkan statement non-import ke bundel utama
        self.merged_statements.extend(other_stmts);

        self.visiting_files.remove(&abs_path);
        self.loaded_files.insert(abs_path);

        Ok(())
    }
}
