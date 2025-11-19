# Model Management Guide

## Available Models

Agent Lucky supports running local open-source models completely offline.

### Code-Specific Models

#### Code Llama
- **7B Q4**: 4.1GB - Fast, good for most tasks
- **13B Q4**: 7.9GB - Better quality, slower
- **Best for**: General code generation, Python, JavaScript, C++

#### StarCoder
- **7B Q4**: 4.3GB
- **Trained on**: 80+ programming languages
- **Best for**: Multi-language projects, data science

#### DeepSeek Coder
- **6.7B Q4**: 4.0GB
- **Best for**: Complex code understanding, refactoring

### General Models

#### Mistral 7B
- **Size**: 4.4GB
- **Context**: 32k tokens (very large!)
- **Best for**: Large files, documentation

#### Llama 3 8B
- **Size**: 4.9GB
- **Best for**: General tasks, explanations

#### Phi-3 Mini
- **Size**: 2.3GB (smallest!)
- **Best for**: Fast iterations, testing

## Downloading Models

### Via API

```python
import requests

response = requests.post('http://127.0.0.1:7777/models/download', json={
    "model_id": "codellama-13b-q4"
})

print(response.json())
```

### Via Python

```python
import asyncio
from backend.models.manager import ModelManager

async def download():
    manager = ModelManager()
    await manager.initialize()
    
    # Download Code Llama
    success = await manager.download_model('codellama-13b-q4')
    print(f"Download {'successful' if success else 'failed'}")

asyncio.run(download())
```

## Model Selection Guide

### For Planning
**Recommended**: Larger models (13B+)
- Better task breakdown
- More accurate dependencies
- Code Llama 13B or DeepSeek Coder

### For Code Generation
**Recommended**: Code-specific models
- Code Llama 7B/13B
- DeepSeek Coder
- StarCoder

### For Documentation
**Recommended**: General models with large context
- Mistral 7B (32k context)
- Llama 3 8B

### For Speed
**Recommended**: Smaller models
- Phi-3 (2.3GB)
- Code Llama 7B (4.1GB)

## Quantization Levels

- **Q4_K_M**: 4-bit (default, best balance)
- **Q5_K_M**: 5-bit (slightly better quality)
- **Q8_0**: 8-bit (highest quality, largest size)

## Hardware Requirements

| Model Size | RAM | GPU VRAM | Speed |
|------------|-----|----------|-------|
| 2-4GB | 8GB | Optional | Fast |
| 4-7GB | 12GB | 4GB+ | Medium |
| 7-10GB | 16GB | 6GB+ | Slower |
| 10GB+ | 24GB+ | 8GB+ | Slowest |

## Custom Models

You can add any GGUF model from HuggingFace:

```python
manager = ModelManager()
await manager.download_custom_model(
    repo_id="TheBloke/SomeModel-GGUF",
    filename="somemodel.Q4_K_M.gguf",
    model_id="my-custom-model"
)
```

## Storage Location

Models are stored in:
- Linux/Mac: `~/.agent-lucky/models/`
- Windows: `%USERPROFILE%\.agent-lucky\models\`

## Managing Models

### List Installed

```bash
curl http://127.0.0.1:7777/models/list
```

### Delete Model

```bash
curl -X DELETE http://127.0.0.1:7777/models/codellama-7b-q4
```

## Troubleshooting

### Download Fails
- Check internet connection
- Verify HuggingFace is accessible
- Check disk space

### Out of Memory
- Use smaller models (Q4 instead of Q8)
- Close other applications
- Increase system swap space

### Slow Inference
- Use GPU acceleration if available
- Use smaller models
- Reduce context window size

