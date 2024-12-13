import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

interface Config {
    indexing?: {
        doc_splitting?: Array<{
            name: string;
            module: string;
            params?: { [key: string]: any };
        }>;
        doc_embedd?: {
            model_name?: string;
        };
    };
    generation?: {
        model?: {
            llm_model?: {
                name?: string;
            };
        };
        llm_pipeline?: {
            QA_prompt?: string;
        };
    };
}

/**
 * Save VS Code settings to the config.json file by updating specific sections.
 * @param extensionPath - The root path of the extension.
 */
export function saveSettingsToConfigFile(extensionPath: string) {
    // Get settings from VS Code configuration
    const config = vscode.workspace.getConfiguration("coderag");

    // Path to the root-level config.json
    const configPath = path.join(extensionPath, "..", "..", "config.json");

    try {
        // Load the existing config.json file
        let existingConfig: Config = {};
        if (fs.existsSync(configPath)) {
            const rawData = fs.readFileSync(configPath, "utf-8");
            existingConfig = JSON.parse(rawData) as Config;
        }

        // Update specific sections with new settings
        const updatedConfig: Config = {
            ...existingConfig,
            indexing: {
                ...existingConfig.indexing,
                doc_splitting: config.get("indexing.docSplitting") || existingConfig.indexing?.doc_splitting,
                doc_embedd: {
                    ...existingConfig.indexing?.doc_embedd,
                    model_name: config.get("indexing.embeddingModel") || existingConfig.indexing?.doc_embedd?.model_name,
                },
            },
            generation: {
                ...existingConfig.generation,
                model: {
                    ...existingConfig.generation?.model,
                    llm_model: {
                        ...existingConfig.generation?.model?.llm_model,
                        name: config.get("generation.modelName") || existingConfig.generation?.model?.llm_model?.name,
                    },
                },
                llm_pipeline: {
                    ...existingConfig.generation?.llm_pipeline,
                    QA_prompt: config.get("generation.QA_prompt") || existingConfig.generation?.llm_pipeline?.QA_prompt,
                },
            },
        };

        // Write the updated configuration back to the file
        fs.writeFileSync(configPath, JSON.stringify(updatedConfig, null, 2));
        vscode.window.showInformationMessage("Settings saved to config.json successfully!");
    } catch (error) {
        vscode.window.showErrorMessage("Error saving settings to config.json.");
        console.error("Error:", error);
    }
}
