// ==========================================
// ⚡ OMNI-TRANSPILER: TypeScript/TSX → JS (Rust + SWC)
// ==========================================
// Mengkonversi TypeScript dan JSX/TSX menjadi JavaScript murni
// yang bisa dibaca V8 Engine secara REAL-TIME (~0.001ms).
//
// KEUNGGULAN: SWC (Rust-native) 100x lebih cepat dari Babel (JS-based)
// ==========================================

use thiserror::Error;

use swc_core::{
    common::{
        errors::Handler,
        sync::Lrc, FileName, Globals, Mark, SourceMap, GLOBALS,
    },
    ecma::{
        ast::{EsVersion, Program as SwcProgram},
        codegen::{text_writer::JsWriter, Emitter, Config as CodegenConfig},
        parser::{lexer::Lexer, Parser, StringInput, Syntax, TsSyntax},
        transforms::{
            base::{fixer::fixer, resolver},
            react::{react, Options as ReactOptions, Runtime as ReactRuntime},
            typescript::strip,
        },
    },
};

#[derive(Error, Debug)]
pub enum TranspileError {
    #[error("🔥 [TRANSPILER] Parse Error: {0}")]
    ParseError(String),
    #[error("🔥 [TRANSPILER] Codegen Error: {0}")]
    CodegenError(String),
}

pub type TranspileResult<T> = Result<T, TranspileError>;

pub struct OmniTranspiler;

impl OmniTranspiler {
    pub fn preprocess_omni_chimera(source: &str) -> String {
        let mut result = String::new();
        let mut current_idx = 0;
        let bytes = source.as_bytes();
        
        let re_var = regex::Regex::new(r"\$([a-zA-Z0-9_.]+)").unwrap();

        while let Some(mut start) = source[current_idx..].find("use::") {
            start += current_idx;
            result.push_str(&source[current_idx..start]);
            
            let lang_start = start + 5;
            let mut lang_end = lang_start;
            while lang_end < source.len() && bytes[lang_end].is_ascii_alphabetic() {
                lang_end += 1;
            }
            let lang = &source[lang_start..lang_end];

            let mut brace_start = lang_end;
            while brace_start < source.len() && bytes[brace_start] != b'{' {
                brace_start += 1;
            }
            
            if brace_start >= source.len() {
                result.push_str("use::");
                current_idx = start + 5;
                continue;
            }

            let mut depth = 1;
            let mut brace_end = brace_start + 1;
            while brace_end < source.len() && depth > 0 {
                let c = bytes[brace_end];
                if c == b'{' { depth += 1; }
                if c == b'}' { depth -= 1; }
                brace_end += 1;
            }

            if depth > 0 {
                result.push_str("use::");
                current_idx = start + 5;
                continue;
            }
            
            let code = &source[brace_start+1..brace_end-1];
            let safe_code = code.replace("`", "\\`");
            
            // Replace $var with ${var} for JS template literals
            let safe_code = re_var.replace_all(&safe_code, |caps: &regex::Captures| {
                format!("${{{}}}", &caps[1])
            }).to_string();

            // Emit the JavaScript equivalent: await __omni_inline_exec("lang", `...`)
            let js_call = format!("await __omni_inline_exec(\"{}\", `{}`)", lang, safe_code);
            result.push_str(&js_call);
            
            current_idx = brace_end;
        }
        
        result.push_str(&source[current_idx..]);
        result
    }

    /// Transpile TypeScript/TSX → JavaScript murni
    pub fn transpile(source: &str, filename: &str, is_jsx: bool) -> TranspileResult<String> {
        GLOBALS.set(&Globals::new(), || {
            let processed_source = Self::preprocess_omni_chimera(source);
            Self::transpile_inner(&processed_source, filename, is_jsx)
        })
    }

    fn transpile_inner(source: &str, filename: &str, is_jsx: bool) -> TranspileResult<String> {
        let cm: Lrc<SourceMap> = Default::default();
        let emitter = Box::new(swc_core::common::errors::emitter::EmitterWriter::new(
            Box::new(std::io::stderr()),
            Some(cm.clone()),
            false,
            true,
        ));
        let handler = Handler::with_emitter(true, false, emitter);
        let fm = cm.new_source_file(Lrc::new(FileName::Custom(filename.into())), source.to_string());

        // STEP 1: PARSE → AST
        let syntax = Syntax::Typescript(TsSyntax { tsx: is_jsx, decorators: true, ..Default::default() });
        let lexer = Lexer::new(syntax, EsVersion::Es2022, StringInput::from(&*fm), None);
        let mut parser = Parser::new_from(lexer);
        let module = parser.parse_module().map_err(|e| {
            e.into_diagnostic(&handler).emit();
            TranspileError::ParseError(format!("Gagal parse {}", filename))
        })?;

        // STEP 2: TRANSFORM (Strip types + JSX)
        let unresolved = Mark::new();
        let top_level = Mark::new();
        let mut program = SwcProgram::Module(module);

        program.mutate(resolver(unresolved, top_level, true));
        program.mutate(strip(unresolved, top_level));

        if is_jsx {
            program.mutate(react(
                cm.clone(), None::<swc_core::common::comments::SingleThreadedComments>,
                ReactOptions { runtime: Some(ReactRuntime::Automatic), ..Default::default() },
                top_level, unresolved,
            ));
        }
        program.mutate(fixer(None));

        let module = match program {
            SwcProgram::Module(m) => m,
            _ => return Err(TranspileError::CodegenError("Expected script to be a module".into())),
        };

        // STEP 3: CODEGEN → JS String
        let mut buf = Vec::new();
        {
            let wr = JsWriter::new(cm.clone(), "\n", &mut buf, None);
            let cfg = CodegenConfig::default().with_target(EsVersion::Es2022).with_minify(false);
            let mut emitter = Emitter { cfg, cm: cm.clone(), comments: None, wr };
            emitter.emit_module(&module).map_err(|e| TranspileError::CodegenError(e.to_string()))?;
        }

        String::from_utf8(buf).map_err(|e| TranspileError::CodegenError(e.to_string()))
    }

    /// Quick: TypeScript → JS
    pub fn transpile_ts(source: &str) -> TranspileResult<String> {
        Self::transpile(source, "input.ts", false)
    }

    /// Quick: TSX → JS
    pub fn transpile_tsx(source: &str) -> TranspileResult<String> {
        Self::transpile(source, "input.tsx", true)
    }

    /// Detect: file perlu transpile?
    pub fn needs_transpile(filename: &str) -> bool {
        let f = filename.to_lowercase();
        f.ends_with(".ts") || f.ends_with(".tsx") || f.ends_with(".jsx") || f.ends_with(".mts") || f.ends_with(".omni")
    }

    pub fn is_jsx_file(filename: &str) -> bool {
        let f = filename.to_lowercase();
        f.ends_with(".tsx") || f.ends_with(".jsx") || f.ends_with(".omni")
    }
}
