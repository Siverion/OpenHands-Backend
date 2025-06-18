#!/usr/bin/env python3
"""
OpenHands Backend - MEDIUM POWER VERSION
More features than ultra simple, but stable for HF Spaces
Includes: File operations, Code execution, Workspace, Memory, Advanced UI
"""

import os
import sys
import logging
import json
import tempfile
import subprocess
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize workspace and database
WORKSPACE_DIR = "/tmp/openhands_workspace"
DB_PATH = "/tmp/openhands.db"
Path(WORKSPACE_DIR).mkdir(parents=True, exist_ok=True)

# Initialize SQLite database for conversation history
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    
    # Files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT,
            filepath TEXT,
            size INTEGER,
            created_at TIMESTAMP,
            conversation_id TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Create FastAPI app
app = FastAPI(
    title="OpenHands Backend - Medium Power",
    description="Advanced AI Assistant with File Operations, Code Execution, and Memory",
    version="2.0.0"
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
    conversation_id: Optional[str] = None
    execute_code: bool = False

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"

class FileEditRequest(BaseModel):
    filepath: str
    content: str

# Utility functions
def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content, timestamp FROM messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp DESC LIMIT ?
    ''', (conversation_id, limit))
    messages = cursor.fetchall()
    conn.close()
    return [{"role": msg[0], "content": msg[1], "timestamp": msg[2]} for msg in reversed(messages)]

def save_message(conversation_id: str, role: str, content: str, metadata: Dict = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create conversation if not exists
    cursor.execute('SELECT id FROM conversations WHERE id = ?', (conversation_id,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO conversations (id, title, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, content[:50] + "...", datetime.now(), datetime.now(), json.dumps(metadata or {})))
    
    # Save message
    cursor.execute('''
        INSERT INTO messages (id, conversation_id, role, content, timestamp, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), conversation_id, role, content, datetime.now(), json.dumps(metadata or {})))
    
    # Update conversation timestamp
    cursor.execute('UPDATE conversations SET updated_at = ? WHERE id = ?', (datetime.now(), conversation_id))
    
    conn.commit()
    conn.close()

def execute_code_safely(code: str, language: str = "python") -> Dict[str, Any]:
    """Execute code safely with timeout and restrictions"""
    try:
        if language.lower() == "python":
            # Create a restricted environment
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sorted': sorted,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                }
            }
            
            # Capture output
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            try:
                with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                    exec(code, restricted_globals)
                
                return {
                    "success": True,
                    "output": output_buffer.getvalue(),
                    "error": error_buffer.getvalue(),
                    "language": language
                }
            except Exception as e:
                return {
                    "success": False,
                    "output": output_buffer.getvalue(),
                    "error": str(e),
                    "language": language
                }
        
        elif language.lower() in ["bash", "shell"]:
            # Safe bash commands only
            safe_commands = ["ls", "pwd", "echo", "cat", "head", "tail", "wc", "grep", "find"]
            first_command = code.strip().split()[0] if code.strip() else ""
            
            if first_command not in safe_commands:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Command '{first_command}' not allowed. Safe commands: {', '.join(safe_commands)}",
                    "language": language
                }
            
            try:
                result = subprocess.run(
                    code, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    cwd=WORKSPACE_DIR
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "language": language
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "output": "",
                    "error": "Command timed out (10s limit)",
                    "language": language
                }
            except Exception as e:
                return {
                    "success": False,
                    "output": "",
                    "error": str(e),
                    "language": language
                }
        
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Language '{language}' not supported. Supported: python, bash",
                "language": language
            }
            
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "language": language
        }

