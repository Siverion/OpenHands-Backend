# 🔑 COMPLETE ENVIRONMENT VARIABLES FOR HUGGING FACE SPACES

## 🚨 **COPY THESE EXACT ENVIRONMENT VARIABLES TO YOUR HF SPACE**

---

## 📋 **HOW TO SET ENVIRONMENT VARIABLES IN HF SPACES:**

1. **Go to your HF Space** (e.g., https://huggingface.co/spaces/your-username/your-space-name)
2. **Click "Settings"** tab
3. **Scroll down to "Variables"** section
4. **Click "New variable"** for each variable below
5. **Copy-paste** the exact names and values

---

## 🔑 **REQUIRED ENVIRONMENT VARIABLES**

### **1. LLM API Configuration (REQUIRED)**
```
Variable Name: LLM_API_KEY
Variable Value: your_openrouter_api_key_here
Description: Your OpenRouter API key (starts with sk-or-v1-)
```

```
Variable Name: LLM_MODEL
Variable Value: openrouter/anthropic/claude-3-haiku-20240307
Description: AI model for cost-effective personal use
```

```
Variable Name: LLM_BASE_URL
Variable Value: https://openrouter.ai/api/v1
Description: OpenRouter API endpoint
```

### **2. Environment Configuration (REQUIRED)**
```
Variable Name: ENVIRONMENT
Variable Value: production
Description: Set environment to production mode
```

```
Variable Name: HF_SPACES
Variable Value: 1
Description: Enable Hugging Face Spaces mode
```

```
Variable Name: RUNTIME
Variable Value: local
Description: Use local runtime (no Docker needed)
```

### **3. Server Configuration (REQUIRED)**
```
Variable Name: HOST
Variable Value: 0.0.0.0
Description: Allow connections from any host
```

```
Variable Name: PORT
Variable Value: 7860
Description: Default HF Spaces port
```

### **4. Security Configuration (OPTIONAL)**
```
Variable Name: SECRET_KEY
Variable Value: your-secret-key-here-make-it-random-and-long
Description: Secret key for session security (generate random string)
```

### **5. OpenHands Configuration (OPTIONAL)**
```
Variable Name: WORKSPACE_BASE
Variable Value: /tmp/workspace
Description: Workspace directory for file operations
```

```
Variable Name: MAX_ITERATIONS
Variable Value: 30
Description: Maximum iterations for AI agent tasks
```

```
Variable Name: MAX_BUDGET_PER_TASK
Variable Value: 10.0
Description: Maximum cost per task in USD
```

---

## 🎯 **RECOMMENDED MODEL CONFIGURATIONS**

### **💰 Budget Option (Recommended for Personal Use):**
```
LLM_MODEL: openrouter/anthropic/claude-3-haiku-20240307
Cost: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
Perfect for: Daily coding help, novel writing, file management
Monthly cost: ~$5-10 for personal use
```

### **⚖️ Balanced Option:**
```
LLM_MODEL: openrouter/anthropic/claude-3-5-sonnet-20241022
Cost: ~$3 per 1M input tokens, ~$15 per 1M output tokens
Perfect for: Complex coding, detailed analysis, advanced tasks
Monthly cost: ~$15-25 for regular use
```

### **🚀 Premium Option:**
```
LLM_MODEL: openrouter/openai/gpt-4o
Cost: ~$5 per 1M input tokens, ~$15 per 1M output tokens
Perfect for: Professional development, complex projects
Monthly cost: ~$20-40 for heavy use
```

### **💻 Coding Specialist:**
```
LLM_MODEL: openrouter/deepseek/deepseek-coder
Cost: ~$0.14 per 1M input tokens, ~$0.28 per 1M output tokens
Perfect for: Pure coding assistance, debugging, code review
Monthly cost: ~$3-8 for coding-focused use
```

### **🇮🇩 Indonesian Language Optimized:**
```
LLM_MODEL: openrouter/anthropic/claude-3-haiku-20240307
Best for: Indonesian novel writing, Bahasa Indonesia conversations
Note: Claude models have excellent Indonesian language support
```

---

## 🔑 **HOW TO GET OPENROUTER API KEY:**

### **Step 1: Create Account**
1. Go to: https://openrouter.ai/
2. Click "Sign Up" 
3. Use email (no Google login required!)
4. Verify your email

### **Step 2: Add Payment Method**
1. Go to "Billing" section
2. Add credit card or payment method
3. Add $10-20 credit (will last months for personal use)

### **Step 3: Create API Key**
1. Go to "Keys" section
2. Click "Create Key"
3. Name it: "HF-Spaces-OpenHands"
4. Copy the key (starts with `sk-or-v1-`)
5. **SAVE IT SECURELY** - you can't see it again!

### **Step 4: Test API Key**
```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer your-api-key-here"
```

---

## 📋 **COMPLETE ENVIRONMENT VARIABLES LIST (COPY-PASTE READY)**

```
# === REQUIRED VARIABLES ===
LLM_API_KEY=your_openrouter_api_key_here
LLM_MODEL=openrouter/anthropic/claude-3-haiku-20240307
LLM_BASE_URL=https://openrouter.ai/api/v1
ENVIRONMENT=production
HF_SPACES=1
RUNTIME=local
HOST=0.0.0.0
PORT=7860

# === OPTIONAL VARIABLES ===
SECRET_KEY=your-random-secret-key-here-make-it-long-and-secure
WORKSPACE_BASE=/tmp/workspace
MAX_ITERATIONS=30
MAX_BUDGET_PER_TASK=10.0
```

---

## 🧪 **TESTING YOUR SETUP**

### **After setting all variables, test these endpoints:**

### **1. Health Check:**
```
https://your-space-name.hf.space/health
Expected: "OK"
```

### **2. HF Status:**
```
https://your-space-name.hf.space/api/hf/status
Expected: {"status": "running", "environment": "production"}
```

### **3. Test Chat:**
```
https://your-space-name.hf.space/test-chat
Expected: Chat interface with working AI responses
```

### **4. API Documentation:**
```
https://your-space-name.hf.space/docs
Expected: Swagger UI with all available endpoints
```

### **5. Novel Writing (Indonesian):**
```
https://your-space-name.hf.space/novel/write
Expected: Indonesian novel writing interface
```

---

## 🚨 **TROUBLESHOOTING ENVIRONMENT VARIABLES**

### **Problem: "LLM API key not configured"**
```
Solution: Make sure LLM_API_KEY is set correctly
Check: Variable name is exactly "LLM_API_KEY" (case sensitive)
Check: Value starts with "sk-or-v1-"
```

### **Problem: "This conversation does not exist"**
```
Solution: Check all required variables are set
Missing: Usually ENVIRONMENT, HF_SPACES, or RUNTIME
Fix: Set all required variables from the list above
```

### **Problem: "Server won't start"**
```
Solution: Check HOST and PORT variables
Fix: HOST=0.0.0.0, PORT=7860
```

### **Problem: "API calls failing"**
```
Solution: Check LLM_BASE_URL and LLM_MODEL
Fix: Use exact values from the list above
```

### **Problem: "Permission denied"**
```
Solution: Check OpenRouter API key and billing
Fix: Ensure you have credit in your OpenRouter account
```

---

## 💰 **COST ESTIMATION**

### **Personal Use (Recommended Setup):**
```
Model: claude-3-haiku-20240307
Daily usage: ~10,000 tokens
Monthly cost: ~$2.50
Perfect for: Coding help, novel writing, file management
```

### **Regular Use:**
```
Model: claude-3-haiku-20240307
Daily usage: ~50,000 tokens  
Monthly cost: ~$12.50
Perfect for: Daily development work, creative writing
```

### **Heavy Use:**
```
Model: claude-3-5-sonnet-20241022
Daily usage: ~100,000 tokens
Monthly cost: ~$90
Perfect for: Professional development, complex projects
```

### **Token Usage Examples:**
```
Simple question: ~100 tokens = $0.000025
Code review: ~2,000 tokens = $0.0005
Novel chapter: ~5,000 tokens = $0.00125
Complex debugging: ~10,000 tokens = $0.0025
```

---

## 🎯 **RECOMMENDED SETUP FOR PERSONAL USE**

### **For You and Your Girlfriend:**
```
LLM_API_KEY=your_openrouter_key
LLM_MODEL=openrouter/anthropic/claude-3-haiku-20240307
LLM_BASE_URL=https://openrouter.ai/api/v1
ENVIRONMENT=production
HF_SPACES=1
RUNTIME=local
HOST=0.0.0.0
PORT=7860
SECRET_KEY=make-this-a-long-random-string-for-security
MAX_BUDGET_PER_TASK=5.0
```

### **Expected Monthly Cost: $5-15**
- Perfect for personal coding assistance
- Great for Indonesian novel writing
- Excellent for file management
- Cost-effective for daily use

---

## 🎊 **FINAL CHECKLIST**

### **Before Deployment:**
- ✅ OpenRouter account created
- ✅ API key generated and saved
- ✅ Payment method added to OpenRouter
- ✅ $10-20 credit added to account

### **In HF Spaces Settings:**
- ✅ All required variables set
- ✅ Variable names exactly as shown (case sensitive)
- ✅ LLM_API_KEY starts with "sk-or-v1-"
- ✅ All values copied correctly

### **After Deployment:**
- ✅ Health endpoint returns "OK"
- ✅ API docs accessible at /docs
- ✅ Test chat working
- ✅ Novel writing responding in Indonesian
- ✅ No error messages in logs

---

## 🚀 **READY TO DEPLOY!**

**With these environment variables set correctly, your OpenHands backend will:**
- ✅ Start without any import errors
- ✅ Connect to OpenRouter API successfully  
- ✅ Provide AI coding assistance
- ✅ Generate Indonesian novels
- ✅ Handle file management
- ✅ Run cost-effectively (~$5-15/month)

**Copy all the required variables above to your HF Space and enjoy your personal AI assistant!** 🤖💕

---

**Need help? The complete troubleshooting guide is in COMPLETE_AI_ASSISTANT_PROMPT.md** 📋✨