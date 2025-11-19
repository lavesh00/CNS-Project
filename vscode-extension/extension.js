/**
 * Agent Lucky VS Code Extension
 * Connects VS Code to the Agent Lucky backend
 */

const vscode = require('vscode');
const axios = require('axios');

let statusBarItem;
let agentPanel;

/**
 * Extension activation
 */
function activate(context) {
    console.log('Agent Lucky extension is now active!');

    // Get backend URL from settings
    const config = vscode.workspace.getConfiguration('agentLucky');
    const backendUrl = config.get('backendUrl', 'http://127.0.0.1:7777');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = '$(loading~spin) Agent Lucky: Connecting...';
    statusBarItem.command = 'agent-lucky.checkStatus';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Check backend status
    checkBackendStatus(backendUrl);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('agent-lucky.startAgent', () => startAgent(backendUrl))
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('agent-lucky.showPanel', () => showAgentPanel(context, backendUrl))
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('agent-lucky.checkStatus', () => checkBackendStatus(backendUrl))
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('agent-lucky.listModels', () => listModels(backendUrl))
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('agent-lucky.downloadModel', () => downloadModel(backendUrl))
    );

    // Auto-check status every 30 seconds
    setInterval(() => {
        checkBackendStatus(backendUrl, true);
    }, 30000);

    vscode.window.showInformationMessage('Agent Lucky activated! Backend: ' + backendUrl);
}

/**
 * Check backend status
 */
async function checkBackendStatus(backendUrl, silent = false) {
    try {
        const response = await axios.get(`${backendUrl}/health`, { timeout: 5000 });
        
        if (response.data.status === 'healthy') {
            statusBarItem.text = '$(check) Agent Lucky: Ready';
            statusBarItem.backgroundColor = undefined;
            
            if (!silent) {
                vscode.window.showInformationMessage('✅ Agent Lucky backend is healthy!');
            }
        }
    } catch (error) {
        statusBarItem.text = '$(error) Agent Lucky: Offline';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        
        if (!silent) {
            vscode.window.showErrorMessage('Agent Lucky backend is not running. Start it with: py backend/main.py');
        }
    }
}

/**
 * Start agent with prompt
 */
async function startAgent(backendUrl) {
    const prompt = await vscode.window.showInputBox({
        prompt: 'What do you want Agent Lucky to do?',
        placeHolder: 'e.g., Create a REST API with authentication',
        ignoreFocusOut: true
    });

    if (!prompt) {
        return;
    }

    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
    
    if (!workspacePath) {
        vscode.window.showErrorMessage('Please open a workspace folder first');
        return;
    }

    try {
        statusBarItem.text = '$(loading~spin) Agent Lucky: Working...';
        
        const response = await axios.post(`${backendUrl}/agent/start`, {
            prompt: prompt,
            workspace_path: workspacePath
        });

        vscode.window.showInformationMessage(
            `✅ Agent started! Task ID: ${response.data.task_id}`
        );

        statusBarItem.text = '$(sync~spin) Agent Lucky: Processing';

        // Show output channel
        const outputChannel = vscode.window.createOutputChannel('Agent Lucky');
        outputChannel.appendLine(`[Agent Lucky] Task started`);
        outputChannel.appendLine(`Prompt: ${prompt}`);
        outputChannel.appendLine(`Workspace: ${workspacePath}`);
        outputChannel.appendLine(`Task ID: ${response.data.task_id}`);
        outputChannel.show();

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to start agent: ${error.message}`);
        statusBarItem.text = '$(error) Agent Lucky: Error';
    }
}

/**
 * Show agent panel with webview
 */
function showAgentPanel(context, backendUrl) {
    if (agentPanel) {
        agentPanel.reveal();
        return;
    }

    agentPanel = vscode.window.createWebviewPanel(
        'agentLuckyPanel',
        'Agent Lucky',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    agentPanel.webview.html = getWebviewContent(backendUrl);

    // Handle messages from webview
    agentPanel.webview.onDidReceiveMessage(
        async message => {
            switch (message.command) {
                case 'startAgent':
                    await handleStartAgentFromWebview(message.prompt, backendUrl);
                    break;
                case 'checkStatus':
                    await handleCheckStatusFromWebview(agentPanel.webview, backendUrl);
                    break;
            }
        },
        undefined,
        context.subscriptions
    );

    agentPanel.onDidDispose(() => {
        agentPanel = undefined;
    });
}

/**
 * Handle start agent from webview
 */
async function handleStartAgentFromWebview(prompt, backendUrl) {
    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
    
    if (!workspacePath) {
        vscode.window.showErrorMessage('Please open a workspace folder first');
        return;
    }

    try {
        const response = await axios.post(`${backendUrl}/agent/start`, {
            prompt: prompt,
            workspace_path: workspacePath
        });

        agentPanel.webview.postMessage({
            command: 'agentStarted',
            data: response.data
        });

        vscode.window.showInformationMessage('✅ Agent task started!');
    } catch (error) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

/**
 * Handle check status from webview
 */
async function handleCheckStatusFromWebview(webview, backendUrl) {
    try {
        const response = await axios.get(`${backendUrl}/status`);
        
        webview.postMessage({
            command: 'statusUpdate',
            data: response.data
        });
    } catch (error) {
        webview.postMessage({
            command: 'statusUpdate',
            data: { error: error.message }
        });
    }
}

/**
 * List available models
 */
async function listModels(backendUrl) {
    try {
        const response = await axios.get(`${backendUrl}/models/list`);
        const models = response.data;

        const items = models.available.map(model => ({
            label: model.name,
            description: `${model.size} - ${model.context_length} tokens`,
            detail: model.description || '',
            model: model
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a model to download',
            ignoreFocusOut: true
        });

        if (selected) {
            const confirm = await vscode.window.showInformationMessage(
                `Download ${selected.label}?`,
                'Yes', 'No'
            );

            if (confirm === 'Yes') {
                downloadModelById(backendUrl, selected.model.id);
            }
        }

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to list models: ${error.message}`);
    }
}

