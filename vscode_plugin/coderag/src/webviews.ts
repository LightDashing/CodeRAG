import * as path from "path";
import * as fs from 'fs';

export function getWebviewContent(): string {
    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Chat</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 10px; }
                #chat-container { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }
                .message { margin-bottom: 10px; }
                .question { color: blue; }
                .answer { color: green; }
                .error { color: red; }
                #loading-indicator { display: none; font-style: italic; color: gray; }
                .repo-section { margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>AI Chat</h1>
            <div id="chat-container"></div>
            <p id="loading-indicator">Generating response...</p>
            <input type="text" id="user-input" placeholder="Ask something..." style="width: 80%;" />
            <button id="send-button">Send</button>
            
            <div class="repo-section">
                <h2>Repository Management</h2>
                <h3>Add Repository</h3>
                <input type="text" id="repo-path" placeholder="Repository Path" style="width: 60%;" />
                <input type="text" id="repo-name" placeholder="Repository Name" style="width: 30%;" />
                <label><input type="checkbox" id="auto-pull" /> Auto Pull</label>
                <button id="add-repo-button">Add Repository</button>
                
                <h3>Delete Repository</h3>
                <input type="text" id="delete-repo-path" placeholder="Repository Path" style="width: 60%;" />
                <input type="text" id="delete-repo-name" placeholder="Repository Name (optional)" style="width: 30%;" />
                <button id="delete-repo-button">Delete Repository</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();

                // Chat functionality
                const state = vscode.getState();
                if (state?.chatHistory) {
                    state.chatHistory.forEach((msg) => addMessage(msg.sender, msg.text, msg.type));
                }

                function addMessage(sender, text, type) {
                    const chatContainer = document.getElementById("chat-container");
                    const messageDiv = document.createElement("div");
                    messageDiv.className = "message " + type;
                    messageDiv.textContent = \`\${sender}: \${text}\`;
                    chatContainer.appendChild(messageDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;

                    const currentState = vscode.getState() || { chatHistory: [] };
                    currentState.chatHistory.push({ sender, text, type });
                    vscode.setState(currentState);
                }

                function showLoading() {
                    document.getElementById("loading-indicator").style.display = "block";
                }

                function hideLoading() {
                    document.getElementById("loading-indicator").style.display = "none";
                }

                document.getElementById("send-button").addEventListener("click", () => {
                    const userInput = document.getElementById("user-input").value;
                    if (userInput.trim()) {
                        addMessage("You", userInput, "question");
                        vscode.postMessage({ command: "askAI", userInput });
                        document.getElementById("user-input").value = "";
                        showLoading();
                    }
                });

                // Add Repository
                document.getElementById("add-repo-button").addEventListener("click", () => {
                    const repoPath = document.getElementById("repo-path").value;
                    const repoName = document.getElementById("repo-name").value;
                    const autoPull = document.getElementById("auto-pull").checked;

                    if (repoPath && repoName) {
                        vscode.postMessage({
                            command: "addRepo",
                            repoPath,
                            repoName,
                            autoPull,
                        });
                    } else {
                        alert("Please provide both repository path and name.");
                    }
                });

                // Delete Repository
                document.getElementById("delete-repo-button").addEventListener("click", () => {
                    const repoPath = document.getElementById("delete-repo-path").value;
                    const repoName = document.getElementById("delete-repo-name").value;

                    if (repoPath) {
                        vscode.postMessage({
                            command: "deleteRepo",
                            repoPath,
                            repoName,
                        });
                    } else {
                        alert("Please provide the repository path.");
                    }
                });

                window.addEventListener("message", (event) => {
                    const message = event.data;
                    if (message.command === "aiResponse") {
                        addMessage("AI", message.answer, "answer");
                        hideLoading();
                    } else if (message.command === "error") {
                        addMessage("Error", message.message, "error");
                        hideLoading();
                    }
                });
            </script>
        </body>
        </html>
    `;
}

export function getRepoManagementWebviewContent(): string {
    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Repository Management</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 10px; }
                .section { margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>Repository Management</h1>
            <div class="section">
                <h2>Add Repository</h2>
                <input type="text" id="repo-path" placeholder="Repository Path" style="width: 60%;" />
                <input type="text" id="repo-name" placeholder="Repository Name" style="width: 30%;" />
                <label><input type="checkbox" id="auto-pull" /> Auto Pull</label>
                <button id="add-repo-button">Add Repository</button>
            </div>
            <div class="section">
                <h2>Delete Repository</h2>
                <input type="text" id="delete-repo-path" placeholder="Repository Path" style="width: 60%;" />
                <input type="text" id="delete-repo-name" placeholder="Repository Name (optional)" style="width: 30%;" />
                <label><input type="checkbox" id="remove-folder" /> Remove Folder</label>
                <button id="delete-repo-button">Delete Repository</button>
            </div>
            <script>
                const vscode = acquireVsCodeApi();

                // Add Repository
                document.getElementById("add-repo-button").addEventListener("click", () => {
                    const repoPath = document.getElementById("repo-path").value;
                    const repoName = document.getElementById("repo-name").value;
                    const autoPull = document.getElementById("auto-pull").checked;

                    if (repoPath && repoName) {
                        vscode.postMessage({
                            command: "addRepo",
                            repoPath,
                            repoName,
                            autoPull,
                        });
                    } else {
                        alert("Please provide both repository path and name.");
                    }
                });

                // Delete Repository
                document.getElementById("delete-repo-button").addEventListener("click", () => {
                    const repoPath = document.getElementById("delete-repo-path").value;
                    const repoName = document.getElementById("delete-repo-name").value;
                    const removeFolder = document.getElementById("remove-folder").checked;

                    if (repoPath) {
                        vscode.postMessage({
                            command: "deleteRepo",
                            repoPath,
                            repoName,
                            removeFolder,
                        });
                    } else {
                        alert("Please provide the repository path.");
                    }
                });
            </script>
        </body>
        </html>
    `;
}

export function getConfigManagerWebviewContent(extensionPath: string): string {
    const configPath = path.join(extensionPath, "..", "..", "config.json");

    // Read the config.json file
    let initialConfig = "";
    try {
        initialConfig = fs.readFileSync(configPath, "utf-8");
    } catch (error) {
        console.error("Error reading config.json:", error);
        initialConfig = "{}"; // Fallback to an empty config if the file doesn't exist
    }

    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Configuration Manager</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 10px; }
                textarea { width: 100%; height: 300px; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <h1>Configuration Manager</h1>
            <textarea id="config-editor">${initialConfig}</textarea>
            <button id="save-button">Save Configuration</button>
            <script>
                const vscode = acquireVsCodeApi();

                document.getElementById("save-button").addEventListener("click", () => {
                    const config = JSON.parse(document.getElementById("config-editor").value);
                    vscode.postMessage({ command: "saveConfig", config });
                });
            </script>
        </body>
        </html>
    `;
}
