"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.FastAPIServer = void 0;
const child_process_1 = require("child_process");
const path = __importStar(require("path"));
const pythonPath = path.resolve(__dirname, "../../../coderag/bin/python");
// You should be sure that all requirements are installed in venv/conda/poetry environment and the path is right
class FastAPIServer {
    serverProcess = null;
    /**
     * Start the Uvicorn FastAPI server.
     * @param scriptPath Path to the FastAPI app (e.g., "main:app").
     * @param port Port to run the server on.
     */
    start(scriptPath, port = 8000) {
        if (this.serverProcess) {
            console.log("Server is already running.");
            return;
        }
        console.log(`Starting FastAPI server on port ${port}...`);
        this.serverProcess = (0, child_process_1.spawn)(pythonPath, ["-m", "uvicorn", scriptPath, `--port=${port}`], {
            stdio: "inherit", // Ensure child process streams are inherited by the parent process
            cwd: path.resolve(__dirname, "../../.."),
            env: {
                ...process.env, // Inherit the existing environment
                PYTHONPATH: path.resolve(__dirname, "../../.."), // Add app_root to PYTHONPATH
            },
        });
        this.serverProcess.on("error", (err) => {
            console.error("Failed to start server:", err);
        });
        this.serverProcess.on("close", (code) => {
            console.log(`Server process exited with code ${code}`);
            this.serverProcess = null;
        });
    }
    /**
     * Stop the Uvicorn FastAPI server.
     */
    stop() {
        if (!this.serverProcess) {
            console.log("No server is running.");
            return;
        }
        console.log("Stopping FastAPI server...");
        this.serverProcess.kill("SIGINT"); // Gracefully stop the server
        this.serverProcess = null;
    }
}
exports.FastAPIServer = FastAPIServer;
// Example usage
// const server = new FastAPIServer();
// // Start the server
// server.start("main:app", 8000);
// // Stop the server after 10 seconds
// setTimeout(() => {
//     server.stop();
// }, 10000);
//# sourceMappingURL=uvicorn_server.js.map