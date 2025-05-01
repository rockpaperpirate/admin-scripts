// src/main.rs
// rustup toolchain install stable-x86_64-pc-windows-gnu
// rustup toolchain install stable-x86_64-pc-windows-msvc
// cargo build --release
//# .cargo/config.toml
// [build]
// # if you want this crate to default to the MSVC target:
// target = "x86_64-pc-windows-msvc"
// # for that MSVC target, enable static CRT (/MT instead of /MD)
// [target.x86_64-pc-windows-msvc]
// rustflags = [ "-Ctarget-feature=+crt-static" ]


use std::env;
use std::ffi::OsStr;
use std::fs;
use std::io::{self, Read};
use std::path::{Path, PathBuf};

/// A list of extensions we’ll consider “text documents”.
const TEXT_EXT: &[&str] = &["txt", "csv", "md", "log", "json", "xml", "yaml", "yml", "toml"];

fn is_text_file(path: &Path) -> bool {
    // 1) Extension check
    if let Some(ext) = path.extension().and_then(OsStr::to_str) {
        if TEXT_EXT.iter().any(|e| e.eq_ignore_ascii_case(ext)) {
            return true;
        }
    }
    // 2) Fallback: try reading first chunk as UTF-8
    if let Ok(mut f) = fs::File::open(path) {
        let mut buf = [0; 1024];
        if let Ok(n) = f.read(&mut buf) {
            return std::str::from_utf8(&buf[..n]).is_ok();
        }
    }
    false
}

fn visit_dir(dir: &Path, out: &mut Vec<PathBuf>) -> io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.is_dir() {
            visit_dir(&path, out)?;
        } else if is_text_file(&path) {
            out.push(path);
        }
    }
    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let start = args.get(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| env::current_dir().expect("cannot get cwd"));

    let mut found = Vec::new();
    if let Err(e) = visit_dir(&start, &mut found) {
        eprintln!("Error traversing {}: {}", start.display(), e);
        std::process::exit(1);
    }

    for p in found {
        println!("{}", p.display());
    }
}
