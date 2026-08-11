// Entry point Playwright's `webServer` runs. Boots the static server on a fixed
// port and keeps it alive for the duration of the run.
import { startServer } from './server.mjs';
const PORT = Number(process.env.VIS_PORT || 8099);
await startServer(PORT);
console.log(`visual-test server on http://127.0.0.1:${PORT}`);
// Keep the process up.
setInterval(() => {}, 1 << 30);
