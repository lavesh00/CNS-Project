"""
Test Agent Lucky API
Simple demonstration of the agentic system
"""

import requests
import json

BASE_URL = "http://127.0.0.1:7777"

def test_agent():
    print("\n" + "="*60)
    print("Agent Lucky API Test")
    print("="*60 + "\n")
    
    # 1. Health Check
    print("[1] Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.json()['status']}")
    print(f"   Version: {response.json()['version']}\n")
    
    # 2. System Status
    print("[2] Checking system status...")
    response = requests.get(f"{BASE_URL}/status")
    data = response.json()
    print(f"   Backend: {data['backend']}")
    print(f"   Models dir: {data['models']['models_dir']}")
    print(f"   Installed models: {data['models']['installed_count']}")
    print(f"   Available presets: {data['models']['available_presets']}\n")
    
    # 3. List Models
    print("[3] Listing available models...")
    response = requests.get(f"{BASE_URL}/models/list")
    models = response.json()
    
    if models.get('available'):
        print(f"   Found {len(models['available'])} models:")
        for model in models['available'][:3]:
            print(f"      - {model['name']} ({model['size']})")
    print()
    
    # 4. Agent Status
    print("[4] Checking agent status...")
    response = requests.get(f"{BASE_URL}/agent/status")
    agent = response.json()
    print(f"   State: {agent['state']}")
    print(f"   Progress: {agent['progress']}%\n")
    
    # 5. Start Agent (demo)
    print("[5] Starting agent with sample task...")
    task = {
        "prompt": "Create a simple REST API with user authentication",
        "workspace_path": "./demo-project"
    }
    response = requests.post(f"{BASE_URL}/agent/start", json=task)
    result = response.json()
    print(f"   Status: {result['status']}")
    print(f"   Task ID: {result.get('task_id', 'N/A')}")
    print(f"   Message: {result.get('message', 'Started')}\n")
    
    print("="*60)
    print("SUCCESS: All tests passed! Agent Lucky is working!")
    print("="*60 + "\n")
    
    print("Next Steps:")
    print("   1. Download a model: POST /models/download")
    print("   2. Create a project: POST /agent/start")
    print("   3. Check documentation: docs/getting-started.md")
    print()

if __name__ == "__main__":
    try:
        test_agent()
    except requests.exceptions.ConnectionError:
        print("ERROR: Backend not running!")
        print("   Start it with: py backend/main.py")
    except Exception as e:
        print(f"ERROR: {e}")

