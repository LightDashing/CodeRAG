"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getWebviewContent = getWebviewContent;
function getWebviewContent() {
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
            </style>
        </head>
        <body>
            <h1>AI Chat</h1>
            <div id="chat-container"></div>
            <p id="loading-indicator">Generating response...</p>
            <input type="text" id="user-input" placeholder="Ask something..." style="width: 80%;" />
            <button id="send-button">Send</button>
            <script>
                const vscode = acquireVsCodeApi();

                // Restore state if it exists
                const state = vscode.getState();
                if (state?.chatHistory) {
                    state.chatHistory.forEach((msg) => addMessage(msg.sender, msg.text, msg.type));
                }

                // Add message to chat and save state
                function addMessage(sender, text, type) {
                    const chatContainer = document.getElementById("chat-container");
                    const messageDiv = document.createElement("div");
                    messageDiv.className = "message " + type;
                    messageDiv.textContent = \`\${sender}: \${text}\`;
                    chatContainer.appendChild(messageDiv);
                    chatContainer.scrollTop = chatContainer.scrollHeight;

                    // Update state
                    const currentState = vscode.getState() || { chatHistory: [] };
                    currentState.chatHistory.push({ sender, text, type });
                    vscode.setState(currentState);
                }

                // Show loading indicator
                function showLoading() {
                    document.getElementById("loading-indicator").style.display = "block";
                }

                // Hide loading indicator
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
//# sourceMappingURL=webviews.js.map