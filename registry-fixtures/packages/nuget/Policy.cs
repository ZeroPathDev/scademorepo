namespace ZeroPath.Rehearsal {
    public static class Policy {
        public static string Version() { return "1.0.0 (" + Newtonsoft.Json.JsonConvert.SerializeObject("policy") + ")"; }
    }
}
