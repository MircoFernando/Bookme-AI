import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import path from "node:path";
var __dirname = path.dirname(fileURLToPath(import.meta.url));
var srcDir = path.resolve(__dirname, "src");
// Run dev from this folder: `cd frontend && npm run dev` (or `make run-ui`).
// The `@/` alias maps to `src/` — e.g. `@/api/auth` → `src/api/auth.ts`.
// lets production deploy the UI behind the same hostname as the API.
export default defineConfig(function (_a) {
    var mode = _a.mode;
    var env = loadEnv(mode, process.cwd(), "");
    var apiTarget = env.VITE_API_URL || "http://localhost:8000";
    return {
        plugins: [react()],
        resolve: {
            alias: {
                "@": srcDir,
            },
        },
        server: {
            port: 5173,
            host: true,
            proxy: {
                "/api": {
                    target: apiTarget,
                    changeOrigin: true,
                    rewrite: function (path) { return path.replace(/^\/api/, ""); },
                },
            },
        },
    };
});