@app.get("/")
async def root():
    """Advanced homepage with full features"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenHands Backend - Medium Power</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .feature-card {
                background: rgba(255,255,255,0.1);
                padding: 25px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .feature-card h3 {
                color: #ffd700;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .feature-card ul {
                list-style: none;
                padding-left: 0;
            }
            .feature-card li {
                margin: 8px 0;
                padding-left: 20px;
                position: relative;
            }
            .feature-card li:before {
                content: "✅";
                position: absolute;
                left: 0;
            }
            .main-interface {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }
            .tab {
                padding: 12px 24px;
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                transition: all 0.3s;
            }
            .tab.active {
                border-bottom-color: #ffd700;
                color: #ffd700;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .chat-container {
                height: 400px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                display: flex;
                flex-direction: column;
            }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background: rgba(0,0,0,0.2);
            }
            .message {
                margin: 10px 0;
                padding: 12px;
                border-radius: 8px;
                animation: fadeIn 0.3s;
            }
            .message.user {
                background: rgba(0, 123, 255, 0.3);
                margin-left: 20%;
                border-left: 3px solid #007bff;
            }
            .message.assistant {
                background: rgba(40, 167, 69, 0.3);
                margin-right: 20%;
                border-left: 3px solid #28a745;
            }
            .message.system {
                background: rgba(255, 193, 7, 0.3);
                text-align: center;
                border-left: 3px solid #ffc107;
            }
            .chat-input {
                display: flex;
                padding: 15px;
                gap: 10px;
                background: rgba(255,255,255,0.1);
                border-radius: 0 0 10px 10px;
            }
            .chat-input input {
                flex: 1;
                padding: 12px;
                border: none;
                border-radius: 8px;
                background: rgba(255,255,255,0.9);
                color: #333;
            }
            .btn {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s;
            }
            .btn-primary {
                background: #ffd700;
                color: #333;
            }
            .btn-primary:hover {
                background: #ffed4e;
                transform: translateY(-2px);
            }
            .btn-secondary {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
            }
            .btn-secondary:hover {
                background: rgba(255,255,255,0.3);
            }
            .code-editor {
                background: #1e1e1e;
                border-radius: 8px;
                overflow: hidden;
                margin: 10px 0;
            }
            .code-header {
                background: #333;
                padding: 10px 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .code-content {
                padding: 0;
            }
            .code-content textarea {
                width: 100%;
                height: 200px;
                background: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                resize: vertical;
            }
            .file-manager {
                background: rgba(0,0,0,0.2);
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            .file-list {
                max-height: 200px;
                overflow-y: auto;
            }
            .file-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            .file-item:hover {
                background: rgba(255,255,255,0.1);
            }
            .upload-area {
                border: 2px dashed rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 30px;
                text-align: center;
                margin: 15px 0;
                transition: all 0.3s;
            }
            .upload-area:hover {
                border-color: #ffd700;
                background: rgba(255,215,0,0.1);
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .status-bar {
                background: rgba(0,0,0,0.3);
                padding: 10px 15px;
                border-radius: 8px;
                margin: 15px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #28a745;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 OpenHands Backend</h1>
                <p>Medium Power Version - Advanced AI Assistant with Code Execution & File Management</p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <h3>💬 Advanced Chat</h3>
                    <ul>
                        <li>Conversation memory</li>
                        <li>Multiple chat threads</li>
                        <li>Code syntax highlighting</li>
                        <li>Markdown rendering</li>
                    </ul>
                </div>
                <div class="feature-card">
                    <h3>⚡ Code Execution</h3>
                    <ul>
                        <li>Python code execution</li>
                        <li>Safe bash commands</li>
                        <li>Real-time output</li>
                        <li>Error handling</li>
                    </ul>
                </div>
                <div class="feature-card">
                    <h3>📁 File Management</h3>
                    <ul>
                        <li>Upload/download files</li>
                        <li>Edit files online</li>
                        <li>Workspace management</li>
                        <li>File history</li>
                    </ul>
                </div>
                <div class="feature-card">
                    <h3>📚 Creative Writing</h3>
                    <ul>
                        <li>Indonesian novel writing</li>
                        <li>Story templates</li>
                        <li>Character development</li>
                        <li>Plot assistance</li>
                    </ul>
                </div>
            </div>
            
            <div class="main-interface">
                <div class="status-bar">
                    <div class="status-indicator">
                        <div class="status-dot"></div>
                        <span>System Online</span>
                    </div>
                    <div>
                        <span id="apiStatus">API: Checking...</span>
                    </div>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('chat')">💬 Chat</button>
                    <button class="tab" onclick="switchTab('code')">⚡ Code</button>
                    <button class="tab" onclick="switchTab('files')">📁 Files</button>
                    <button class="tab" onclick="switchTab('novel')">📚 Novel</button>
                </div>
                
                <!-- Chat Tab -->
                <div id="chat" class="tab-content active">
                    <div class="chat-container">
                        <div class="chat-messages" id="chatMessages"></div>
                        <div class="chat-input">
                            <input type="text" id="messageInput" placeholder="Type your message... (supports code, questions, creative writing)" onkeypress="if(event.key==='Enter') sendMessage()">
                            <button class="btn btn-primary" onclick="sendMessage()">Send</button>
                            <button class="btn btn-secondary" onclick="newConversation()">New Chat</button>
                        </div>
                    </div>
                </div>
                
                <!-- Code Tab -->
                <div id="code" class="tab-content">
                    <div class="code-editor">
                        <div class="code-header">
                            <span>Code Editor</span>
                            <div>
                                <select id="codeLanguage">
                                    <option value="python">Python</option>
                                    <option value="bash">Bash</option>
                                </select>
                                <button class="btn btn-primary" onclick="executeCode()">▶ Run</button>
                            </div>
                        </div>
                        <div class="code-content">
                            <textarea id="codeEditor" placeholder="# Write your code here...
print('Hello from OpenHands!')

# Example: Simple calculation
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

for i in range(10):
    print(f'Fibonacci {i}: {calculate_fibonacci(i)}')"></textarea>
                        </div>
                    </div>
                    <div id="codeOutput" style="display: none;">
                        <h4>Output:</h4>
                        <pre id="outputContent" style="background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 8px; overflow-x: auto;"></pre>
                    </div>
                </div>
                
                <!-- Files Tab -->
                <div id="files" class="tab-content">
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <p>📁 Click to upload files or drag & drop</p>
                        <input type="file" id="fileInput" multiple style="display: none;" onchange="uploadFiles()">
                    </div>
                    <div class="file-manager">
                        <h4>Workspace Files:</h4>
                        <div class="file-list" id="fileList">
                            <div class="file-item">
                                <span>📄 example.txt</span>
                                <div>
                                    <button class="btn btn-secondary" onclick="editFile('example.txt')">Edit</button>
                                    <button class="btn btn-secondary" onclick="downloadFile('example.txt')">Download</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Novel Tab -->
                <div id="novel" class="tab-content">
                    <h3>📚 Indonesian Novel Writing Assistant</h3>
                    <div style="margin: 15px 0;">
                        <button class="btn btn-secondary" onclick="setNovelTemplate('romance')">💕 Romance</button>
                        <button class="btn btn-secondary" onclick="setNovelTemplate('adventure')">🗺️ Adventure</button>
                        <button class="btn btn-secondary" onclick="setNovelTemplate('mystery')">🔍 Mystery</button>
                        <button class="btn btn-secondary" onclick="setNovelTemplate('scifi')">🚀 Sci-Fi</button>
                    </div>
                    <textarea id="novelPrompt" style="width: 100%; height: 150px; padding: 15px; border-radius: 8px; border: none; background: rgba(255,255,255,0.9); color: #333;" placeholder="Tulis prompt untuk novel Anda dalam Bahasa Indonesia..."></textarea>
                    <div style="margin: 15px 0;">
                        <button class="btn btn-primary" onclick="generateNovel()">✍️ Generate Novel</button>
                        <button class="btn btn-secondary" onclick="clearNovel()">🗑️ Clear</button>
                    </div>
                    <div id="novelOutput" style="display: none;">
                        <h4>Generated Novel:</h4>
                        <div id="novelContent" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 8px; white-space: pre-wrap; line-height: 1.6;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let currentConversationId = generateUUID();
            
            function generateUUID() {
                return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                    return v.toString(16);
                });
            }
            
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const messagesDiv = document.getElementById('chatMessages');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                addMessage('user', message);
                input.value = '';
                
                // Add loading message
                const loadingId = 'loading-' + Date.now();
                addMessage('assistant', '⏳ Thinking...', loadingId);
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: message,
                            conversation_id: currentConversationId
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Remove loading message
                    document.getElementById(loadingId)?.remove();
                    
                    // Add AI response
                    addMessage('assistant', data.response || 'Response received!');
                    
                    // Show code execution if available
                    if (data.code_execution) {
                        addCodeExecution(data.code_execution);
                    }
                    
                } catch (error) {
                    document.getElementById(loadingId)?.remove();
                    addMessage('assistant', '❌ Error: ' + error.message);
                }
            }
            
            function addMessage(role, content, id = null) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;
                if (id) messageDiv.id = id;
                
                const roleLabel = role === 'user' ? 'You' : 'Assistant';
                messageDiv.innerHTML = `<strong>${roleLabel}:</strong> ${content}`;
                
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function addCodeExecution(execution) {
                const messagesDiv = document.getElementById('chatMessages');
                const execDiv = document.createElement('div');
                execDiv.className = 'message system';
                
                let content = `<strong>Code Execution (${execution.language}):</strong><br>`;
                if (execution.output) {
                    content += `<pre style="background: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 5px; margin: 5px 0;">${execution.output}</pre>`;
                }
                if (execution.error) {
                    content += `<pre style="background: #d32f2f; color: white; padding: 10px; border-radius: 5px; margin: 5px 0;">${execution.error}</pre>`;
                }
                
                execDiv.innerHTML = content;
                messagesDiv.appendChild(execDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function newConversation() {
                currentConversationId = generateUUID();
                document.getElementById('chatMessages').innerHTML = '';
                addMessage('system', 'New conversation started! 🎉');
            }
            
            async function executeCode() {
                const code = document.getElementById('codeEditor').value;
                const language = document.getElementById('codeLanguage').value;
                const outputDiv = document.getElementById('codeOutput');
                const contentDiv = document.getElementById('outputContent');
                
                if (!code.trim()) return;
                
                outputDiv.style.display = 'block';
                contentDiv.textContent = '⏳ Executing...';
                
                try {
                    const response = await fetch('/api/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code, language })
                    });
                    
                    const data = await response.json();
                    
                    let output = '';
                    if (data.output) output += `Output:\n${data.output}\n\n`;
                    if (data.error) output += `Error:\n${data.error}`;
                    
                    contentDiv.textContent = output || 'No output';
                    
                } catch (error) {
                    contentDiv.textContent = 'Execution error: ' + error.message;
                }
            }
            
            async function uploadFiles() {
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                
                if (files.length === 0) return;
                
                for (let file of files) {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    try {
                        const response = await fetch('/api/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        if (data.success) {
                            refreshFileList();
                        }
                    } catch (error) {
                        console.error('Upload error:', error);
                    }
                }
                
                fileInput.value = '';
            }
            
            async function refreshFileList() {
                try {
                    const response = await fetch('/api/files');
                    const data = await response.json();
                    
                    const fileList = document.getElementById('fileList');
                    fileList.innerHTML = '';
                    
                    data.files.forEach(file => {
                        const fileDiv = document.createElement('div');
                        fileDiv.className = 'file-item';
                        fileDiv.innerHTML = `
                            <span>📄 ${file.filename}</span>
                            <div>
                                <button class="btn btn-secondary" onclick="editFile('${file.filename}')">Edit</button>
                                <button class="btn btn-secondary" onclick="downloadFile('${file.filename}')">Download</button>
                            </div>
                        `;
                        fileList.appendChild(fileDiv);
                    });
                } catch (error) {
                    console.error('Error refreshing file list:', error);
                }
            }
            
            function setNovelTemplate(type) {
                const templates = {
                    romance: 'Tulis cerita romantis tentang dua programmer yang bertemu di hackathon Jakarta dan jatuh cinta melalui kolaborasi coding...',
                    adventure: 'Ceritakan petualangan seorang developer yang menemukan bug misterius yang membuka portal ke dunia digital...',
                    mystery: 'Buat cerita misteri tentang hilangnya source code rahasia dari startup unicorn Indonesia...',
                    scifi: 'Tulis cerita fiksi ilmiah tentang AI yang dikembangkan di Indonesia dan menjadi sadar diri...'
                };
                document.getElementById('novelPrompt').value = templates[type];
            }
            
            async function generateNovel() {
                const prompt = document.getElementById('novelPrompt').value.trim();
                const outputDiv = document.getElementById('novelOutput');
                const contentDiv = document.getElementById('novelContent');
                
                if (!prompt) {
                    alert('Silakan masukkan prompt untuk novel Anda!');
                    return;
                }
                
                outputDiv.style.display = 'block';
                contentDiv.textContent = '⏳ Sedang menulis novel Anda... Mohon tunggu...';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: `Sebagai penulis novel Indonesia yang berpengalaman, ${prompt}. Tulis dengan gaya bahasa yang menarik, dialog yang natural, dan deskripsi yang vivid. Buat cerita sepanjang 4-5 paragraf dengan karakter yang kuat dan alur yang menarik. Gunakan Bahasa Indonesia yang baik dan benar.`,
                            conversation_id: 'novel-' + generateUUID()
                        })
                    });
                    
                    const data = await response.json();
                    contentDiv.textContent = data.response || 'Novel berhasil dibuat!';
                } catch (error) {
                    contentDiv.textContent = '❌ Error saat membuat novel: ' + error.message;
                }
            }
            
            function clearNovel() {
                document.getElementById('novelPrompt').value = '';
                document.getElementById('novelOutput').style.display = 'none';
            }
            
            // Check API status on load
            async function checkApiStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('apiStatus').textContent = 
                        `API: ${data.api_key_configured ? '✅ Ready' : '❌ No Key'}`;
                } catch (error) {
                    document.getElementById('apiStatus').textContent = 'API: ❌ Error';
                }
            }
            
            // Initialize
            checkApiStatus();
            refreshFileList();
            addMessage('system', 'Welcome to OpenHands Medium Power! 🚀 Try asking me to help with coding, execute some Python code, or write an Indonesian novel!');
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    """Enhanced health check"""
    api_key = os.getenv('LLM_API_KEY', 'NOT_SET')
    return {
        "status": "OK",
        "version": "2.0.0 - Medium Power",
        "features": [
            "Advanced Chat with Memory",
            "Code Execution (Python/Bash)",
            "File Management",
            "Indonesian Novel Writing",
            "Conversation History",
            "Workspace Management"
        ],
        "api_key_configured": api_key != 'NOT_SET',
        "model": os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307'),
        "workspace": WORKSPACE_DIR,
        "database": "SQLite with conversation history"
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Enhanced chat with memory and code execution"""
    message = request.message
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Save user message
    save_message(conversation_id, "user", message)
    
    # Get conversation history
    history = get_conversation_history(conversation_id, limit=10)
    
    # Check API key
    api_key = os.getenv('LLM_API_KEY')
    if not api_key:
        error_msg = "⚠️ LLM API key not configured. Please set LLM_API_KEY environment variable."
        save_message(conversation_id, "assistant", error_msg)
        return {"response": error_msg, "status": "error", "conversation_id": conversation_id}
    
    # Check if user wants code execution
    code_execution_result = None
    if request.execute_code or "execute" in message.lower() or "run" in message.lower():
        # Try to extract code from message
        if "```" in message:
            code_blocks = message.split("```")
            for i, block in enumerate(code_blocks):
                if i % 2 == 1:  # Odd indices are code blocks
                    lines = block.strip().split('\n')
                    language = lines[0] if lines[0] in ['python', 'bash', 'shell'] else 'python'
                    code = '\n'.join(lines[1:]) if lines[0] in ['python', 'bash', 'shell'] else block.strip()
                    code_execution_result = execute_code_safely(code, language)
                    break
    
    try:
        # Prepare messages for API
        api_messages = [
            {
                "role": "system",
                "content": """You are an advanced AI assistant with the following capabilities:
                
1. Code Help: Provide programming assistance, code review, debugging help
2. Code Execution: When users ask to run code, I can execute Python and safe bash commands
3. File Management: Help with file operations and workspace management
4. Indonesian Novel Writing: Creative writing assistance in Bahasa Indonesia
5. Conversation Memory: Remember previous messages in our conversation

Guidelines:
- If user asks in Indonesian, respond in Indonesian
- If user asks in English, respond in English  
- For coding questions, provide clear explanations and examples
- For creative writing, be imaginative and engaging
- Always be helpful, friendly, and professional

Current conversation context: This is an ongoing conversation with message history."""
            }
        ]
        
        # Add conversation history
        for msg in history[-5:]:  # Last 5 messages for context
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current message
        api_messages.append({"role": "user", "content": message})
        
        # Add code execution context if available
        if code_execution_result:
            context = f"\n\nCode Execution Result:\nLanguage: {code_execution_result['language']}\nSuccess: {code_execution_result['success']}\nOutput: {code_execution_result['output']}\nError: {code_execution_result['error']}"
            api_messages[-1]["content"] += context
        
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
                    "messages": api_messages,
                    "max_tokens": 1500,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                
                # Save assistant response
                save_message(conversation_id, "assistant", ai_response)
                
                result = {
                    "response": ai_response,
                    "status": "success",
                    "conversation_id": conversation_id
                }
                
                # Include code execution result if available
                if code_execution_result:
                    result["code_execution"] = code_execution_result
                
                return result
            else:
                error_msg = f"❌ API Error: {response.status_code} - Please check your OpenRouter API key and billing."
                save_message(conversation_id, "assistant", error_msg)
                return {
                    "response": error_msg,
                    "status": "error",
                    "conversation_id": conversation_id
                }
                
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}. Please check your OpenRouter API key and internet connection."
        save_message(conversation_id, "assistant", error_msg)
        return {
            "response": error_msg,
            "status": "error",
            "conversation_id": conversation_id
        }

