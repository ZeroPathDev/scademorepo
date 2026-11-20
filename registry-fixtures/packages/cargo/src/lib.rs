pub fn policy_version() -> String {
    format!("1.0.{}", itoa::Buffer::new().format(0))
}
