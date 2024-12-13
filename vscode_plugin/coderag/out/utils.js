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
exports.saveSettingsToConfigFile = saveSettingsToConfigFile;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const vscode = __importStar(require("vscode"));
/**
 * Save VS Code settings to the config.json file by updating specific sections.
 * @param extensionPath - The root path of the extension.
 */
function saveSettingsToConfigFile(extensionPath) {
    // Get settings from VS Code configuration
    const config = vscode.workspace.getConfiguration("coderag");
    // Path to the root-level config.json
    const configPath = path.join(extensionPath, "..", "..", "config.json");
    try {
        // Load the existing config.json file
        let existingConfig = {};
        if (fs.existsSync(configPath)) {
            const rawData = fs.readFileSync(configPath, "utf-8");
            existingConfig = JSON.parse(rawData);
        }
        // Update specific sections with new settings
        const updatedConfig = {
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
    }
    catch (error) {
        vscode.window.showErrorMessage("Error saving settings to config.json.");
        console.error("Error:", error);
    }
}
//# sourceMappingURL=utils.js.map