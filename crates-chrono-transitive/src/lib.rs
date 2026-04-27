use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEvent {
    pub id: String,
    pub actor: String,
    pub action: String,
    pub target: Option<String>,
    pub recorded_at: DateTime<Utc>,
}

impl AuditEvent {
    pub fn new(actor: impl Into<String>, action: impl Into<String>) -> Self {
        Self {
            id: format!("evt_{}", Utc::now().timestamp_nanos_opt().unwrap_or(0)),
            actor: actor.into(),
            action: action.into(),
            target: None,
            recorded_at: Utc::now(),
        }
    }

    pub fn with_target(mut self, target: impl Into<String>) -> Self {
        self.target = Some(target.into());
        self
    }

    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }
}

pub fn parse_window(window: &str) -> Option<(DateTime<Utc>, DateTime<Utc>)> {
    let mut parts = window.split("..");
    let start = DateTime::parse_from_rfc3339(parts.next()?).ok()?.with_timezone(&Utc);
    let end = DateTime::parse_from_rfc3339(parts.next()?).ok()?.with_timezone(&Utc);
    if end < start {
        return None;
    }
    Some((start, end))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builds_event_with_target() {
        let evt = AuditEvent::new("alice", "delete").with_target("repo:42");
        assert_eq!(evt.actor, "alice");
        assert_eq!(evt.target.as_deref(), Some("repo:42"));
    }

    #[test]
    fn parses_rfc3339_window() {
        let win = parse_window("2026-01-01T00:00:00Z..2026-02-01T00:00:00Z");
        assert!(win.is_some());
    }

    #[test]
    fn rejects_inverted_window() {
        assert!(parse_window("2026-02-01T00:00:00Z..2026-01-01T00:00:00Z").is_none());
    }
}
