const express = require("express");
const _ = require("lodash");
const fetch = require("node-fetch");

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

const defaultConfig = {
  theme: "light",
  locale: "en-US",
  notifications: { email: true, sms: false },
};

app.get("/api/config", (req, res) => {
  const userOverrides = req.query.overrides
    ? JSON.parse(req.query.overrides)
    : {};
  const config = _.merge({}, defaultConfig, userOverrides);
  res.json(config);
});

app.post("/api/profiles", async (req, res) => {
  const profiles = req.body.profiles || [];
  const grouped = _.groupBy(profiles, "department");
  const sorted = _.orderBy(
    profiles,
    ["department", "lastName"],
    ["asc", "asc"]
  );

  const enriched = sorted.map((p) => ({
    ...p,
    displayName: _.capitalize(p.firstName) + " " + _.capitalize(p.lastName),
    initials: _.toUpper(p.firstName[0] + p.lastName[0]),
  }));

  res.json({ grouped, sorted: enriched });
});

app.get("/api/proxy", async (req, res) => {
  const url = req.query.url;
  if (!url) return res.status(400).json({ error: "url parameter required" });

  try {
    const response = await fetch(url);
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: "Failed to fetch upstream resource" });
  }
});

app.post("/api/templates", (req, res) => {
  const template = req.body.template || {};
  const defaults = {
    margin: { top: 10, bottom: 10, left: 15, right: 15 },
    font: { family: "Arial", size: 12 },
    header: { enabled: true },
  };
  const merged = _.defaultsDeep({}, template, defaults);
  res.json(merged);
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
