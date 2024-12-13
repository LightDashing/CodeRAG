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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const uvicorn_server_1 = require("./uvicorn_server");
const webviews_1 = require("./webviews");
const utils_1 = require("./utils");
const axios_1 = __importDefault(require("axios"));
const server = new uvicorn_server_1.FastAPIServer();
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "coderag" is now active!');
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    const disposable = vscode.commands.registerCommand('coderag.helloWorld', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage('Hello World from CodeRag!');
    });
    vscode.commands.registerCommand('coderag.startServer', () => {
        console.log("Check!");
        server.start('app:app');
    });
    vscode.commands.registerCommand('coderag.stopServer', () => {
        server.stop();
    });
    context.subscriptions.push(vscode.commands.registerCommand("coderag.openChat", () => {
        const panel = vscode.window.createWebviewPanel("coderagChat", "AI Chat", vscode.ViewColumn.One, { enableScripts: true } // Allow JavaScript in the webview
        );
        panel.webview.html = (0, webviews_1.getWebviewContent)();
        // Handle messages from the webview
        panel.webview.onDidReceiveMessage(async (message) => {
            if (message.command === "askAI") {
                // Handle AI Chat
                try {
                    const response = await axios_1.default.get("http://127.0.0.1:8000/generate", {
                        params: { user_input: message.userInput },
                    });
                    if (response.data.success) {
                        panel.webview.postMessage({
                            command: "aiResponse",
                            answer: response.data.generated.answer,
                        });
                    }
                    else {
                        panel.webview.postMessage({
                            command: "error",
                            message: "Failed to generate a response.",
                        });
                    }
                }
                catch (error) {
                    panel.webview.postMessage({
                        command: "error",
                        message: "Error connecting to AI server.",
                    });
                }
            }
            else if (message.command === "addRepo") {
                // Handle Add Repository
                try {
                    const response = await axios_1.default.post("http://127.0.0.1:8000/add_repo", {
                        repo_path: message.repoPath,
                        repo_name: message.repoName,
                        auto_pull: message.autoPull,
                    });
                    if (response.data.success) {
                        vscode.window.showInformationMessage("Repository added successfully!");
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to add repository.");
                    }
                }
                catch (error) {
                    vscode.window.showErrorMessage("Error adding repository.");
                }
            }
            else if (message.command === "deleteRepo") {
                // Handle Delete Repository
                try {
                    const response = await axios_1.default.delete("http://127.0.0.1:8000/remove_repo", {
                        params: {
                            repo_path: message.repoPath,
                            repo_name: message.repoName || undefined,
                        },
                    });
                    if (response.data.success) {
                        vscode.window.showInformationMessage("Repository deleted successfully!");
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to delete repository.");
                    }
                }
                catch (error) {
                    vscode.window.showErrorMessage("Error deleting repository.");
                }
            }
        });
    }));
    context.subscriptions.push(vscode.commands.registerCommand("coderag.manageRepos", () => {
        const panel = vscode.window.createWebviewPanel("repoManagement", "Repository Management", vscode.ViewColumn.One, { enableScripts: true });
        panel.webview.html = (0, webviews_1.getRepoManagementWebviewContent)();
        // Handle messages from the repository management webview
        panel.webview.onDidReceiveMessage(async (message) => {
            if (message.command === "addRepo") {
                try {
                    const response = await axios_1.default.post("http://127.0.0.1:8000/add_repo", {
                        repo_path: message.repoPath,
                        repo_name: message.repoName,
                        auto_pull: message.autoPull,
                    });
                    if (response.data.success) {
                        vscode.window.showInformationMessage("Repository added successfully!");
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to add repository.");
                    }
                }
                catch (error) {
                    vscode.window.showErrorMessage("Error adding repository.");
                }
            }
            else if (message.command === "deleteRepo") {
                try {
                    const response = await axios_1.default.delete("http://127.0.0.1:8000/remove_repo", {
                        params: {
                            repo_path: message.repoPath,
                            repo_name: message.repoName || undefined,
                            remove_folder: message.removeFolder,
                        },
                    });
                    if (response.data.success) {
                        vscode.window.showInformationMessage("Repository deleted successfully!");
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to delete repository.");
                    }
                }
                catch (error) {
                    vscode.window.showErrorMessage("Error deleting repository.");
                }
            }
        });
    }));
    context.subscriptions.push(vscode.commands.registerCommand("coderag.openConfigManager", () => {
        const panel = vscode.window.createWebviewPanel("configManager", "Configuration Manager", vscode.ViewColumn.One, { enableScripts: true });
        // Pass extensionPath to the webview function
        panel.webview.html = (0, webviews_1.getConfigManagerWebviewContent)(context.extensionPath);
        panel.webview.onDidReceiveMessage(async (message) => {
            if (message.command === "saveConfig") {
                try {
                    const configPath = path.join(context.extensionPath, "..", "..", "config.json");
                    fs.writeFileSync(configPath, JSON.stringify(message.config, null, 2));
                    vscode.window.showInformationMessage("Configuration saved successfully!");
                }
                catch (error) {
                    vscode.window.showErrorMessage("Error saving configuration.");
                }
            }
        });
    }));
    context.subscriptions.push(vscode.commands.registerCommand("coderag.saveSettings", () => {
        (0, utils_1.saveSettingsToConfigFile)(context.extensionPath);
    }));
    vscode.workspace.onDidChangeConfiguration((event) => {
        if (event.affectsConfiguration("coderag")) {
            (0, utils_1.saveSettingsToConfigFile)(context.extensionPath);
        }
    });
    context.subscriptions.push(disposable);
}
// This method is called when your extension is deactivated
function deactivate() { }
//# sourceMappingURL=extension.js.map