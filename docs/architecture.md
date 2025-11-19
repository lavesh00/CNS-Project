# Agent Lucky Architecture

## Overview

Agent Lucky is a production-grade agentic AI coding system built on top of VS Code. It uses a three-stage agentic loop: **Planner → Worker → Summarizer**.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     VS Code IDE                         │
│  ┌────────────────────────────────────────────────┐    │
│  │  Agent Panels (UI)                             │    │
│  │  - Agent Panel (prompt input)                  │    │
│  │  - Plan/TODO Panel                             │    │
│  │  - Patch Review Panel                          │    │
│  │  - Agent Console (logs)                        │    │
│  └────────────────────────────────────────────────┘    │
│                        │ REST API                       │
└────────────────────────┼───────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │  Orchestrator                            │          │
│  │  - Manages Planner/Worker/Summarizer     │          │
│  │  - Tracks state and progress             │          │
│  └──────────────────────────────────────────┘          │
│           │            │            │                    │
│           ▼            ▼            ▼                    │
│  ┌─────────┐  ┌─────────┐  ┌──────────────┐           │
│  │ Planner │  │ Worker  │  │ Summarizer   │           │
│  │         │  │         │  │              │           │
│  │ Creates │  │Executes │  │ Creates      │           │
│  │ TODOs   │  │ TODOs   │  │ summaries    │           │
│  └─────────┘  └─────────┘  └──────────────┘           │
│       │            │                │                    │
│       └────────────┼────────────────┘                    │
│                    │                                      │
│  ┌─────────────────┼─────────────────────────┐          │
│  │  Supporting Systems                       │          │
│  │                                            │          │
│  │  • Model Manager (HuggingFace downloads)  │          │
│  │  • llama.cpp Runtime (local inference)    │          │
│  │  • RAG System (FAISS + embeddings)        │          │
│  │  • Git Automation (GitPython)             │          │
│  │  • GitHub Integration (PyGithub)          │          │
│  │  • Web Scraper (Playwright)               │          │
│  │  • MCP Client (extensibility)             │          │
│  │  • Test Sandbox (Docker)                  │          │
│  └────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Orchestrator

**Purpose**: Manages the main agentic loop

**Workflow**:
1. Receives user prompt
2. Calls Planner to create execution plan
3. Iterates through TODOs:
   - Calls Worker to execute TODO
   - Applies patches to workspace
   - Commits changes (based on strategy)
   - Runs tests if specified
4. Calls Summarizer to create progress summary
5. Returns final results to user

**Key Features**:
- Progress tracking
- State management
- Error recovery
- Stop/pause controls

### 2. Planner

**Purpose**: Breaks down high-level prompts into structured TODOs

**Input**:
- User prompt
- Workspace context
- Project summary (from previous iterations)

**Output**: JSON plan with TODOs
```json
{
  "goal": "Create authentication system",
  "todos": [
    {
      "id": "todo-1",
      "title": "Create user model",
      "description": "...",
      "required_context": ["models/", "db config"],
      "estimated_steps": 3,
      "dependencies": []
    }
  ]
}
```

**How It Works**:
- Uses LLM in JSON-only mode for structured output
- Validates dependencies to avoid circular references
- Estimates complexity for each TODO
- Identifies required context files

### 3. Worker

**Purpose**: Executes individual TODOs and generates code patches

**Input**:
- Single TODO
- Workspace path
- Project context

**Process**:
1. **Retrieve Context**: Uses RAG to find relevant code
2. **Use MCP Tools**: Calls external tools if needed (docs, APIs)
3. **Generate Code**: LLM produces code changes
4. **Create Patches**: Generates patches in unified diff format
5. **Validate**: Checks syntax and file existence

**Output**: WorkResult with patches and evidence
```json
{
  "status": "done",
  "explanation": "Created user authentication model",
  "patches": [
    {
      "file": "backend/models/user.py",
      "action": "create",
      "content": "..."
    }
  ],
  "evidence": [
    {"file": "backend/models/user.py", "lines": [10, 25]}
  ],
  "tests": ["pytest tests/test_auth.py"]
}
```

### 4. Summarizer

**Purpose**: Creates compact, evidence-backed summaries

**Two-Stage Process**:

**Stage 1 - Extractive Summarization (TextRank)**:
- Extracts key sentences from logs and code changes
- Uses graph-based ranking
- Selects top 10 most important sentences

**Stage 2 - Structured Reasoning (LLM)**:
- Feeds extracted sentences to LLM
- Generates structured JSON summary:
  - Progress overview
  - Completed TODOs
  - Claims with evidence (file:line)
  - Open issues
  - Next suggested TODOs

**Output**: Compact summary for next iteration

## Supporting Systems

### Model Manager

**Purpose**: Downloads and manages local AI models

**Features**:
- Preset model catalog (Code Llama, StarCoder, etc.)
- HuggingFace Hub integration
- GGUF format support
- Model validation (size, license)
- Storage in `~/.agent-lucky/models/`

**Models**:
```
codellama-7b-q4     -> 4.1GB
codellama-13b-q4    -> 7.9GB
starcoder-7b-q4     -> 4.3GB
deepseek-coder-q4   -> 4.0GB
mistral-7b-q4       -> 4.4GB
phi3-q4             -> 2.3GB
```

### llama.cpp Runtime

**Purpose**: Runs quantized models locally

**Features**:
- CPU and GPU acceleration
- Streaming token generation
- JSON-only mode (grammar constraints)
- Context window management (8k-128k)
- Temperature/top_p/top_k controls

**Workflow**:
1. Load model from disk
2. Generate tokens with constraints
3. Stream or batch output
4. Validate and repair JSON

