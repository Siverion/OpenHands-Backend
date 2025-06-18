#!/usr/bin/env python3
"""
Ultra Simple OpenHands Backend for HF Spaces
NO complex imports - just pure FastAPI + OpenRouter
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenHands Backend - Ultra Simple",
    description="Personal AI Assistant with OpenRouter",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    """Homepage with working interface"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenHands Backend - Ultra Simple</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { 
                text-align: center; 
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status { 
                background: rgba(40, 167, 69, 0.2); 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                border: 1px solid rgba(40, 167, 69, 0.3);
            }
            .endpoint { 
                background: rgba(255,255,255,0.1); 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 8px;
                border-left: 4px solid #ffd700;
            }
            .success { color: #90EE90; font-weight: bold; }
            .info { color: #87CEEB; }
            a { 
                color: #ffd700; 
                text-decoration: none; 
                font-weight: bold;
            }
            a:hover { text-decoration: underline; }
            .chat-section {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .chat-box {
                background: rgba(0,0,0,0.2);
                height: 300px;
                overflow-y: auto;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .input-group {
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255,255,255,0.9);
                color: #333;
                font-size: 14px;
            }
            button {
                padding: 12px 24px;
                background: #ffd700;
                color: #333;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s;
            }
            button:hover {
                background: #ffed4e;
                transform: translateY(-2px);
            }
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 8px;
                animation: fadeIn 0.3s;
            }
            .user {
                background: rgba(0, 123, 255, 0.3);
                text-align: right;
                border-left: 3px solid #007bff;
            }
            .assistant {
                background: rgba(40, 167, 69, 0.3);
                border-left: 3px solid #28a745;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 OpenHands Backend</h1>
            <div class="status">
                <p class="success">✅ Server is running successfully!</p>
                <p class="info">🚀 Ready for AI assistance and Indonesian novel writing</p>
                <p class="info">💡 Ultra Simple Version - No Complex Dependencies</p>
            </div>
            
            <h2>📡 Available Endpoints:</h2>
            <div class="endpoint">
                <strong>Health Check:</strong> <a href="/health">/health</a>
            </div>
            <div class="endpoint">
                <strong>API Documentation:</strong> <a href="/docs">/docs</a>
            </div>
            <div class="endpoint">
                <strong>Novel Writing:</strong> <a href="/novel">/novel</a>
            </div>
            
            <div class="chat-section">
                <h2>💬 Test Chat (Live)</h2>
                <div id="chatBox" class="chat-box"></div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Type your message here... (English or Indonesian)" onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Send</button>
                </div>
                <p style="font-size: 12px; opacity: 0.8;"><em>Try: "Help me write Python code" or "Tulis cerita pendek tentang Jakarta"</em></p>
            </div>
            
            <h2>💡 Features:</h2>
            <ul>
                <li><strong>AI Coding Assistant:</strong> Get help with programming in any language</li>
                <li><strong>Indonesian Novel Writing:</strong> Creative writing in Bahasa Indonesia</li>
                <li><strong>Real-time Chat:</strong> Instant responses via OpenRouter</li>
                <li><strong>Cost Effective:</strong> ~$5-15/month for personal use</li>
            </ul>
            
            <p style="text-align: center; margin-top: 30px; opacity: 0.8;">
                <em>Personal AI Assistant powered by OpenRouter 💕</em>
            </p>
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
                chatBox.scrollTop = chatBox.scrollHeight;
                
                // Add loading message
                chatBox.innerHTML += `<div class="message assistant" id="loading"><strong>Assistant:</strong> ⏳ Thinking...</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    
                    // Remove loading message
                    document.getElementById('loading').remove();
                    
                    // Add AI response
                    chatBox.innerHTML += `<div class="message assistant"><strong>Assistant:</strong> ${data.response || 'Response received!'}</div>`;
                } catch (error) {
                    // Remove loading message
                    document.getElementById('loading').remove();
                    
                    chatBox.innerHTML += `<div class="message assistant"><strong>Assistant:</strong> ❌ Sorry, I'm having trouble connecting. Please check the API configuration.</div>`;
                }
                
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    """Health check endpoint"""
    api_key = os.getenv('LLM_API_KEY', 'NOT_SET')
    return {
        "status": "OK", 
        "message": "OpenHands Backend is running",
        "api_key_configured": api_key != 'NOT_SET',
        "model": os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307')
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Simple chat endpoint with OpenRouter"""
    message = request.message
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Check API key
    api_key = os.getenv('LLM_API_KEY')
    if not api_key:
        return {
            "response": "⚠️ LLM API key not configured. Please set LLM_API_KEY environment variable in HF Spaces settings.",
            "status": "error"
        }
    
    try:
        # Call OpenRouter API
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
                        {
                            "role": "system", 
                            "content": "You are a helpful AI assistant for coding and creative writing. If the user writes in Indonesian, respond in Indonesian. If they write in English, respond in English. Be friendly and helpful."
                        },
                        {"role": "user", "content": message}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                return {"response": ai_response, "status": "success"}
            else:
                return {
                    "response": f"❌ API Error: {response.status_code} - Please check your OpenRouter API key and billing.",
                    "status": "error"
                }
                
    except Exception as e:
        return {
            "response": f"❌ Error: {str(e)}. Please check your OpenRouter API key and internet connection.",
            "status": "error"
        }

@app.get("/novel")
async def novel_interface():
    """Indonesian novel writing interface"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Novel Writing - OpenHands</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 900px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px);
            }
            h1 { text-align: center; color: #ffd700; }
            textarea { 
                width: 100%; 
                height: 200px; 
                padding: 15px; 
                border: none; 
                border-radius: 10px; 
                font-family: inherit; 
                font-size: 14px;
                background: rgba(255,255,255,0.9);
                color: #333;
                resize: vertical;
            }
            button { 
                padding: 12px 24px; 
                background: #ffd700; 
                color: #333; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                margin: 10px 5px;
                font-weight: bold;
                transition: all 0.3s;
            }
            button:hover { 
                background: #ffed4e;
                transform: translateY(-2px);
            }
            .result { 
                margin-top: 20px; 
                padding: 20px; 
                background: rgba(255,255,255,0.1); 
                border-radius: 10px; 
                white-space: pre-wrap; 
                line-height: 1.6;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .templates { 
                display: flex; 
                flex-wrap: wrap; 
                gap: 10px; 
                margin: 15px 0; 
            }
            .template { 
                padding: 8px 16px; 
                background: rgba(255,255,255,0.2); 
                border: none; 
                border-radius: 20px; 
                cursor: pointer; 
                font-size: 12px;
                color: white;
                transition: all 0.3s;
            }
            .template:hover { 
                background: rgba(255,255,255,0.3);
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Indonesian Novel Writing</h1>
            <p>Tulis prompt untuk cerita Anda dalam Bahasa Indonesia:</p>
            
            <div class="templates">
                <button class="template" onclick="setTemplate('Romance')">💕 Romance</button>
                <button class="template" onclick="setTemplate('Adventure')">🗺️ Petualangan</button>
                <button class="template" onclick="setTemplate('Mystery')">🔍 Misteri</button>
                <button class="template" onclick="setTemplate('SciFi')">🚀 Sci-Fi</button>
                <button class="template" onclick="setTemplate('Fantasy')">🧙 Fantasy</button>
                <button class="template" onclick="setTemplate('Drama')">🎭 Drama</button>
                <button class="template" onclick="setTemplate('Comedy')">😄 Komedi</button>
            </div>
            
            <textarea id="promptInput" placeholder="Contoh: Tulis cerita romantis tentang seorang programmer yang jatuh cinta dengan AI assistant di Jakarta..."></textarea>
            <br>
            <button onclick="generateNovel()">✍️ Generate Novel</button>
            <button onclick="clearResult()">🗑️ Clear</button>
            <button onclick="goHome()">🏠 Home</button>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <script>
            function setTemplate(type) {
                const templates = {
                    'Romance': 'Tulis cerita romantis tentang dua orang yang bertemu di kafe Jakarta dan jatuh cinta melalui percakapan tentang teknologi...',
                    'Adventure': 'Ceritakan petualangan seorang penjelajah muda yang menemukan gua tersembunyi di Gunung Bromo...',
                    'Mystery': 'Buat cerita misteri tentang hilangnya artefak kuno dari Museum Nasional Jakarta...',
                    'SciFi': 'Tulis cerita fiksi ilmiah tentang kehidupan manusia di koloni Mars yang didirikan oleh Indonesia tahun 2050...',
                    'Fantasy': 'Ceritakan tentang dunia magis yang tersembunyi di balik air terjun Sekumpul, Bali...',
                    'Drama': 'Buat drama keluarga tentang konflik generasi dalam keluarga Jawa di Solo...',
                    'Comedy': 'Tulis komedi tentang kehidupan mahasiswa IT di Jakarta yang selalu mengalami kejadian lucu...'
                };
                document.getElementById('promptInput').value = templates[type];
            }
            
            async function generateNovel() {
                const prompt = document.getElementById('promptInput').value.trim();
                const resultDiv = document.getElementById('result');
                
                if (!prompt) {
                    alert('Silakan masukkan prompt untuk novel Anda!');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '⏳ Sedang menulis novel Anda... Mohon tunggu...';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: `Sebagai penulis novel Indonesia yang berpengalaman, ${prompt}. Tulis dengan gaya bahasa yang menarik, dialog yang natural, dan deskripsi yang vivid. Buat cerita sepanjang 3-4 paragraf dengan karakter yang kuat dan alur yang menarik. Gunakan Bahasa Indonesia yang baik dan benar.`
                        })
                    });
                    
                    const data = await response.json();
                    resultDiv.innerHTML = data.response || 'Novel berhasil dibuat!';
                } catch (error) {
                    resultDiv.innerHTML = '❌ Error saat membuat novel. Silakan periksa konfigurasi API.';
                }
            }
            
            function clearResult() {
                document.getElementById('result').style.display = 'none';
                document.getElementById('promptInput').value = '';
            }
            
            function goHome() {
                window.location.href = '/';
            }
        </script>
    </body>
    </html>
    """)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Log startup info
    logger.info("🚀 Starting Ultra Simple OpenHands Backend")
    logger.info(f"🔑 API Key: {'✅ Set' if os.getenv('LLM_API_KEY') else '❌ Missing'}")
    logger.info(f"🤖 Model: {os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )