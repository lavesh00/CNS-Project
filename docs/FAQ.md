# Frequently Asked Questions

## General

### What is Agent Lucky?
Agent Lucky is a production-grade agentic AI coding system built on top of VS Code. It can generate entire projects, fix bugs, and manage codebases using local open-source models.

### Is it really free and open-source?
Yes! Agent Lucky is released under the MIT License and is completely free to use.

### Does it work offline?
Yes! Agent Lucky runs local models and works completely offline once models are downloaded.

## Installation

### What are the system requirements?
- Node.js 18+
- Python 3.10+
- 8GB+ RAM (16GB+ recommended)
- Git

### How much disk space do I need?
- Backend: ~500MB
- Models: 2-10GB per model
- Total: 5-20GB depending on models

### Can I run it on Windows/Mac/Linux?
Yes, Agent Lucky supports all three platforms.

## Models

### Which model should I use?
- For speed: Phi-3 (2.3GB) or Code Llama 7B (4GB)
- For quality: Code Llama 13B (8GB) or DeepSeek Coder (4GB)
- For large files: Mistral 7B (32k context)

### Can I use cloud models like GPT-4?
Currently, Agent Lucky only supports local models. Cloud model support is planned for future releases.

### How do I add my own model?
```python
manager = ModelManager()
await manager.download_custom_model(
    repo_id="HuggingFace/model-repo",
    filename="model.Q4_K_M.gguf"
)
```

## Usage

### How do I generate a project?
```python
response = requests.post('http://127.0.0.1:7777/agent/start', json={
    "prompt": "Create a React todo app",
    "workspace_path": "./my-project"
})
```

### Can it modify existing projects?
Yes! Point the workspace_path to your existing project and Agent Lucky will analyze and modify it.

### Does it commit to Git automatically?
Yes, with configurable strategies:
- per-file: One commit per file
- per-todo: One commit per task (default)
- batch: All changes in one commit

### Can I review changes before they're applied?
Yes, the Patch Review Panel (coming soon in VS Code UI) will let you review and approve changes.

## Performance

### Why is it slow?
- Large models (13B+) are slower but produce better results
- Use smaller models (7B) or GPU acceleration for speed
- First run includes model download and workspace indexing

### How can I speed it up?
- Use GPU acceleration (CUDA/Metal)
- Use smaller quantized models (Q4)
- Reduce context window size
- Use SSD storage for models

### It's using too much memory
- Use smaller models (Phi-3, Code Llama 7B)
- Close other applications
- Use Q4 quantization instead of Q8

## Troubleshooting

### Backend won't start
- Check Python 3.10+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check port 7777 is not in use

### Model download fails
- Check internet connection
- Verify HuggingFace is accessible
- Check disk space

### Generated code has errors
- Use code-specific models (Code Llama, DeepSeek)
- Increase temperature (0.4-0.6)
- Provide more context in prompt
- Enable RAG for existing codebase

### Tests fail
- Check Docker is installed (optional but recommended)
- Verify test commands are correct
- Check workspace has required dependencies

## Features

### Does it support TypeScript?
Code generation works with JavaScript. Full TypeScript support is planned.

### Can it create databases?
Yes, it can generate database schemas, models, and migrations.

### Does it support mobile development?
React Native projects are supported through templates.

### Can it deploy to cloud?
It can generate deployment configurations (Docker, CI/CD), but doesn't deploy automatically.

## Privacy & Security

### Is my code sent to external servers?
No! Everything runs locally. No data is sent anywhere.

### Is there telemetry?
No telemetry or tracking at all.

### How are GitHub tokens stored?
In your OS keychain (secure storage).

### Is it safe to use for work projects?
Yes, but always review generated code before committing.

## Future Plans

### Will there be a VS Code extension?
Yes! VS Code integration is in progress.

### Will it support cloud models?
Optional cloud model support is planned.

### Can teams use it together?
Team collaboration features are planned.

## Getting Help

Can't find your answer?

- Check [Documentation](getting-started.md)
- Ask on [GitHub Discussions](https://github.com/lavesh00/agent-lucky/discussions)
- Join [Discord](https://discord.gg/agentlucky)
- Report bugs on [GitHub Issues](https://github.com/lavesh00/agent-lucky/issues)

