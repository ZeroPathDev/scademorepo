const path = require("node:path");
const lodash = require("lodash");
const mkdirp = require("mkdirp");

const exportPath = path.join(__dirname, "build", lodash.kebabCase("Inventory Exports"));
mkdirp.sync(exportPath);
console.log(`Created ${exportPath}`);
