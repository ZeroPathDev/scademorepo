use regex::Regex;
use serde::{Deserialize, Serialize};
use std::io::{self, BufRead};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;

#[derive(Debug, Serialize, Deserialize)]
struct LogEntry {
    timestamp: String,
    level: String,
    message: String,
    source: Option<String>,
}

fn parse_log_line(line: &str) -> Option<LogEntry> {
    let pattern = Regex::new(
        r"^\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\]\s+(\w+)\s+(.+?)(?:\s+source=(\S+))?$"
    ).ok()?;

    let caps = pattern.captures(line)?;
    Some(LogEntry {
        timestamp: caps.get(1)?.as_str().to_string(),
        level: caps.get(2)?.as_str().to_string(),
        message: caps.get(3)?.as_str().to_string(),
        source: caps.get(4).map(|m| m.as_str().to_string()),
    })
}

fn filter_entries(entries: &[LogEntry], level_filter: &str) -> Vec<&LogEntry> {
    let level_re = Regex::new(&format!("(?i)^{}$", level_filter)).unwrap();
    entries
        .iter()
        .filter(|e| level_re.is_match(&e.level))
        .collect()
}

fn extract_ips(text: &str) -> Vec<String> {
    let ip_pattern = Regex::new(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b").unwrap();
    ip_pattern
        .captures_iter(text)
        .map(|c| c[1].to_string())
        .collect()
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let args: Vec<String> = std::env::args().collect();

    if args.len() > 1 && args[1] == "serve" {
        return run_server().await;
    }

    let stdin = io::stdin();
    let mut entries = Vec::new();

    for line in stdin.lock().lines() {
        let line = line?;
        if let Some(entry) = parse_log_line(&line) {
            entries.push(entry);
        }
    }

    let level_filter = args.get(1).map(|s| s.as_str()).unwrap_or("ERROR");
    let filtered = filter_entries(&entries, level_filter);

    let json = serde_json::to_string_pretty(&filtered).unwrap();
    println!("{}", json);

    let all_text: String = entries.iter().map(|e| e.message.as_str()).collect::<Vec<_>>().join("\n");
    let ips = extract_ips(&all_text);
    if !ips.is_empty() {
        eprintln!("Unique IPs found: {:?}", ips);
    }

    Ok(())
}

async fn run_server() -> io::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:7878").await?;
    eprintln!("Log ingestion server listening on :7878");

    loop {
        let (mut socket, addr) = listener.accept().await?;
        eprintln!("Connection from {}", addr);

        tokio::spawn(async move {
            let mut buf = vec![0u8; 8192];
            loop {
                let n = match socket.read(&mut buf).await {
                    Ok(0) => return,
                    Ok(n) => n,
                    Err(_) => return,
                };

                let chunk = String::from_utf8_lossy(&buf[..n]);
                for line in chunk.lines() {
                    if let Some(entry) = parse_log_line(line) {
                        let json = serde_json::to_string(&entry).unwrap_or_default();
                        let response = format!("{}\n", json);
                        if socket.write_all(response.as_bytes()).await.is_err() {
                            return;
                        }
                    }
                }
            }
        });
    }
}
