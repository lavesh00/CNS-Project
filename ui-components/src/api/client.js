/**
 * Agent Lucky API Client
 * Communicates with the FastAPI backend
 */

const API_BASE = 'http://127.0.0.1:7777';

class AgentLuckyClient {
  constructor(baseURL = API_BASE) {
    this.baseURL = baseURL;
    this.ws = null;
  }

  /**
   * Health check
   */
  async health() {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }

  /**
   * Get backend status
   */
  async getStatus() {
    const response = await fetch(`${this.baseURL}/status`);
    return response.json();
  }

  /**
   * Start agent task
   */
  async startAgent(prompt, workspacePath, context = {}) {
    const response = await fetch(`${this.baseURL}/agent/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        workspace_path: workspacePath,
        context,
      }),
    });
    return response.json();
  }

  /**
   * Stop agent task
   */
  async stopAgent(taskId) {
    const response = await fetch(`${this.baseURL}/agent/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ task_id: taskId }),
    });
    return response.json();
  }

  /**
   * Get agent status
   */
  async getAgentStatus() {
    const response = await fetch(`${this.baseURL}/agent/status`);
    return response.json();
  }

  /**
   * Get current plan
   */
  async getCurrentPlan() {
    const response = await fetch(`${this.baseURL}/agent/plan/current`);
    return response.json();
  }

  /**
   * List available models
   */
  async listModels() {
    const response = await fetch(`${this.baseURL}/models/list`);
    return response.json();
  }

  /**
   * Download model
   */
  async downloadModel(modelId, quantization = 'Q4_K_M') {
    const response = await fetch(`${this.baseURL}/models/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model_id: modelId,
        quantization,
      }),
    });
    return response.json();
  }

  /**
   * Get model download status
   */
  async getModelStatus(modelId) {
    const response = await fetch(`${this.baseURL}/models/status/${modelId}`);
    return response.json();
  }

  /**
   * Delete model
   */
  async deleteModel(modelId) {
    const response = await fetch(`${this.baseURL}/models/${modelId}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  /**
   * Start web scraping
   */
  async startScraping(url, options = {}) {
    const response = await fetch(`${this.baseURL}/scraper/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url,
        ...options,
      }),
    });
    return response.json();
  }

  /**
   * Get scraper status
   */
  async getScraperStatus(scrapeId) {
    const response = await fetch(`${this.baseURL}/scraper/status/${scrapeId}`);
    return response.json();
  }

  /**
   * Create GitHub repository
   */
  async createGitHubRepo(name, description, isPrivate = false) {
    const response = await fetch(`${this.baseURL}/github/create-repo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        description,
        private: isPrivate,
      }),
    });
    return response.json();
  }

  /**
   * Push to GitHub
   */
  async pushToGitHub(branch = 'main', commitMessage = null) {
    const response = await fetch(`${this.baseURL}/github/push`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        branch,
        commit_message: commitMessage,
      }),
    });
    return response.json();
  }

  /**
   * Create pull request
   */
  async createPullRequest(title, description, baseBranch, headBranch) {
    const response = await fetch(`${this.baseURL}/github/create-pr`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title,
        description,
        base_branch: baseBranch,
        head_branch: headBranch,
      }),
    });
    return response.json();
  }

  /**
   * Connect to WebSocket for streaming
   */
  connectWebSocket(onMessage, onError, onClose) {
    const wsURL = this.baseURL.replace('http', 'ws') + '/ws/stream';
    this.ws = new WebSocket(wsURL);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      if (onClose) onClose();
    };

    return this.ws;
  }

  /**
   * Send message via WebSocket
   */
  sendWebSocketMessage(type, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }));
    }
  }

  /**
   * Close WebSocket connection
   */
  closeWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default AgentLuckyClient;

