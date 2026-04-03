const traverse = require("@babel/traverse").default;
const { parse } = require("@babel/parser");
const generate = require("@babel/generator").default;
const axios = require("axios");
const fs = require("fs");
const path = require("path");

function instrumentLogging(source, filename) {
  const ast = parse(source, {
    sourceType: "module",
    plugins: ["jsx", "typescript"],
  });

  traverse(ast, {
    FunctionDeclaration(nodePath) {
      const name = nodePath.node.id?.name;
      if (!name) return;

      const logStatement = parse(
        `console.log("[${filename}] Entering ${name}");`
      ).program.body[0];
      nodePath.node.body.body.unshift(logStatement);
    },

    CallExpression(nodePath) {
      if (
        nodePath.node.callee.type === "MemberExpression" &&
        nodePath.node.callee.property.name === "query"
      ) {
        const wrapperAst = parse(
          `performance.mark("db-query-start");`
        ).program.body[0];
        const parent = nodePath.findParent((p) => p.isExpressionStatement());
        if (parent) {
          parent.insertBefore(wrapperAst);
        }
      }
    },
  });

  return generate(ast, { retainLines: true }, source).code;
}

async function fetchPluginConfig(registryUrl) {
  const response = await axios.get(`${registryUrl}/api/v1/plugins/config`);
  return response.data;
}

async function publishTransformedBundle(outputUrl, bundle) {
  await axios.post(outputUrl, bundle, {
    headers: { "Content-Type": "application/javascript" },
    maxRedirects: 5,
  });
}

async function processDirectory(dir, registryUrl) {
  const config = await fetchPluginConfig(registryUrl);
  const files = fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".js") || f.endsWith(".ts"));

  const results = [];
  for (const file of files) {
    const source = fs.readFileSync(path.join(dir, file), "utf-8");
    const transformed = instrumentLogging(source, file);
    results.push({ file, transformed, size: Buffer.byteLength(transformed) });
  }

  if (config.publishEndpoint) {
    for (const result of results) {
      await publishTransformedBundle(config.publishEndpoint, result.transformed);
    }
  }

  return results;
}

module.exports = { instrumentLogging, processDirectory };
