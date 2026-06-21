import { spawn } from "node:child_process";
import { createReadStream, existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";

const repoRoot = resolve(process.cwd());
const docsRoot = join(repoRoot, "docs");
const siteSrcRoot = join(repoRoot, "site-src");
const tailwindInput = join(siteSrcRoot, "input.css");
const tailwindOutput = join(docsRoot, "assets", "site.css");
const tailwindConfig = join(repoRoot, "tailwind.config.js");
const host = process.env.HOST || "0.0.0.0";
const port = Number(process.env.PORT || 4173);
const clients = new Set();
const fileState = new Map();
let pollTimer;
let reloadTimer;
let buildRunning = false;
let buildQueued = false;

const mimeTypes = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".svg", "image/svg+xml"],
  [".webp", "image/webp"],
  [".ico", "image/x-icon"],
]);

const reloadSnippet = [
  "<script>",
  "  (() => {",
  '    const source = new EventSource("/__reload");',
  '    source.addEventListener("reload", () => window.location.reload());',
  "  })();",
  "</script>",
].join("\n");

function broadcastReload() {
  for (const response of clients) {
    response.write("event: reload\\ndata: now\\n\\n");
  }
}

function queueReload(delay = 80) {
  clearTimeout(reloadTimer);
  reloadTimer = setTimeout(() => broadcastReload(), delay);
}

function collectFiles(rootDir, files = []) {
  for (const entry of readdirSync(rootDir, { withFileTypes: true })) {
    if (entry.name === ".git") continue;
    const fullPath = join(rootDir, entry.name);
    if (entry.isDirectory()) {
      collectFiles(fullPath, files);
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

function isTailwindRelated(filePath) {
  return filePath === tailwindConfig || filePath.startsWith(siteSrcRoot) || filePath.endsWith(join("docs", "index.html"));
}

function scanForChanges() {
  const changedPaths = [];
  const seen = new Set();
  const files = [...collectFiles(docsRoot), ...collectFiles(siteSrcRoot), tailwindConfig];

  for (const filePath of files) {
    if (!existsSync(filePath)) continue;
    const stats = statSync(filePath);
    const next = `${stats.mtimeMs}:${stats.size}`;
    seen.add(filePath);
    if (fileState.get(filePath) !== next) {
      fileState.set(filePath, next);
      changedPaths.push(filePath);
    }
  }

  for (const filePath of [...fileState.keys()]) {
    if (!seen.has(filePath)) {
      fileState.delete(filePath);
      changedPaths.push(filePath);
    }
  }

  return changedPaths;
}

function runTailwindBuild() {
  if (buildRunning) {
    buildQueued = true;
    return;
  }

  buildRunning = true;
  const child = spawn(
    process.platform === "win32" ? "npx.cmd" : "npx",
    [
      "tailwindcss",
      "-c",
      tailwindConfig,
      "-i",
      tailwindInput,
      "-o",
      tailwindOutput,
    ],
    { cwd: repoRoot, stdio: ["ignore", "pipe", "pipe"] },
  );

  child.stdout.on("data", (chunk) => process.stdout.write(chunk.toString()));
  child.stderr.on("data", (chunk) => process.stderr.write(chunk.toString()));
  child.on("exit", (code) => {
    buildRunning = false;
    if (code === 0) {
      queueReload();
    }
    if (buildQueued) {
      buildQueued = false;
      runTailwindBuild();
    }
  });
}

function startPolling() {
  scanForChanges();
  pollTimer = setInterval(() => {
    const changedPaths = scanForChanges();
    if (changedPaths.length === 0) return;

    if (changedPaths.some(isTailwindRelated)) {
      runTailwindBuild();
      return;
    }

    queueReload();
  }, 250);
}

function serveFile(filePath, response) {
  const extension = extname(filePath).toLowerCase();
  const type = mimeTypes.get(extension) || "application/octet-stream";
  response.writeHead(200, { "Content-Type": type });
  createReadStream(filePath).pipe(response);
}

function serveHtml(filePath, response) {
  const html = readFileSync(filePath, "utf8");
  const injected = html.includes("</body>")
    ? html.replace("</body>", `${reloadSnippet}\n</body>`)
    : `${html}\n${reloadSnippet}`;

  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(injected);
}

const server = createServer((request, response) => {
  const requestUrl = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
  const pathname = decodeURIComponent(requestUrl.pathname);

  if (pathname === "/__reload") {
    response.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });
    response.write("\n");
    clients.add(response);
    request.on("close", () => clients.delete(response));
    return;
  }

  const relativePath = pathname === "/" ? "index.html" : pathname.replace(/^\/+/, "");
  const filePath = normalize(join(docsRoot, relativePath));

  if (!filePath.startsWith(docsRoot) || !existsSync(filePath) || statSync(filePath).isDirectory()) {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    response.end("Not found");
    return;
  }

  if (extname(filePath).toLowerCase() === ".html") {
    serveHtml(filePath, response);
    return;
  }

  serveFile(filePath, response);
});

runTailwindBuild();
startPolling();

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    clearTimeout(reloadTimer);
    clearInterval(pollTimer);
    server.close(() => process.exit(0));
  });
}

server.listen(port, host, () => {
  const displayHost = host === "0.0.0.0" ? "127.0.0.1" : host;
  console.log(`Site dev server: http://${displayHost}:${port} (bind: ${host})`);
});
