# API Reference

## FastAPI Backend Endpoints

Base URL: `http://127.0.0.1:7777`

### Health & Status

#### GET /health
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "service": "agent-lucky-backend",
  "version": "1.0.0"
}
```

#### GET /status
Get backend status

**Response**:
```json
{
  "backend": "running",
  "models": {...},
  "indexer": {...}
}
```

### Agent Operations

#### POST /agent/start
Start an agent task

**Request Body**:
```json
{
  "prompt": "Create a todo app",
  "workspace_path": "/path/to/workspace",
  "context": {}
}
```

**Response**:
```json
{
  "status": "started",
  "task_id": "task-001",
  "message": "Agent task started"
}
```

#### POST /agent/stop
Stop a running agent task

**Request Body**:
```json
{
  "task_id": "task-001"
}
```

#### GET /agent/status
Get current agent status

**Response**:
```json
{
  "state": "working",
  "current_task": "todo-3",
  "progress": 60
}
```

#### GET /agent/plan/current
Get current execution plan

**Response**:
```json
{
  "plan": {...},
  "todos": [...],
  "completed": [...],
  "in_progress": "todo-3"
}
```

### Model Management

#### GET /models/list
List available and installed models

**Response**:
```json
{
  "installed": [...],
  "available": [...]
}
```

#### POST /models/download
Download a model

**Request Body**:
```json
{
  "model_id": "codellama-13b-q4",
  "quantization": "Q4_K_M"
}
```

#### GET /models/status/{model_id}
Get model download/load status

#### DELETE /models/{model_id}
Delete an installed model

### Web Scraping

#### POST /scraper/start
Start scraping a website

**Request Body**:
```json
{
  "url": "https://example.com",
  "max_depth": 2,
  "respect_robots": true,
  "output_path": "./scraped"
}
```

#### GET /scraper/status/{scrape_id}
Get scraper status

#### POST /scraper/stop/{scrape_id}
Stop a scraping task

### GitHub Integration

#### POST /github/create-repo
Create a GitHub repository

**Request Body**:
```json
{
  "name": "my-project",
  "description": "Created by Agent Lucky",
  "private": false
}
```

#### POST /github/push
Push changes to GitHub

**Request Body**:
```json
{
  "branch": "main",
  "commit_message": "Update from Agent Lucky"
}
```

#### POST /github/create-pr
Create a pull request

**Request Body**:
```json
{
  "title": "Feature: New functionality",
  "description": "Implemented by Agent Lucky",
  "base_branch": "main",
  "head_branch": "feature-branch"
}
```

#### GET /github/status
Get GitHub connection status

### WebSocket

#### WS /ws/stream
WebSocket endpoint for streaming agent responses

**Message Types**:
- `ping`: Heartbeat
- `agent_request`: Start agent task
- `agent_response`: Agent response/update

**Example**:
```javascript
const ws = new WebSocket('ws://127.0.0.1:7777/ws/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

ws.send(JSON.stringify({
  type: 'agent_request',
  prompt: 'Create a todo app'
}));
```

## Python Client Example

```python
import requests

# Start agent
response = requests.post('http://127.0.0.1:7777/agent/start', json={
    "prompt": "Create a REST API with authentication",
    "workspace_path": "./my-project"
})

task_id = response.json()['task_id']

# Check status
while True:
    status = requests.get('http://127.0.0.1:7777/agent/status').json()
    if status['state'] == 'completed':
        break
    time.sleep(1)

# Get plan
plan = requests.get('http://127.0.0.1:7777/agent/plan/current').json()
print(plan)
```

## JavaScript Client Example

```javascript
const client = new AgentLuckyClient();

// Start agent
const result = await client.startAgent(
  "Create a React dashboard",
  "./my-project"
);

// Stream responses
client.connectWebSocket(
  (message) => console.log(message),
  (error) => console.error(error)
);

// Download model
await client.downloadModel('codellama-7b-q4');
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "path": "/api/endpoint"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad request
- 404: Not found
- 500: Internal server error

