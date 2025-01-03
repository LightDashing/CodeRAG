import { spawn, ChildProcess } from "child_process";
import * as path from "path";

const pythonPath = path.resolve(__dirname, "../../../coderag/bin/python");
// You should be sure that all requirements are installed in venv/conda/poetry environment and the path is right

export class FastAPIServer {
    private serverProcess: ChildProcess | null = null;

    /**
     * Start the Uvicorn FastAPI server.
     * @param scriptPath Path to the FastAPI app (e.g., "main:app").
     * @param port Port to run the server on.
     */
    start(scriptPath: string, port: number = 8000): void {
        if (this.serverProcess) {
            console.log("Server is already running.");
            return;
        }

        console.log(`Starting FastAPI server on port ${port}...`);
        this.serverProcess = spawn(pythonPath, ["-m", "uvicorn", scriptPath, `--port=${port}`], {
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
    stop(): void {
        if (!this.serverProcess) {
            console.log("No server is running.");
            return;
        }

        console.log("Stopping FastAPI server...");
        this.serverProcess.kill("SIGINT"); // Gracefully stop the server
        this.serverProcess = null;
    }
}

// Example usage
// const server = new FastAPIServer();

// // Start the server
// server.start("main:app", 8000);

// // Stop the server after 10 seconds
// setTimeout(() => {
//     server.stop();
// }, 10000);
