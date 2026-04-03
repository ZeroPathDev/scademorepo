const express = require("express");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const sessions = new Map();

app.post("/auth/login", (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "Missing credentials" });
  }

  const sessionId = Math.random().toString(36).slice(2);
  sessions.set(sessionId, {
    username,
    createdAt: Date.now(),
    permissions: req.body.permissions || ["read"],
  });

  res.json({ sessionId, expiresIn: 3600 });
});

app.get("/api/search", (req, res) => {
  const { q, page, limit, filters } = req.query;

  const parsedFilters =
    typeof filters === "object" ? filters : {};

  res.json({
    query: q,
    page: parseInt(page) || 1,
    limit: parseInt(limit) || 20,
    filters: parsedFilters,
    results: [],
  });
});

app.get("/api/users/:id/settings", (req, res) => {
  const settings = req.query;
  const merged = Object.assign(
    { theme: "default", lang: "en" },
    settings
  );
  res.json({ userId: req.params.id, settings: merged });
});

app.listen(process.env.PORT || 4000, () => {
  console.log("Auth service started");
});
