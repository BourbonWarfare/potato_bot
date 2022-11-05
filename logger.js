const log4js = require("log4js");

log4js.configure({
  appenders: { out: { type: "stdout" } },
  categories: { default: { appenders: ["out"], level: "info" } },
  pm2: true,
});

const logger = log4js.getLogger("out");

module.exports = logger;