/**
 * Download a model
 */
async function downloadModel(backendUrl) {
    const modelId = await vscode.window.showInputBox({
        prompt: 'Enter model ID',
        placeHolder: 'e.g., codellama-13b-q4',
        ignoreFocusOut: true
    });

    if (modelId) {
        downloadModelById(backendUrl, modelId);
    }
}

/**
 * Download model by ID
 */
async function downloadModelById(backendUrl, modelId) {
    try {
        vscode.window.showInformationMessage(`Starting download: ${modelId}...`);

        const response = await axios.post(`${backendUrl}/models/download`, {
            model_id: modelId
        });

        if (response.data.status === 'already_downloading') {
            vscode.window.showWarningMessage(`${modelId} is already being downloaded`);
            return;
        }

        vscode.window.showInformationMessage(
            `✅ Download started: ${modelId}`
        );

        // Start polling for progress
        const progressInterval = setInterval(async () => {
            try {
                const statusResponse = await axios.get(`${backendUrl}/models/status/${modelId}`);
                const status = statusResponse.data;
                
                statusBarItem.text = `$(sync~spin) Agent Lucky: Downloading ${modelId} (${status.progress}%)`;
                
                if (status.status === 'completed') {
                    clearInterval(progressInterval);
                    statusBarItem.text = '$(check) Agent Lucky: Ready';
                    vscode.window.showInformationMessage(
                        `✅ ${modelId} downloaded successfully!`
                    );
                } else if (status.status === 'error') {
                    clearInterval(progressInterval);
                    statusBarItem.text = '$(error) Agent Lucky: Download Failed';
                    vscode.window.showErrorMessage(
                        `❌ Download failed: ${status.message}`
                    );
                }
            } catch (err) {
                clearInterval(progressInterval);
                logger.error('Error checking download status:', err);
            }
        }, 2000); // Check every 2 seconds

    } catch (error) {
        vscode.window.showErrorMessage(`Failed to start download: ${error.message}`);
    }
}

/**
 * Get webview HTML content
 */
