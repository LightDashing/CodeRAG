// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as path from "path";
import * as fs from 'fs';
import { FastAPIServer } from './uvicorn_server'
import { getWebviewContent, getRepoManagementWebviewContent,
        getConfigManagerWebviewContent
        } from './webviews'
import { saveSettingsToConfigFile } from './utils'
import axios from "axios";

const server = new FastAPIServer();
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

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
		console.log("Check!")
		server.start('app:app')
	})
	vscode.commands.registerCommand('coderag.stopServer', () => {
		server.stop()
	})

	context.subscriptions.push(
        vscode.commands.registerCommand("coderag.openChat", () => {
            const panel = vscode.window.createWebviewPanel(
                "coderagChat",
                "AI Chat",
                vscode.ViewColumn.One,
                { enableScripts: true } // Allow JavaScript in the webview
            );

            panel.webview.html = getWebviewContent();

            // Handle messages from the webview
            panel.webview.onDidReceiveMessage(async (message) => {
                if (message.command === "askAI") {
                    // Handle AI Chat
                    try {
                        const response = await axios.get("http://127.0.0.1:8000/generate", {
                            params: { user_input: message.userInput },
                        });
            
                        if (response.data.success) {
                            panel.webview.postMessage({
                                command: "aiResponse",
                                answer: response.data.generated.answer,
                            });
                        } else {
                            panel.webview.postMessage({
                                command: "error",
                                message: "Failed to generate a response.",
                            });
                        }
                    } catch (error) {
                        panel.webview.postMessage({
                            command: "error",
                            message: "Error connecting to AI server.",
                        });
                    }
                } else if (message.command === "addRepo") {
                    // Handle Add Repository
                    try {
                        const response = await axios.post("http://127.0.0.1:8000/add_repo", {
                            repo_path: message.repoPath,
                            repo_name: message.repoName,
                            auto_pull: message.autoPull,
                        });
            
                        if (response.data.success) {
                            vscode.window.showInformationMessage("Repository added successfully!");
                        } else {
                            vscode.window.showErrorMessage("Failed to add repository.");
                        }
                    } catch (error) {
                        vscode.window.showErrorMessage("Error adding repository.");
                    }
                } else if (message.command === "deleteRepo") {
                    // Handle Delete Repository
                    try {
                        const response = await axios.delete("http://127.0.0.1:8000/remove_repo", {
                            params: {
                                repo_path: message.repoPath,
                                repo_name: message.repoName || undefined,
                            },
                        });
            
                        if (response.data.success) {
                            vscode.window.showInformationMessage("Repository deleted successfully!");
                        } else {
                            vscode.window.showErrorMessage("Failed to delete repository.");
                        }
                    } catch (error) {
                        vscode.window.showErrorMessage("Error deleting repository.");
                    }
                }
            });
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("coderag.manageRepos", () => {
            const panel = vscode.window.createWebviewPanel(
                "repoManagement",
                "Repository Management",
                vscode.ViewColumn.One,
                { enableScripts: true }
            );
    
            panel.webview.html = getRepoManagementWebviewContent();
    
            // Handle messages from the repository management webview
            panel.webview.onDidReceiveMessage(async (message) => {
                if (message.command === "addRepo") {
                    try {
                        const response = await axios.post("http://127.0.0.1:8000/add_repo", {
                            repo_path: message.repoPath,
                            repo_name: message.repoName,
                            auto_pull: message.autoPull,
                        });
    
                        if (response.data.success) {
                            vscode.window.showInformationMessage("Repository added successfully!");
                        } else {
                            vscode.window.showErrorMessage("Failed to add repository.");
                        }
                    } catch (error) {
                        vscode.window.showErrorMessage("Error adding repository.");
                    }
                } else if (message.command === "deleteRepo") {
                    try {
                        const response = await axios.delete("http://127.0.0.1:8000/remove_repo", {
                            params: {
                                repo_path: message.repoPath,
                                repo_name: message.repoName || undefined,
                                remove_folder: message.removeFolder,
                            },
                        });
    
                        if (response.data.success) {
                            vscode.window.showInformationMessage("Repository deleted successfully!");
                        } else {
                            vscode.window.showErrorMessage("Failed to delete repository.");
                        }
                    } catch (error) {
                        vscode.window.showErrorMessage("Error deleting repository.");
                    }
                }
            });
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("coderag.openConfigManager", () => {
            const panel = vscode.window.createWebviewPanel(
                "configManager",
                "Configuration Manager",
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            // Pass extensionPath to the webview function
            panel.webview.html = getConfigManagerWebviewContent(context.extensionPath);

            panel.webview.onDidReceiveMessage(async (message) => {
                if (message.command === "saveConfig") {
                    try {
                        const configPath = path.join(context.extensionPath, "..", "..", "config.json");
                        fs.writeFileSync(configPath, JSON.stringify(message.config, null, 2));
                        vscode.window.showInformationMessage("Configuration saved successfully!");
                    } catch (error) {
                        vscode.window.showErrorMessage("Error saving configuration.");
                    }
                }
            });
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("coderag.saveSettings", () => {
            saveSettingsToConfigFile(context.extensionPath);
        })
    );

    vscode.workspace.onDidChangeConfiguration((event) => {
        if (event.affectsConfiguration("coderag")) {
            saveSettingsToConfigFile(context.extensionPath);
        }
    });
    
	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
