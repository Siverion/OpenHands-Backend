#!/usr/bin/env python3
"""
OpenHands Backend for Hugging Face Spaces - FIXED VERSION
Handles file storage and session management properly
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_hf_environment():
    """Setup environment for Hugging Face Spaces with proper file storage"""
    logger.info("🔧 Setting up Hugging Face environment...")
    
    # Set environment variables
    os.environ['HF_SPACES'] = '1'
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['RUNTIME'] = 'local'
    os.environ['PYTHONPATH'] = '/app'
    
    # Setup proper workspace and storage directories
    workspace_dir = '/tmp/workspace'
    sessions_dir = '/tmp/sessions'
    logs_dir = '/tmp/logs'
    
    # Create directories if they don't exist
    for directory in [workspace_dir, sessions_dir, logs_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")
    
    # Set OpenHands specific environment variables
    os.environ['WORKSPACE_BASE'] = workspace_dir
    os.environ['WORKSPACE_MOUNT_PATH'] = workspace_dir
    os.environ['WORKSPACE_MOUNT_PATH_IN_SANDBOX'] = workspace_dir
    os.environ['SANDBOX_RUNTIME_CONTAINER_IMAGE'] = 'ubuntu:22.04'
    os.environ['SANDBOX_USER_ID'] = '1000'
    os.environ['SANDBOX_TIMEOUT'] = '120'
    
    # Disable problematic features for HF Spaces
    os.environ['DISABLE_COLOR'] = '1'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['SANDBOX_TYPE'] = 'local'
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    logger.info("✅ Environment configured for Hugging Face Spaces")
    return workspace_dir, sessions_dir, logs_dir

def check_dependencies():
    """Check if required dependencies are available"""
    logger.info("🔍 Checking dependencies...")
    
    required_deps = ['fastapi', 'uvicorn', 'litellm']
    missing_deps = []
    
    for dep in required_deps:
        try:
            __import__(dep)
            logger.info(f"✅ {dep} available")
        except ImportError:
            logger.error(f"❌ {dep} not available")
            missing_deps.append(dep)
    
    if missing_deps:
        logger.error(f"❌ Missing required dependencies: {missing_deps}")
        return False
    
    # Check optional dependencies
    optional_deps = ['docker', 'google.api_core']
    for dep in optional_deps:
        try:
            __import__(dep)
            logger.info(f"✅ {dep} available")
        except ImportError:
            logger.info(f"✅ {dep} not available (expected for HF Spaces)")
    
    return True

def setup_minimal_config():
    """Setup minimal configuration for OpenHands"""
    logger.info("⚙️ Setting up minimal OpenHands configuration...")
    
    # Create minimal config
    config = {
        'default_agent': 'CodeActAgent',
        'runtime': 'local',
        'max_iterations': 30,
        'max_budget_per_task': float(os.getenv('MAX_BUDGET_PER_TASK', '10.0')),
        'e2b_api_key': None,
        'sandbox': {
            'runtime_container_image': 'ubuntu:22.04',
            'user_id': 1000,
            'timeout': 120,
            'enable_auto_lint': False,
            'use_host_network': False,
        },
        'llm': {
            'model': os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307'),
            'api_key': os.getenv('LLM_API_KEY', ''),
            'base_url': os.getenv('LLM_BASE_URL', 'https://openrouter.ai/api/v1'),
            'api_version': None,
        }
    }
    
    # Set config environment
    import json
    os.environ['OPENHANDS_CONFIG'] = json.dumps(config)
    
    logger.info("✅ Minimal configuration setup complete")
    return config

def create_simple_app():
    """Create a simple FastAPI app for HF Spaces"""
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import httpx
    
    app = FastAPI(
        title="OpenHands Backend for HF Spaces",
        description="Personal AI Assistant with OpenRouter Integration",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OpenHands Backend - HF Spaces</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }
                .success { color: #27ae60; font-weight: bold; }
                .info { color: #3498db; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 OpenHands Backend</h1>
                <div class="status">
                    <p class="success">✅ Server is running successfully!</p>
                    <p class="info">🚀 Ready for AI assistance and Indonesian novel writing</p>
                </div>
                
                <h2>📡 Available Endpoints:</h2>
                <div class="endpoint">
                    <strong>Health Check:</strong> <a href="/health">/health</a>
                </div>
                <div class="endpoint">
                    <strong>API Documentation:</strong> <a href="/docs">/docs</a>
                </div>
                <div class="endpoint">
                    <strong>Test Chat:</strong> <a href="/test-chat">/test-chat</a>
                </div>
                <div class="endpoint">
                    <strong>Novel Writing:</strong> <a href="/novel">/novel</a>
                </div>
                <div class="endpoint">
                    <strong>Simple Chat API:</strong> <a href="/api/chat">/api/chat</a>
                </div>
                
                <h2>💡 How to Use:</h2>
                <ul>
                    <li><strong>Coding Help:</strong> Use /api/chat for programming assistance</li>
                    <li><strong>Novel Writing:</strong> Use /novel for Indonesian creative writing</li>
                    <li><strong>File Management:</strong> Upload and manage files through API</li>
                </ul>
                
                <p style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                    <em>Personal AI Assistant powered by OpenRouter 💕</em>
                </p>
            </div>
        </body>
        </html>
        """)
    
    @app.get("/health")
    async def health():
        return {"status": "OK", "message": "OpenHands Backend is running"}
    
    @app.get("/test-chat")
    async def test_chat():
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Chat - OpenHands</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                .chat-box { border: 1px solid #ddd; height: 300px; overflow-y: auto; padding: 10px; margin: 10px 0; background: #fafafa; }
                .input-group { display: flex; gap: 10px; }
                input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                .user { background: #e3f2fd; text-align: right; }
                .assistant { background: #f1f8e9; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💬 Test Chat</h1>
                <div id="chatBox" class="chat-box"></div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Send</button>
                </div>
                <p><em>Try asking: "Help me write a Python function" or "Tulis cerita pendek tentang Jakarta"</em></p>
            </div>
            
            <script>
                async function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const chatBox = document.getElementById('chatBox');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    // Add user message
                    chatBox.innerHTML += `<div class="message user"><strong>You:</strong> ${message}</div>`;
                    input.value = '';
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: message })
                        });
                        
                        const data = await response.json();
                        chatBox.innerHTML += `<div class="message assistant"><strong>Assistant:</strong> ${data.response || 'Response received!'}</div>`;
                    } catch (error) {
                        chatBox.innerHTML += `<div class="message assistant"><strong>Assistant:</strong> Sorry, I'm having trouble connecting. Please check the API configuration.</div>`;
                    }
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            </script>
        </body>
        </html>
        """)
    
    @app.post("/api/chat")
    async def chat(request: dict):
        message = request.get('message', '')
        
        # Simple response for testing
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Check if LLM API key is configured
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            return {
                "response": "⚠️ LLM API key not configured. Please set LLM_API_KEY environment variable in HF Spaces settings.",
                "status": "error"
            }
        
        try:
            # Simple OpenRouter API call
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307'),
                        "messages": [
                            {"role": "system", "content": "You are a helpful AI assistant for coding and creative writing. Respond in the same language as the user's question."},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data['choices'][0]['message']['content']
                    return {"response": ai_response, "status": "success"}
                else:
                    return {
                        "response": f"API Error: {response.status_code} - {response.text}",
                        "status": "error"
                    }
                    
        except Exception as e:
            return {
                "response": f"Error: {str(e)}. Please check your OpenRouter API key and internet connection.",
                "status": "error"
            }
    
    @app.get("/novel")
    async def novel_interface():
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Novel Writing - OpenHands</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
                textarea { width: 100%; height: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: inherit; }
                button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 10px 5px; }
                button:hover { background: #218838; }
                .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; white-space: pre-wrap; }
                .templates { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
                .template { padding: 5px 10px; background: #e9ecef; border: none; border-radius: 3px; cursor: pointer; font-size: 12px; }
                .template:hover { background: #dee2e6; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 Indonesian Novel Writing</h1>
                <p>Tulis prompt untuk cerita Anda dalam Bahasa Indonesia:</p>
                
                <div class="templates">
                    <button class="template" onclick="setTemplate('Romance')">Romance</button>
                    <button class="template" onclick="setTemplate('Adventure')">Petualangan</button>
                    <button class="template" onclick="setTemplate('Mystery')">Misteri</button>
                    <button class="template" onclick="setTemplate('SciFi')">Sci-Fi</button>
                    <button class="template" onclick="setTemplate('Fantasy')">Fantasy</button>
                    <button class="template" onclick="setTemplate('Drama')">Drama</button>
                    <button class="template" onclick="setTemplate('Comedy')">Komedi</button>
                </div>
                
                <textarea id="promptInput" placeholder="Contoh: Tulis cerita romantis tentang seorang programmer yang jatuh cinta dengan AI assistant..."></textarea>
                <br>
                <button onclick="generateNovel()">✍️ Generate Novel</button>
                <button onclick="clearResult()">🗑️ Clear</button>
                
                <div id="result" class="result" style="display: none;"></div>
            </div>
            
            <script>
                function setTemplate(type) {
                    const templates = {
                        'Romance': 'Tulis cerita romantis tentang dua orang yang bertemu di Jakarta...',
                        'Adventure': 'Ceritakan petualangan seorang penjelajah di hutan Kalimantan...',
                        'Mystery': 'Buat cerita misteri tentang hilangnya artefak kuno di museum...',
                        'SciFi': 'Tulis cerita fiksi ilmiah tentang kehidupan di Mars tahun 2050...',
                        'Fantasy': 'Ceritakan tentang dunia magis yang tersembunyi di Indonesia...',
                        'Drama': 'Buat drama keluarga tentang konflik generasi di Jakarta...',
                        'Comedy': 'Tulis komedi tentang kehidupan mahasiswa di kampus...'
                    };
                    document.getElementById('promptInput').value = templates[type];
                }
                
                async function generateNovel() {
                    const prompt = document.getElementById('promptInput').value.trim();
                    const resultDiv = document.getElementById('result');
                    
                    if (!prompt) {
                        alert('Please enter a prompt for your novel!');
                        return;
                    }
                    
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '⏳ Generating your novel... Please wait...';
                    
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                message: `Sebagai penulis novel Indonesia yang berpengalaman, ${prompt}. Tulis dengan gaya bahasa yang menarik, dialog yang natural, dan deskripsi yang vivid. Buat cerita sepanjang 2-3 paragraf dengan karakter yang kuat.`
                            })
                        });
                        
                        const data = await response.json();
                        resultDiv.innerHTML = data.response || 'Novel generated successfully!';
                    } catch (error) {
                        resultDiv.innerHTML = 'Error generating novel. Please check your API configuration.';
                    }
                }
                
                function clearResult() {
                    document.getElementById('result').style.display = 'none';
                    document.getElementById('promptInput').value = '';
                }
            </script>
        </body>
        </html>
        """)
    
    return app