### RAG System

**Purpose**: Retrieves relevant code context

**Components**:

**VectorStore** (FAISS):
- CPU-optimized vector search
- sentence-transformers embeddings
- Metadata: file_path, lines, language

**Indexer**:
- Watches workspace for changes
- Incremental indexing
- Language-aware chunking (functions, classes)
- Supports 20+ languages

**Retriever**:
- Semantic search (vector similarity)
- Hybrid search (semantic + file-based)
- Reranking for relevance
- Context formatting for LLM

**Chunking Strategy**:
- Small files: Single chunk
- Large files: Split by functions/classes
- Overlap: 200 characters between chunks
- Size: 500-1000 tokens per chunk

### Git Automation

**Purpose**: Local Git operations

**Features**:
- Initialize repos
- Stage files (individual or batch)
- Commit with structured messages
- Branch creation/switching
- Push to remote

**Commit Strategies**:
1. **Per-file**: One commit per file change
2. **Per-TODO**: One commit per completed TODO (default)
3. **Batch**: Group all changes in one commit

**Commit Message Template**:
```
[Agent] <TODO title>

- Created/Modified: file1, file2, file3
- Purpose: <brief explanation>
- Evidence: file:line

Generated by Agent Lucky
```

### GitHub Integration

**Purpose**: Remote repository management

**Features**:
- Create repositories
- Push branches
- Open pull requests
- Add PR comments
- Auto-merge (if tests pass)
- Token-based authentication

**Security**:
- Tokens stored in OS keychain
- Environment variable fallback
- User approval required for actions

### Web Scraper

**Purpose**: Scrape and clone websites

**Technology**: Playwright (headless Chromium)

**Features**:
- Recursive crawling
- Asset downloading (images, CSS, JS)
- URL rewriting for local serving
- Domain filtering
- robots.txt respect (optional)
- Depth control

**Output**:
- HTML pages in `scraped/pages/`
- Assets in `scraped/assets/`
- Manifest JSON with metadata

### MCP Client

**Purpose**: Extensibility via Model Context Protocol

**Features**:
- Connect to MCP servers
- Tool discovery and invocation
- Context provider integration
- Multiple transport types (stdio, HTTP)

**Built-in MCP Servers** (planned):
- Documentation server
- GitHub API server
- Stack Overflow search

### Test Sandbox

**Purpose**: Isolated test execution

**Modes**:
1. **Docker** (preferred): Full isolation in containers
2. **Local** (fallback): Direct execution

**Supported Frameworks**:
- Python: pytest, unittest
- Node.js: jest, mocha
- Java: JUnit
- Go: go test

**Features**:
- Timeout handling
- Output capture
- Pass/fail detection
- Resource limits (Docker)

## Data Flow

### Project Generation Flow

```
User Prompt
    │
    ▼
Planner → Plan with TODOs
    │
    ├─→ TODO 1
    │     │
    │     ▼
    │   Worker
    │     │
    │     ├─→ RAG: Get relevant context
    │     ├─→ MCP: Get external data
    │     └─→ Generate patches
    │          │
    │          ▼
    │       Apply patches
    │          │
    │          ▼
    │       Git commit
    │          │
    │          ▼
    │       GitHub push
    │          │
    │          ▼
    │       Run tests
    │
    ├─→ TODO 2
    │   ...
    │
    ▼
Summarizer → Progress summary
    │
    ▼
Return to user
```

## Technology Stack

### Frontend (VS Code)
- TypeScript (VS Code core)
- JavaScript (custom panels)
- React (UI components)
- Monaco Editor
- Electron

### Backend
- Python 3.10+
- FastAPI (REST API)
- llama.cpp (inference)
- FAISS (vector search)
- sentence-transformers
- GitPython
- PyGithub
- Playwright
- Docker SDK

### Models
- GGUF format (quantized)
- 4-bit, 5-bit, 8-bit quantization
- CPU and GPU support

## Performance Considerations

### Memory Usage
- **4GB models**: 6-8GB RAM recommended
- **7GB models**: 12-16GB RAM recommended
- **13GB+ models**: 24GB+ RAM recommended

### Speed
- **Planning**: 5-30 seconds (depends on model size)
- **Code Generation**: 10-60 seconds per TODO
- **RAG Indexing**: 1-5 seconds per 1000 files
- **Web Scraping**: 2-10 seconds per page

### Optimization
- Use quantized models (Q4_K_M) for best speed/quality
- Enable GPU acceleration when available
- Index workspace incrementally
- Use smaller context windows when possible

## Security Model

### Local-First
- All processing happens locally
- No data sent to external servers
- Models run on your machine

### Permission System
- Explicit approval for external actions
- Token storage in OS keychain
- Sandbox isolation for tests

### Privacy
- No telemetry
- No tracking
- No cloud requirements (fully offline)

## Extensibility

### Adding Models
1. Add model config to `ModelManager.PRESET_MODELS`
2. Specify HuggingFace repo and filename
3. Model auto-downloaded on first use

### Adding Project Templates
1. Create JSON in `backend/templates/`
2. Define structure and files
3. Templates auto-discovered by agent

### Adding MCP Servers
1. Create MCP server (stdio or HTTP)
2. Register in MCP client config
3. Tools and providers auto-discovered

### Custom Workflows
1. Extend Orchestrator for custom loops
2. Add API endpoints in FastAPI
3. Create UI panels in VS Code

## Future Enhancements

- Multi-model support (different models per task)
- Cloud sync (optional)
- Team collaboration
- Voice input
- Visual debugging
- Plugin marketplace