function getWebviewContent(backendUrl) {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agent Lucky</title>
        <style>
            body {
                padding: 20px;
                color: var(--vscode-foreground);
                font-family: var(--vscode-font-family);
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: var(--vscode-editor-foreground);
                margin-bottom: 20px;
            }
            .input-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            textarea {
                width: 100%;
                min-height: 100px;
                background: var(--vscode-input-background);
                color: var(--vscode-input-foreground);
                border: 1px solid var(--vscode-input-border);
                padding: 10px;
                font-family: var(--vscode-editor-font-family);
                font-size: 14px;
                resize: vertical;
            }
            button {
                background: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 14px;
                margin-right: 10px;
            }
            button:hover {
                background: var(--vscode-button-hoverBackground);
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                background: var(--vscode-editor-background);
                border-left: 3px solid var(--vscode-button-background);
            }
            .status-item {
                margin: 5px 0;
            }
            .logo {
                font-size: 48px;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🍀</div>
            <h1>Agent Lucky</h1>
            <p>Agentic AI coding assistant powered by local models</p>

            <div class="input-group">
                <label for="prompt">What do you want to create?</label>
                <textarea id="prompt" placeholder="e.g., Create a REST API with user authentication and JWT tokens"></textarea>
            </div>

            <button onclick="startAgent()">🚀 Start Agent</button>
            <button onclick="checkStatus()">📊 Check Status</button>

            <div class="status" id="status">
                <div class="status-item"><strong>Backend:</strong> <span id="backend-status">Checking...</span></div>
                <div class="status-item"><strong>Models:</strong> <span id="models-status">-</span></div>
                <div class="status-item"><strong>Agent:</strong> <span id="agent-status">Idle</span></div>
                <div class="status-item" id="download-status-container" style="display: none;">
                    <strong>Download:</strong> <span id="download-status">-</span>
                    <div style="background: var(--vscode-input-background); height: 20px; margin-top: 5px; border-radius: 3px; overflow: hidden;">
                        <div id="progress-bar" style="background: var(--vscode-button-background); height: 100%; width: 0%; transition: width 0.3s;"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const vscode = acquireVsCodeApi();
            const backendUrl = '${backendUrl}';
            let downloadCheckInterval = null;

            function startAgent() {
                const prompt = document.getElementById('prompt').value;
                if (!prompt) {
                    alert('Please enter a prompt');
                    return;
                }

                vscode.postMessage({
                    command: 'startAgent',
                    prompt: prompt
                });

                document.getElementById('agent-status').textContent = 'Starting...';
            }

            function checkStatus() {
                vscode.postMessage({
                    command: 'checkStatus'
                });
                checkDownloads();
            }

            async function checkDownloads() {
                try {
                    const response = await fetch(backendUrl + '/models/downloads');
                    const data = await response.json();
                    
                    if (data.downloads && Object.keys(data.downloads).length > 0) {
                        const downloadContainer = document.getElementById('download-status-container');
                        downloadContainer.style.display = 'block';
                        
                        // Show first active download
                        const modelId = Object.keys(data.downloads)[0];
                        const download = data.downloads[modelId];
                        
                        document.getElementById('download-status').textContent = 
                            modelId + ': ' + download.message;
                        document.getElementById('progress-bar').style.width = download.progress + '%';
                        
                        // Clear completed/error downloads after 5 seconds
                        if (download.status === 'completed' || download.status === 'error') {
                            setTimeout(() => {
                                downloadContainer.style.display = 'none';
                            }, 5000);
                        }
                    } else {
                        document.getElementById('download-status-container').style.display = 'none';
                    }
                } catch (error) {
                    console.error('Failed to check downloads:', error);
                }
            }

            // Handle messages from extension
            window.addEventListener('message', event => {
                const message = event.data;
                
                switch (message.command) {
                    case 'agentStarted':
                        document.getElementById('agent-status').textContent = 
                            'Running - Task ID: ' + message.data.task_id;
                        break;
                    
                    case 'statusUpdate':
                        if (message.data.error) {
                            document.getElementById('backend-status').textContent = 'Offline';
                        } else {
                            document.getElementById('backend-status').textContent = 
                                message.data.backend || 'Unknown';
                            document.getElementById('models-status').textContent = 
                                (message.data.models?.installed_count || 0) + ' installed';
                        }
                        break;
                }
            });

            // Check status on load and every 3 seconds
            setTimeout(checkStatus, 1000);
            setInterval(checkDownloads, 3000);
        </script>
    </body>
    </html>`;
}

/**
 * Extension deactivation
 */
function deactivate() {
    console.log('Agent Lucky extension deactivated');
}

module.exports = {
    activate,
    deactivate
};