def main():
    """Main application entry point"""
    print("=" * 60)
    print("🤗 OpenHands Backend for Hugging Face Spaces - FIXED")
    print("=" * 60)
    
    # Setup environment
    workspace_dir, sessions_dir, logs_dir = setup_hf_environment()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Required dependencies missing")
        sys.exit(1)
    
    # Setup minimal config
    config = setup_minimal_config()
    
    # Create simple app instead of importing complex OpenHands
    logger.info("📦 Creating simplified FastAPI app...")
    app = create_simple_app()
    
    # Configuration
    host = "0.0.0.0"
    port = 7860
    
    # Environment variables info
    llm_api_key = os.getenv('LLM_API_KEY', 'NOT_SET')
    llm_model = os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307')
    llm_base_url = os.getenv('LLM_BASE_URL', 'https://openrouter.ai/api/v1')
    
    print("\n" + "=" * 60)
    print("🤗 OpenHands Backend - Simplified for HF Spaces")
    print("=" * 60)
    print(f"🚀 Server: {host}:{port}")
    print(f"🔑 LLM API Key: {'✅ Set' if llm_api_key != 'NOT_SET' else '❌ Missing'}")
    print(f"🤖 LLM Model: {llm_model}")
    print(f"🌐 LLM Base URL: {llm_base_url}")
    print(f"🏃 Runtime: local (simplified)")
    print(f"📁 Workspace: {workspace_dir}")
    print(f"📂 Sessions: {sessions_dir}")
    print(f"📋 Logs: {logs_dir}")
    print("=" * 60)
    
    if llm_api_key == 'NOT_SET':
        print("\n⚠️  WARNING: LLM_API_KEY not set!")
        print("💡 Set your OpenRouter API key in HF Spaces environment variables")
    
    print("\n🚀 Starting simplified uvicorn server...")
    
    # Start the server
    import uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()