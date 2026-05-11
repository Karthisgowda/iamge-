const { spawnSync, spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const action = process.argv[2] || "start";

function run(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: root,
    stdio: "inherit",
    shell: false,
    env: { ...process.env, ...options.env },
  });
}

function tryRun(command, args) {
  return spawnSync(command, args, {
    cwd: root,
    stdio: "pipe",
    shell: false,
    encoding: "utf8",
  });
}

function findPython() {
  const candidates = [
    { command: "python", args: ["--version"] },
    { command: "py", args: ["-3", "--version"], prefix: ["-3"] },
    { command: "python3", args: ["--version"] },
  ];

  for (const candidate of candidates) {
    const result = tryRun(candidate.command, candidate.args);
    const output = `${result.stdout || ""}${result.stderr || ""}`.trim();
    if (result.status === 0 && output.toLowerCase().includes("python")) {
      return {
        command: candidate.command,
        prefix: candidate.prefix || [],
        version: output,
      };
    }
  }

  console.error("Python was not found.");
  console.error('Install Python from https://www.python.org/downloads/ and enable "Add Python to PATH".');
  process.exit(1);
}

function ensureProjectRoot() {
  if (!fs.existsSync(path.join(root, "app.py"))) {
    console.error("app.py was not found.");
    console.error("Open the extracted project folder that contains app.py, then run npm again.");
    process.exit(1);
  }
}

function pythonArgs(python, extraArgs) {
  return [...python.prefix, ...extraArgs];
}

function setup() {
  ensureProjectRoot();
  const python = findPython();
  console.log(`Using ${python.version}`);
  const result = run(
    python.command,
    pythonArgs(python, ["-m", "pip", "install", "-r", "local-requirements.txt"])
  );
  process.exit(result.status || 0);
}

function check() {
  ensureProjectRoot();
  const python = findPython();
  const result = run(
    python.command,
    pythonArgs(python, [
      "-m",
      "py_compile",
      "app.py",
      "config.py",
      "forms.py",
      "image_recognition.py",
      "main.py",
      "models.py",
      "routes.py",
      "run_xampp.py",
      "api/index.py",
    ]),
    { env: { USE_SQLITE: "1" } }
  );
  process.exit(result.status || 0);
}

function start() {
  ensureProjectRoot();
  const python = findPython();

  console.log(`Using ${python.version}`);
  console.log("Starting Flask with local SQLite. XAMPP/MySQL is not required.");
  console.log("Open http://localhost:5000");
  console.log("Press Ctrl+C to stop the server.");

  const child = spawn(python.command, pythonArgs(python, ["app.py"]), {
    cwd: root,
    stdio: "inherit",
    shell: false,
    env: {
      ...process.env,
      USE_SQLITE: "1",
      FLASK_ENV: "development",
      FLASK_DEBUG: "1",
    },
  });

  child.on("exit", (code) => {
    process.exit(code || 0);
  });
}

if (action === "setup") {
  setup();
} else if (action === "check") {
  check();
} else if (action === "start") {
  start();
} else {
  console.error(`Unknown action: ${action}`);
  console.error("Use: npm run setup, npm run check, or npm start");
  process.exit(1);
}
