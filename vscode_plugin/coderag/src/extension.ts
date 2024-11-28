// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { FastAPIServer } from './uvicorn_server'
import { getWebviewContent } from './webviews'
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
                    try {
                        const response = await axios.get("http://127.0.0.1:8000/generate", {
                            params: { user_input: message.userInput },
                        });

                        if (response.data.success) {
                            panel.webview.postMessage({
                                command: "aiResponse",
                                answer: response.data.generated.answer,
                                question: response.data.generated.question,
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
                }
            });
        })
    );

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