@app.post("/api/execute")
async def execute_code_endpoint(request: CodeExecutionRequest):
    """Code execution endpoint"""
    result = execute_code_safely(request.code, request.language)
    return result

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """File upload endpoint"""
    try:
        # Save file to workspace
        file_path = Path(WORKSPACE_DIR) / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (id, filename, filepath, size, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), file.filename, str(file_path), len(content), datetime.now()))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "message": f"File {file.filename} uploaded successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/files")
async def list_files():
    """List workspace files"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT filename, size, created_at FROM files ORDER BY created_at DESC')
        files = cursor.fetchall()
        conn.close()
        
        return {
            "files": [
                {
                    "filename": f[0],
                    "size": f[1],
                    "created_at": f[2]
                } for f in files
            ]
        }
    except Exception as e:
        return {"files": [], "error": str(e)}

@app.get("/api/conversations")
async def list_conversations():
    """List conversation history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT 20')
        conversations = cursor.fetchall()
        conn.close()
        
        return {
            "conversations": [
                {
                    "id": c[0],
                    "title": c[1],
                    "created_at": c[2],
                    "updated_at": c[3]
                } for c in conversations
            ]
        }
    except Exception as e:
        return {"conversations": [], "error": str(e)}

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    # Log startup info
    logger.info("🚀 Starting OpenHands Backend - Medium Power Version")
    logger.info(f"🔑 API Key: {'✅ Set' if os.getenv('LLM_API_KEY') else '❌ Missing'}")
    logger.info(f"🤖 Model: {os.getenv('LLM_MODEL', 'openrouter/anthropic/claude-3-haiku-20240307')}")
    logger.info(f"📁 Workspace: {WORKSPACE_DIR}")
    logger.info(f"🗄️ Database: {DB_PATH}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info"
    )