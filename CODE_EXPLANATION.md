# Code Explanation Document

This document explains all the code changes and answers your questions.

## Table of Contents
1. [Job ID Generation](#1-job-id-generation)
2. [Agent/Runner Event Loop](#2-agentrunner-event-loop)
3. [Code Extraction](#3-code-extraction)
4. [Language Detection](#4-language-detection)
5. [Result Flow](#5-result-flow)
6. [Backend URL Configuration](#6-backend-url-configuration)
7. [Complete Flow Explanation](#7-complete-flow-explanation)

---

## 1. Job ID Generation

### Question: Why generate unique job_id when Cloud Run makes one?

**Answer:** Cloud Run generates an **execution ID** (internal to Cloud Run), but we need our own **job_id** to:
- Track results in our backend database
- Link frontend requests to agent results
- Provide a simple identifier for users

**Cloud Run's ID vs Our ID:**
```python
# Cloud Run's ID (internal, complex)
# Format: projects/xxx/locations/yyy/jobs/zzz/executions/abc-123-def

# Our ID (simple, for our system)
# Format: "550e8400-e29b-41d4-a716-446655440000" (UUID)
```

**Why both?**
- Cloud Run ID: Used by Google Cloud to manage the job execution
- Our job_id: Used by our application to track and retrieve results

---

## 2. Agent/Runner Event Loop

### Question: Where are yields/emits in our code?

**Answer:** The yields/emits happen **inside ADK's framework**, not in your code. Here's what's happening:

### How It Actually Works:

```python
# Your code (main.py line 63-67)
events = runner.run_async(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=content
)

# Behind the scenes (inside ADK):
# 1. Runner calls root_agent.run_async()
# 2. root_agent internally yields events (you don't see this)
# 3. Runner receives events and processes them
# 4. You iterate over the events with async for
```

### What You See vs What Happens:

**What You See:**
```python
async for event in events:
    if event.is_final_response():
        response_text = event.content.parts[0].text
```

**What Happens Inside ADK:**
```python
# Inside root_agent (you don't write this):
async def run_async(context, new_message):
    # Agent processes
    yield Event(content="...", actions=...)  # ← Yield happens here
    # Runner processes event
    # Agent resumes
    yield Event(content="...", is_final=True)  # ← Another yield
```

### The Event Loop (Simplified):

```
1. runner.run_async() called
   ↓
2. Runner → root_agent.run_async()
   ↓
3. root_agent processes (internally yields events)
   ↓
4. Events come back to you via async for loop
   ↓
5. You process events (line 71-75)
   ↓
6. When agent finishes, loop ends
```

**Key Point:** You don't write `yield` - ADK agents do it internally. You just consume the events.

### Documentation Reference:
- [ADK Runtime - Event Loop](https://google.github.io/adk-docs/runtime/#the-heartbeat-the-event-loop---inner-workings)
- [ADK Runtime - Step by Step](https://google.github.io/adk-docs/runtime/#how-it-works-a-simplified-invocation)

---

## 3. Code Extraction

### Question: How does code extraction work? Where to learn?

**Answer:** Uses **Regular Expressions (Regex)** to find patterns in text.

### Learning Resources:

1. **Python Regex Tutorial (Official):**
   - https://docs.python.org/3/library/re.html
   - https://docs.python.org/3/howto/regex.html

2. **Interactive Regex Learning:**
   - https://regex101.com/ - Test patterns online
   - https://regexr.com/ - Another great tool

3. **YouTube Tutorials:**
   - Search: "Python regex tutorial"
   - Search: "Regex basics for beginners"

### How Our Extraction Works:

```python
# Pattern 1: Find "OLD CODE:" followed by code block
old_code_match = re.search(
    r'(?:OLD CODE|old code|Before):[\s\S]*?```(?:\w+)?\n([\s\S]*?)```',
    response,
    re.IGNORECASE
)
# Explanation:
# - (?:OLD CODE|...) - Match these keywords
# - [\s\S]*? - Match anything (including newlines)
# - ```(?:\w+)?\n - Match ```python or ```
# - ([\s\S]*?) - CAPTURE the code inside (group 1)
# - ``` - Match closing ```

# Pattern 2: Find all code blocks
code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', response)
# Explanation:
# - ```(\w+)? - Optional language name
# - \n - Newline
# - ([\s\S]*?) - CAPTURE code content
# - ``` - Closing backticks
```

### Mindset for Writing Regex:

1. **Identify the pattern:** What does the text look like?
   - Example: "OLD CODE: ... ```python\ncode here\n```"

2. **Break it down:**
   - "OLD CODE:" - literal text
   - "..." - anything
   - "```python\n" - code block start
   - "code here" - **what we want to capture**
   - "```" - code block end

3. **Write the pattern:**
   - Use `()` for capturing groups
   - Use `(?:)` for non-capturing groups
   - Use `[\s\S]*?` for "any character including newlines"

4. **Test it:**
   - Use regex101.com to test
   - Try with different examples

### Formula for Code Extraction:

```python
def extract_code(text):
    # Step 1: Try specific patterns (most reliable)
    pattern1 = r'OLD CODE:.*?```(\w+)?\n(.*?)```'
    match1 = re.search(pattern1, text, re.DOTALL)
    
    # Step 2: Try generic patterns (fallback)
    pattern2 = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern2, text, re.DOTALL)
    
    # Step 3: Return extracted code
    if match1:
        return match1.group(2)  # Captured code
    elif matches:
        return matches[0][1]  # First code block
    return ""
```

---

## 4. Language Detection

### Question: Why default to "python" when repo can be any language?

**Answer:** It's a **fallback default**, not a hardcoded value. The code actually tries to detect the language:

```python
# Line 94: Default (fallback only)
"language": "python",  # ← Only used if detection fails

# Line 106-108: Detection from code block
lang_match = re.search(r'```(\w+)', new_code_match.group(0))
if lang_match:
    result["language"] = lang_match.group(1).lower()  # ← Detected!

# Example:
# Input: ```javascript\nconst x = 1;\n```
# Output: language = "javascript" ✅
```

**The logic:**
1. Try to detect from code blocks → if found, use it
2. If detection fails → fallback to "python"
3. Better to have a default than empty string

**Why "python"?**
- Common default
- Won't break the editor
- Can be changed to any other default if needed

---

## 5. Result Flow

### Question: Where is the result caught?

**Answer:** Results are caught at **line 162** in `main.py`:

```python
# Line 162: Run agent and CAPTURE result
result = asyncio.run(run_agent_async(...))
#                  ↑
# This returns the dict from line 83-87

# The return comes from run_agent_async() (line 83-87):
return {
    "status": "completed",
    "final_response": final_response or "",
    "code_changes": code_changes
}

# Then used at line 175-177:
json={
    "status": result.get("status"),  # ← From return dict
    "final_response": result.get("final_response"),  # ← From return dict
    "code_changes": result.get("code_changes", {})  # ← From return dict
}
```

**Flow:**
```
Line 162: result = asyncio.run(run_agent_async(...))
           ↓
Line 83-87: run_agent_async() returns dict
           ↓
Line 162: result variable holds the dict
           ↓
Line 175-177: Use result.get() to send to backend
```

---

## 6. Backend URL Configuration

### Question: Backend deployed on Render - how to configure URL?

**Answer:** Set `BACKEND_URL` environment variable in Cloud Run Job.

**For Render Deployment:**

1. **Get your Render backend URL:**
   - Format: `https://your-backend.onrender.com`
   - Or: `https://your-backend-name.render.com`

2. **Set it in Cloud Run Job configuration:**
   ```python
   # In backend/services/job.py line 50
   run_v2.EnvVar(
       name="BACKEND_URL",
       value=os.getenv("BACKEND_URL", "https://your-backend.onrender.com")
   )
   ```

3. **Or set as environment variable in your backend service:**
   - Add `BACKEND_URL=https://your-backend.onrender.com` to your Render environment variables
   - Then it will be picked up automatically

**Current Code:**
```python
# Line 50 in job.py
run_v2.EnvVar(
    name="BACKEND_URL",
    value=os.getenv("BACKEND_URL", "http://localhost:8000")  # ← Change default
)
```

**Better Solution (Update config.py):**
```python
# backend/core/config.py
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-backend.onrender.com")

# Then in job.py:
from core.config import BACKEND_URL
run_v2.EnvVar(name="BACKEND_URL", value=BACKEND_URL)
```

---

## 7. Complete Flow Explanation

### What Happens (Step by Step):

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: User Submits Prompt (MainContent.tsx)                │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Backend Schedules Job (job.py)                      │
│   - Generate job_id (UUID)                                   │
│   - Store in job_results[job_id]                             │
│   - Schedule Cloud Run job with JOB_ID env var              │
│   - Return job_id to frontend                                │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Navigate to Chatui (MainContent.tsx)                 │
│   - Store task data in sessionStorage                        │
│   - Navigate to /task page                                   │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Cloud Run Job Starts (main.py)                       │
│   - Create VM/container                                      │
│   - Read env vars (PROMPT, REPO, BRANCH, TOKEN, JOB_ID)     │
│   - Run main() function                                      │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Clone Repository (main.py lines 139-157)            │
│   - Create temp directory                                    │
│   - git clone --depth 1 -b branch repo.git                  │
│   - Repository now in temp_dir                               │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Run Agent (main.py lines 159-162)                   │
│   - Call run_agent_async()                                   │
│   - This function:                                           │
│     1. Creates session                                       │
│     2. Sets repo_path in state                               │
│     3. Creates Runner                                        │
│     4. Calls runner.run_async()                              │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Agent/Runner Event Loop (ADK Internally)            │
│   - Runner starts agent                                      │
│   - Agent yields events (internally, you don't see)         │
│   - Runner processes events                                  │
│   - You iterate with: async for event in events              │
│   - When final event comes → extract response                │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: Extract Results (main.py lines 70-87)               │
│   - Collect final_response from events                      │
│   - Call extract_code_from_response()                        │
│   - Return dict with status, response, code_changes         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: Send Results to Backend (main.py lines 165-188)      │
│   - Get JOB_ID from environment                              │
│   - POST /agent/results/{job_id} with results                │
│   - Backend stores in job_results[job_id]                    │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: Frontend Polls (Chatui.tsx)                        │
│   - Polls GET /agent/results/{job_id} every 2 seconds        │
│   - When status === "completed":                             │
│     * Show agent response in chat                            │
│     * Show code changes in DiffEditor                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Points:

1. **Cloud Run Job = Secure VM:**
   - ✅ Creates isolated container
   - ✅ Clones repo inside it
   - ✅ Runs agent in isolation
   - ✅ Gets cleaned up after

2. **Job ID:**
   - We generate it (UUID) for our tracking
   - Pass it to Cloud Run as env var
   - Use it to link results back

3. **Event Loop:**
   - Happens inside ADK (you don't write yields)
   - You just consume events with `async for`
   - Events come when agent has something to report

4. **Result Flow:**
   - Agent returns → caught in `result` variable (line 162)
   - Extracted → code changes parsed
   - Sent → POST to backend
   - Stored → job_results[job_id]
   - Retrieved → Frontend polls and gets it

---

## Code Changes Summary

### File: `backend/services/job.py`

**Before:**
```python
operation = client.run_job(request=request)
response = operation.result()
return response.name  # Cloud Run's execution name
```

**After:**
```python
# Generate our own job_id for tracking
job_id = str(uuid.uuid4())

# Store it for results lookup
job_results[job_id] = {...}

# Pass it to Cloud Run job
run_v2.EnvVar(name="JOB_ID", value=job_id)

# Return our job_id instead
return job_id
```

**Why:** Need our own ID to track results, not Cloud Run's internal ID.

---

### File: `job_runner/main.py`

**Before:**
```python
asyncio.run(run_agent_async(...))  # No return value captured
```

**After:**
```python
# Capture return value
result = asyncio.run(run_agent_async(...))

# Extract code changes
code_changes = extract_code_from_response(final_response)

# Send to backend
POST /agent/results/{job_id} with results
```

**Why:** Need to capture and send results back to frontend.

---

### File: `frontend/src/components/Chatui.tsx`

**Before:**
```typescript
// Static chat messages
<div className="bg-zinc-900">Hey!</div>
```

**After:**
```typescript
// Dynamic messages from state
{messages.map((message) => (
  <div className={message.role === "user" ? "..." : "..."}>
    {message.content}
  </div>
))}

// Poll for results
startPolling(job_id)  // Every 2 seconds

// Update when results arrive
setMessages([...prev, agentResponse])
setCodeChanges(result.code_changes)
```

**Why:** Need to show real agent results, not static content.

---

## Regex Learning Path

1. **Start Here:**
   - Python Regex Tutorial: https://docs.python.org/3/howto/regex.html

2. **Practice:**
   - regex101.com - Interactive playground
   - Write patterns, test them

3. **Common Patterns:**
   - `\w+` - word characters
   - `\d+` - digits
   - `.*?` - anything (non-greedy)
   - `([...])` - capture group
   - `(?:...)` - non-capturing group

4. **Mindset:**
   - Think: "What pattern am I looking for?"
   - Break it into parts
   - Test with real examples
   - Iterate and improve

---

## Complete Code Changes: Before vs After

### File: `backend/services/job.py`

**BEFORE:**
```python
from google.cloud import run_v2
from models.agent_model import AgentRunRequest
from core import config
from services.github_app_service import mint_installation_token

async def schedule_agent_job(payload:AgentRunRequest):
    installation_access_token = await mint_installation_token(str(payload.installation_id))
    client = run_v2.JobsClient()

    job_name = f"projects/{config.PROJECT}/locations/{config.REGION}/jobs/{config.JOB}"
    request = run_v2.RunJobRequest(
        name = job_name,
        overrides = run_v2.RunJobRequest.Overrides(
            container_overrides = [
                run_v2.RunJobRequest.Overrides.ContainerOverride(
                    env = [
                        run_v2.EnvVar(name="PROMPT", value=payload.prompt),
                        run_v2.EnvVar(name="REPO", value=payload.repo_name),
                        run_v2.EnvVar(name="BRANCH", value=payload.branches),
                        run_v2.EnvVar(name="TOKEN", value=installation_access_token),
                    ]
                )
            ]
        )
    )

    operation = client.run_job(request=request)
    response = operation.result()
    return response.name
```

**AFTER:**
```python
import os
import uuid
from datetime import datetime
from google.cloud import run_v2
from models.agent_model import AgentRunRequest
from core import config
from services.github_app_service import mint_installation_token

# In-memory storage for results
job_results = {}

async def schedule_agent_job(payload:AgentRunRequest):
    installation_access_token = await mint_installation_token(str(payload.installation_id))
    client = run_v2.JobsClient()

    job_name = f"projects/{config.PROJECT}/locations/{config.REGION}/jobs/{config.JOB}"
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job result storage
    job_results[job_id] = {
        "status": "queued",
        "final_response": None,
        "prompt": payload.prompt,
        "repo": payload.repo_name,
        "branch": payload.branches,
        "code_changes": {...},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None
    }

    request = run_v2.RunJobRequest(
        name = job_name,
        overrides = run_v2.RunJobRequest.Overrides(
            container_overrides = [
                run_v2.RunJobRequest.Overrides.ContainerOverride(
                    env = [
                        run_v2.EnvVar(name="PROMPT", value=payload.prompt),
                        run_v2.EnvVar(name="REPO", value=payload.repo_name),
                        run_v2.EnvVar(name="BRANCH", value=payload.branches),
                        run_v2.EnvVar(name="TOKEN", value=installation_access_token),
                        run_v2.EnvVar(name="JOB_ID", value=job_id),  # ← NEW
                        run_v2.EnvVar(name="BACKEND_URL", value=config.BACKEND_URL),  # ← NEW
                    ]
                )
            ]
        )
    )

    operation = client.run_job(request=request)
    response = operation.result()
    return job_id  # ← CHANGED: Return our job_id instead
```

**Key Changes:**
1. Generate `job_id` (UUID) for tracking
2. Store results in `job_results` dict
3. Pass `JOB_ID` and `BACKEND_URL` to Cloud Run job
4. Return `job_id` instead of Cloud Run's execution name

---

### File: `job_runner/main.py`

**BEFORE:**
```python
async def run_agent_async(prompt: str, repo: str, branch: str, token: str, temp_dir: str):
    # ... session setup ...
    
    # Process events
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text if event.content.parts else ""
            logging.info(f"Agent final response: {response_text[:200]}...")
    
    logging.info("✅ Agent workflow finished successfully.")

def main():
    # ... clone repo ...
    
    try:
        asyncio.run(run_agent_async(prompt, repo, branch, token, temp_dir))
        logging.info("✅ Agent workflow finished successfully.")
    except Exception as e:
        logging.exception("Agent run failed")
        sys.exit(1)
```

**AFTER:**
```python
async def run_agent_async(prompt: str, repo: str, branch: str, token: str, temp_dir: str):
    # ... session setup ...
    
    # Process events and collect results
    final_response = None
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text if event.content.parts else ""
            final_response = response_text  # ← CAPTURE response
            logging.info(f"Agent final response: {response_text[:200]}...")
    
    logging.info("✅ Agent workflow finished successfully.")
    
    # Extract code changes from final response  # ← NEW
    code_changes = extract_code_from_response(final_response or "")
    
    # Return results  # ← NEW
    return {
        "status": "completed",
        "final_response": final_response or "",
        "code_changes": code_changes
    }

def extract_code_from_response(response: str) -> dict:  # ← NEW FUNCTION
    """Extract code changes from agent response"""
    # Regex patterns to find code blocks
    # Returns: {original, modified, language, file_path}

def detect_language_from_code(code: str) -> str:  # ← NEW FUNCTION
    """Detect programming language from code content"""
    # Pattern matching for different languages
    # Returns: language name

def main():
    # ... clone repo ...
    
    try:
        # Run the async agent function and capture results  # ← CHANGED
        result = asyncio.run(run_agent_async(prompt, repo, branch, token, temp_dir))
        logging.info("✅ Agent workflow finished successfully.")
        
        # Send results to backend API  # ← NEW
        job_id = os.environ.get("JOB_ID")
        if job_id:
            backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
            # POST /agent/results/{job_id} with results
    except Exception as e:
        # ... error handling ...
        # Send error to backend  # ← NEW
```

**Key Changes:**
1. Capture `final_response` from events
2. Extract code changes using regex
3. Return results dict
4. Send results to backend via POST request
5. Added language detection function

---

### File: `backend/routes/agent_runner.py`

**BEFORE:**
```python
from fastapi import APIRouter
from services.job import schedule_agent_job
from models.agent_model import AgentRunRequest

router = APIRouter()

@router.post("/agent/run")
async def run_agent(payload: AgentRunRequest):
    job_id = await schedule_agent_job(payload)
    return {"job_id": job_id, "status": "queued"}
```

**AFTER:**
```python
from fastapi import APIRouter, HTTPException
from services.job import schedule_agent_job, job_results
from models.agent_model import AgentRunRequest
from datetime import datetime

router = APIRouter()

@router.post("/agent/run")
async def run_agent(payload: AgentRunRequest):
    job_id = await schedule_agent_job(payload)
    return {"job_id": job_id, "status": "queued"}

@router.post("/agent/results/{job_id}")  # ← NEW
async def store_results(job_id: str, result_data: dict):
    """Store results from job runner"""
    job_results[job_id].update({
        "status": result_data.get("status"),
        "final_response": result_data.get("final_response"),
        "code_changes": result_data.get("code_changes", {}),
        "updated_at": datetime.utcnow().isoformat()
    })
    return {"success": True, "job_id": job_id}

@router.get("/agent/results/{job_id}")  # ← NEW
async def get_results(job_id: str):
    """Get results for a job"""
    if job_id not in job_results:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_results[job_id]
```

**Key Changes:**
1. Added `POST /agent/results/{job_id}` - Store results from job runner
2. Added `GET /agent/results/{job_id}` - Get results for frontend polling

---

### File: `frontend/src/components/Chatui.tsx`

**BEFORE:**
```typescript
export function Chatui() {
  return (
    <div>
      <PanelGroup>
        <Panel>
          {/* Static chat messages */}
          <div className="bg-zinc-900">Hey!</div>
          <div className="bg-zinc-700">Hello world</div>
        </Panel>
        <Panel>
          {/* Static editor */}
          <DiffEditor
            original=""
            modified=""
          />
        </Panel>
      </PanelGroup>
    </div>
  );
}
```

**AFTER:**
```typescript
export function Chatui() {
  const location = useLocation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [codeChanges, setCodeChanges] = useState({...});
  
  useEffect(() => {
    // Load task data
    const taskData = location.state || JSON.parse(sessionStorage.getItem('currentTask'));
    
    // Add user message
    setMessages([{role: "user", content: taskData.prompt}]);
    
    // Start polling for results
    if (taskData.job_id) {
      startPolling(taskData.job_id);
    }
  }, [location]);
  
  const startPolling = (jobId: string) => {
    // Poll every 2 seconds
    setInterval(async () => {
      const result = await getAgentResults(jobId);
      if (result.status === "completed") {
        // Update messages and code changes
        setMessages(prev => [...prev, agentResponse]);
        setCodeChanges(result.code_changes);
      }
    }, 2000);
  };
  
  return (
    <div>
      {/* Dynamic messages */}
      {messages.map(msg => (
        <div className={msg.role === "user" ? "..." : "..."}>
          {msg.content}
        </div>
      ))}
      
      {/* Dynamic code changes */}
      {codeChanges.modified && (
        <DiffEditor
          original={codeChanges.original}
          modified={codeChanges.modified}
          language={codeChanges.language}
        />
      )}
    </div>
  );
}
```

**Key Changes:**
1. Load task data from route state/sessionStorage
2. Display user prompt immediately
3. Poll for results every 2 seconds
4. Update messages when results arrive
5. Display code changes in DiffEditor

---

## Next Steps

1. **For Render Deployment:**
   - Set `BACKEND_URL=https://your-backend.onrender.com` in environment variables
   - Or update `config.py` with default Render URL

2. **For Production:**
   - Replace `job_results` dict with database (Firestore/PostgreSQL)
   - Add error handling and retries
   - Add progress updates during agent execution

3. **Testing:**
   - Test with different code languages
   - Test with different response formats
   - Improve regex patterns based on real agent outputs

<!-- JOB.PY CODE HERE -->
import os
import uuid
from datetime import datetime
from google.cloud import run_v2
from models.agent_model import AgentRunRequest
from core import config
from services.github_app_service import mint_installation_token

# In-memory storage for results (use database in production)
job_results = {}

async def schedule_agent_job(payload:AgentRunRequest):
    # Resolve installation_id -> installation access token on the server
    installation_access_token = await mint_installation_token(str(payload.installation_id))
    client = run_v2.JobsClient()

    job_name = f"projects/{config.PROJECT}/locations/{config.REGION}/jobs/{config.JOB}"
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job result storage
    job_results[job_id] = {
        "status": "queued",
        "final_response": None,
        "prompt": payload.prompt,
        "repo": payload.repo_name,
        "branch": payload.branches,
        "code_changes": {
            "original": "",
            "modified": "",
            "language": "",
            "file_path": ""
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }

    request = run_v2.RunJobRequest(
        name = job_name,
        overrides = run_v2.RunJobRequest.Overrides(
            container_overrides = [
                run_v2.RunJobRequest.Overrides.ContainerOverride(
                    env = [
                        run_v2.EnvVar(name="PROMPT", value=payload.prompt),
                        run_v2.EnvVar(name="REPO", value=payload.repo_name),
                        run_v2.EnvVar(name="BRANCH", value=payload.branches),
                        run_v2.EnvVar(name="TOKEN", value=installation_access_token),
                        run_v2.EnvVar(name="JOB_ID", value=job_id),
                        run_v2.EnvVar(name="BACKEND_URL", value=config.BACKEND_URL),
                    ]
                )
            ]
        )
    )

    operation = client.run_job(request=request)
    response = operation.result()
    return job_id
<!-- END HERE -->

<!-- MAIN.PY CODE HERE  -->
import os
import subprocess
import tempfile
from backend.Raw_Gent.main_agent import root_agent
import logging
import google.cloud.logging
import sys
import asyncio
import shutil
import httpx
import re
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# init cloud loging client
client = google.cloud.logging.Client()

# route python logs to  cloud loging
client.setup_logging()

async def run_agent_async(prompt: str, repo: str, branch: str, token: str, temp_dir: str):
    """
    Run the agent with proper session state management.
    Sets repo_path in session state so all tools and sub-agents can access it.
    """
    APP_NAME = "raw_gent_agent"
    USER_ID = "job_runner"
    SESSION_ID = f"{repo}_{branch}_{os.getpid()}"
    
    # Create session service and runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Set repo_path in session state before running agent
    session.state['repo_path'] = temp_dir
    session.state['repo'] = repo
    session.state['branch'] = branch
    session.state['github_token'] = token
    
    # Save the session with updated state
    await session_service.update_session(session)
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Create user message content
    content = types.Content(
        role='user',
        parts=[types.Part(text=prompt)]
    )
    
    # Run the agent
    logging.info(f"Starting agent execution for session: {SESSION_ID}")
    events = runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )
    
    # Process events and collect results
    final_response = None
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text if event.content.parts else ""
            final_response = response_text
            logging.info(f"Agent final response: {response_text[:200]}...")  # Log first 200 chars
    
    logging.info("✅ Agent workflow finished successfully.")
    
    # Extract code changes from final response
    code_changes = extract_code_from_response(final_response or "")
    
    # Return results
    return {
        "status": "completed",
        "final_response": final_response or "",
        "code_changes": code_changes
    }

def extract_code_from_response(response: str) -> dict:
    """Extract code changes from agent response"""
    result = {
        "original": "",
        "modified": "",
        "language": "",  # Will be detected from code blocks or default
        "file_path": ""
    }
    
    # Try to find OLD CODE and NEW CODE markers
    old_code_match = re.search(r'(?:OLD CODE|old code|Before):[\s\S]*?```(?:\w+)?\n([\s\S]*?)```', response, re.IGNORECASE)
    new_code_match = re.search(r'(?:NEW CODE|new code|After|Fixed):[\s\S]*?```(?:\w+)?\n([\s\S]*?)```', response, re.IGNORECASE)
    
    if old_code_match and new_code_match:
        result["original"] = old_code_match.group(1).strip()
        result["modified"] = new_code_match.group(1).strip()
        # Try to detect language
        lang_match = re.search(r'```(\w+)', new_code_match.group(0))
        if lang_match:
            result["language"] = lang_match.group(1).lower()
    else:
        # Try to find multiple code blocks
        code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', response)
        if len(code_blocks) >= 2:
            result["original"] = code_blocks[0][1].strip()
            result["modified"] = code_blocks[1][1].strip()
            # Detect language from code block
            if code_blocks[1][0]:
                result["language"] = code_blocks[1][0].lower()
            elif code_blocks[0][0]:
                result["language"] = code_blocks[0][0].lower()
            # If no language detected, try to infer from file extension or code patterns
            if not result["language"]:
                result["language"] = detect_language_from_code(result["modified"])
        elif len(code_blocks) == 1:
            result["modified"] = code_blocks[0][1].strip()
            result["language"] = code_blocks[0][0].lower() if code_blocks[0][0] else detect_language_from_code(result["modified"])
    
    # Try to extract file path
    file_match = re.search(r'(?:File|file):\s*([^\n]+)', response)
    if file_match:
        result["file_path"] = file_match.group(1).strip()
    
    # If still no language, try to detect from code content
    if not result["language"] and result["modified"]:
        result["language"] = detect_language_from_code(result["modified"])
    
    return result

def detect_language_from_code(code: str) -> str:
    """Try to detect programming language from code content"""
    if not code:
        return "python"  # Default fallback
    
    # Common language patterns
    patterns = {
        "javascript": [r"function\s+\w+\s*\(", r"const\s+\w+\s*=", r"import\s+.*from"],
        "typescript": [r"function\s+\w+\s*:\s*\w+", r"interface\s+\w+", r"type\s+\w+"],
        "python": [r"def\s+\w+\s*\(", r"import\s+\w+", r"class\s+\w+"],
        "java": [r"public\s+class\s+\w+", r"@Override", r"package\s+\w+"],
        "go": [r"func\s+\w+\s*\(", r"package\s+\w+", r":=\s+"],
        "rust": [r"fn\s+\w+\s*\(", r"let\s+mut\s+", r"use\s+\w+::"],
        "cpp": [r"#include\s*<", r"namespace\s+\w+", r"std::"],
        "c": [r"#include\s*<", r"int\s+main\s*\("],
        "ruby": [r"def\s+\w+", r"class\s+\w+", r"require\s+"],
    }
    
    for lang, lang_patterns in patterns.items():
        for pattern in lang_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return lang
    
    # Default fallback
    return "python"

def main():
    prompt = os.environ["PROMPT"]
    repo = os.environ["REPO"]
    branch = os.environ["BRANCH"]
    token = os.environ["TOKEN"]

    temp_dir = None
    temp_dir = tempfile.mkdtemp()
    clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"

    logging.info(f"Starting agent job for repo: {repo}, branch: {branch}")

    try:
        subprocess.run([
           "git", "clone", "--depth", "1", "-b", branch,
            clone_url, temp_dir
        ], check=True,capture_output=True,text=True,timeout=300)
        logging.info("Repository clone successfully") 
    except FileNotFoundError:
        logging.critical("❌ Git not found in container. Install it in Dockerfile.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logging.error(f"Git clone failed with code {e.returncode}\n"
            f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        sys.exit(1)
    except subprocess.TimeoutExpired as e:
        logging.info(f"❌ Git clone timed out after {e.timeout} seconds.")
        sys.exit(1)
    except Exception as e:
        logging.info("Unexpected error occured")
        sys.exit(1)

    try:
        logging.info("Running root agent workflow...")
        # Run the async agent function and capture results
        result = asyncio.run(run_agent_async(prompt, repo, branch, token, temp_dir))
        logging.info("✅ Agent workflow finished successfully.")
        
        # Send results to backend API (if JOB_ID is provided)
        job_id = os.environ.get("JOB_ID")
        if job_id:
            try:
                backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
                async def send_results():
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{backend_url}/agent/results/{job_id}",
                            json={
                                "status": result.get("status"),
                                "final_response": result.get("final_response"),
                                "code_changes": result.get("code_changes", {})
                            },
                            timeout=30.0
                        )
                        if response.status_code == 200:
                            logging.info(f"✅ Results sent to backend for job {job_id}")
                        else:
                            logging.warning(f"⚠️ Failed to send results: {response.status_code}")
                
                asyncio.run(send_results())
            except Exception as e:
                logging.error(f"Failed to send results to backend: {e}")
        
    except Exception as e:
        logging.exception("Agent run failed")
        
        # Send error to backend if JOB_ID provided
        job_id = os.environ.get("JOB_ID")
        if job_id:
            try:
                backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
                async def send_error():
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            f"{backend_url}/agent/results/{job_id}",
                            json={
                                "status": "failed",
                                "final_response": f"Error: {str(e)}",
                                "code_changes": {}
                            },
                            timeout=30.0
                        )
                asyncio.run(send_error())
            except:
                pass
        
        sys.exit(1)
    finally:
        # Cleanup temp dir after agent completes
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.info("🧹 Cleaned up temporary directory.")
<!-- END HERE -->

<!-- AGENT RUNNER CODE HERE  -->
from fastapi import APIRouter, HTTPException
from services.job import schedule_agent_job, job_results
from models.agent_model import AgentRunRequest
from datetime import datetime

router = APIRouter()

@router.post("/agent/run")
async def run_agent(payload: AgentRunRequest):
    job_id = await schedule_agent_job(payload)
    return {"job_id": job_id, "status": "queued"}

@router.post("/agent/results/{job_id}")
async def store_results(job_id: str, result_data: dict):
    """Store results from job runner"""
    if job_id not in job_results:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_results[job_id].update({
        "status": result_data.get("status", "completed"),
        "final_response": result_data.get("final_response"),
        "code_changes": result_data.get("code_changes", {}),
        "updated_at": datetime.utcnow().isoformat()
    })
    
    return {"success": True, "job_id": job_id}

@router.get("/agent/results/{job_id}")
async def get_results(job_id: str):
    """Get results for a job"""
    if job_id not in job_results:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_results[job_id]

<!-- END HERE  -->

<!-- MAIN CONTENT CODE HERE  -->

import {
  ChevronDown,
  GitBranch,
  ArrowRight,
  Play,
  Lightbulb,
  Plus,
  Check,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { useEffect, useState } from "react";
import { installGithubApp } from "../services/github";
import { fetchbranch, fetchInstallRepos } from "../services/github_api";
import { runagent } from "../services/run_agent";
import { useNavigate } from "react-router-dom";

export function MainContent() {
  const navigate = useNavigate();
  const [selectedbranch, setSelectedbranch] = useState("(empty repo)");
  const [selectedRepo, setSelectedRepo] = useState<RepoType | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [pending, setPending] = useState(false);
  const [repos, setRepos] = useState([]);
  const [branches, setBranches] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);

  const handleRunAgent = async() => {
    if (!inputValue.trim()) {
      alert("Please enter a prompt");
      return;
    }
    if (!selectedRepo) {
      alert("Please select a valid repo");
      return;
    }

    setPending(true);

    try {
      const result = await runagent(
        inputValue,
        selectedRepo.full_name,
        selectedRepo.id,
        selectedbranch
      );
      
      // Store task data in sessionStorage for Chatui to access
      const taskData = {
        job_id: result.job_id || null,
        prompt: inputValue,
        repo: selectedRepo.full_name,
        branch: selectedbranch,
        status: "queued",
        createdAt: new Date().toISOString()
      };
      
      sessionStorage.setItem('currentTask', JSON.stringify(taskData));
      
      // Navigate to task page
      navigate('/task', { state: taskData });
      
    } catch (error) {
      console.error("Agent failed:", error);
      alert("Failed to run agent. Please try again.");
      setPending(false);
    }
  }

  const handleinstallGithubApp = () => {
    installGithubApp();
  };

  const handleRepoSelect = async(repo) => {
    setSelectedRepo(repo);
    setShowDropdown(false);
    try {
      const branchresponse = await fetchbranch(repo.name);
      const branchesdata = branchresponse.Branches || [];
      setBranches(branchesdata);

      if (branchesdata.length > 0) {
        setSelectedbranch(branchesdata[0].name);
      } else {
        setSelectedbranch("(empty repo)");
      }
    } catch (error) {
      console.error("Failed to fetch branches", error);
      setBranches([]);
      setSelectedbranch("(empty repo)");
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const hasInstall = params.get("installation_id");

    if (hasInstall) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    const loadrepos = async () => {
      setPending(true);
      try {
        const data = await fetchInstallRepos();
        console.log("📦 Repo Data:", data);
        const repositories = data.repositories || [];
        setRepos(repositories);
        setHasInitialized(true);

        // Auto-select the first repository
        if (repositories.length > 0) {
          const firstrepo = repositories[0];
          setSelectedRepo(firstrepo);

          const branchresponse = await fetchbranch(firstrepo.name);
          const branchesdata = branchresponse.Branches || [];
          setBranches(branchesdata);

          if (branchesdata.length > 0) {
            setSelectedbranch(branchesdata[0].name);
          }
        }
      } catch (error) {
        console.error("Failed to fetch repos", error);
        setRepos([]);
        setHasInitialized(true);
      } finally {
        setPending(false);
      }
    };
    loadrepos();
  }, []);

  return (
    <div className="flex-1 flex flex-col  bg-[#1a1a1a]">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">
            Raw-Gent: an async development agent.
          </h1>
          <p className="text-gray-400 text-lg">
            Raw-Gent tackles bugs, small feature requests and other software
            engineering tasks, with direct export to GitHub.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                {/* Repository Section */}
                <div className="flex items-center gap-2 flex-1 mr-4">
                  <GitBranch className="w-5 h-5 text-gray-500" />

                  {/* Repository Selection Logic */}
                  {!hasInitialized ? (
                    // Initial state - Add Repository button
                    <Button
                      variant="ghost"
                      className="text-gray-400 justify-between w-48"
                      onClick={handleinstallGithubApp}
                      disabled={pending}
                    >
                      {pending ? (
                        <>
                          <span className="flex items-center gap-2">
                            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                            Loading...
                          </span>
                        </>
                      ) : (
                        <>
                          Add Repository
                          <Plus className="w-4 h-4" />
                        </>
                      )}
                    </Button>
                  ) : selectedRepo ? (
                    // Selected repository with dropdown
                    <div className="relative">
                      <Button
                        variant="ghost"
                        className="text-gray-300 justify-between w-64 hover:bg-gray-800"
                        onClick={() => setShowDropdown(!showDropdown)}
                      >
                        <div className="flex items-center gap-2">
                          <Check className="w-4 h-4 text-green-500" />
                          <span className="truncate">
                            {selectedRepo.full_name}
                          </span>
                        </div>
                        <ChevronDown
                          className={`w-4 h-4 transition-transform ${
                            showDropdown ? "rotate-180" : ""
                          }`}
                        />
                      </Button>

                      {/* Repository Dropdown */}
                      {showDropdown && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
                          {repos.length > 0 ? (
                            <div className="py-2">
                              {/* Other repositories */}
                              {repos
                                .filter((repo) => repo.id !== selectedRepo.id)
                                .map((repo) => (
                                  <button
                                    key={repo.id}
                                    onClick={() => handleRepoSelect(repo)}
                                    className="w-full text-left px-4 py-3 text-gray-300 hover:bg-gray-700 transition-colors"
                                  >
                                    <div className="font-medium">
                                      {repo.full_name}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                      {repo.name}
                                    </div>
                                  </button>
                                ))}

                              {/* Add more repositories button */}
                              <div className="border-t border-gray-700 mt-2 pt-2">
                                <button
                                  onClick={handleinstallGithubApp}
                                  className="w-full text-left px-4 py-3 text-blue-400 hover:bg-gray-700 transition-colors flex items-center gap-2"
                                >
                                  <Plus className="w-4 h-4" />
                                  Add more repositories
                                </button>
                              </div>
                            </div>
                          ) : (
                            <div className="p-4 text-gray-500 text-center">
                              No other repositories found
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ) : (
                    // No repos available
                    <Button
                      variant="ghost"
                      className="text-gray-400 justify-between w-48"
                      onClick={handleinstallGithubApp}
                    >
                      No repositories found
                      <Plus className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* Branch Section */}
                <div className="flex items-center gap-2">
                  <GitBranch className="w-5 h-5 text-gray-500" />

                  {branches.length > 0 ? (
                    <select
                      value={selectedbranch}
                      onChange={(e) => setSelectedbranch(e.target.value)}
                      className="bg-gray-800 text-white px-4 py-2 rounded w-48"
                    >
                      {branches.map((branch) => (
                        <option key={branch.name} value={branch.name}>
                          {branch.name}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <Button
                      variant="ghost"
                      className="text-gray-400 justify-between w-48"
                      disabled
                    >
                      {selectedbranch}
                      <ChevronDown className="w-4 h-4" />
                    </Button>
                  )}
                </div>
              </div>

              <div className="relative">
                <Textarea
                  placeholder="Help me fix this error ..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  className="min-h-[120px] bg-transparent border-none text-gray-300 placeholder-gray-600 resize-none text-lg p-0"
                />
                <Button
                  className="absolute bottom-4 right-4 bg-gray-700 hover:bg-gray-600 text-gray-300"
                  size="sm"
                  onClick={handleRunAgent}
                >
                  Give me a plan
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-center">
            <Button
              variant="ghost"
              className="flex items-center gap-2 text-purple-400 hover:text-purple-300 border border-purple-500/20 hover:border-purple-500/40"
            >
              <Play className="w-4 h-4" />
              How it works
            </Button>
            <Button
              variant="ghost"
              className="flex items-center gap-2 text-purple-400 hover:text-purple-300 border border-purple-500/20 hover:border-purple-500/40"
            >
              <Lightbulb className="w-4 h-4" />
              Need inspiration?
            </Button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-gray-800">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-gray-400">
              Terms
            </a>
            <a href="#" className="hover:text-gray-400">
              Open source licenses
            </a>
            <a href="#" className="hover:text-gray-400">
              Use code with caution
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
<!-- END HERE  -->

<!-- CHAT UI  -->
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { Button } from "./ui/button";
import { ArrowRight } from "lucide-react";
import { DiffEditor } from "@monaco-editor/react";
import { useEffect, useState, useRef, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { getAgentResults } from "../services/get_agent_results";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function Chatui() {
  const location = useLocation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [codeChanges, setCodeChanges] = useState({ original: "", modified: "", language: "python" });
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const startPolling = useCallback((jobId: string) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const result = await getAgentResults(jobId);
        
        if (result.status === "completed") {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          setIsLoading(false);
          
          // Add agent response to messages
          setMessages(prev => [...prev, {
            role: "assistant",
            content: result.final_response || "Task completed successfully!",
            timestamp: new Date()
          }]);
          
          // Update code changes if available
          if (result.code_changes && result.code_changes.modified) {
            setCodeChanges({
              original: result.code_changes.original || "",
              modified: result.code_changes.modified || "",
              language: result.code_changes.language || "python"
            });
          }
          
        } else if (result.status === "failed") {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          setIsLoading(false);
          setMessages(prev => [...prev, {
            role: "assistant",
            content: `Error: ${result.final_response || "Unknown error occurred"}`,
            timestamp: new Date()
          }]);
        }
      } catch (error) {
        console.error("Failed to fetch results:", error);
      }
    }, 2000); // Poll every 2 seconds
    
    // Stop polling after 10 minutes
    setTimeout(() => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
        setIsLoading(false);
      }
    }, 600000);
  }, []);

  // Load task data from route state or sessionStorage
  useEffect(() => {
    const taskData = location.state || JSON.parse(sessionStorage.getItem('currentTask') || '{}');
    
    if (taskData.prompt) {
      // Add user message
      setMessages([{
        role: "user",
        content: taskData.prompt,
        timestamp: new Date()
      }]);
      
      // Start polling if job_id exists
      if (taskData.job_id) {
        setIsLoading(true);
        startPolling(taskData.job_id);
      }
    }
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [location, startPolling]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className="bg-[#28252b] p-0 absolute top-[48px] left-64 right-0 bottom-0 flex flex-col
         text-white font-normal text-[13px] overflow-hidden"
    >
      <PanelGroup direction="horizontal" className="flex-1">
        <Panel
          defaultSize={30}
          minSize={20}
          className="border-r border-gray-700 flex flex-col"
        >
          {/* Panel Header*/}
          <div className="h-10 px-4 border-b border-gray-700 flex items-center justify-between bg-[#28252b] flex-shrink-0">
            <span className="text-white font-sans font-medium">Chat Panel</span>
          </div>

          {/* Chat Messages Area */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden">
            <div className="p-4 space-y-4 min-h-full">
              {messages.length === 0 ? (
                <div className="text-gray-500 text-center mt-8">
                  No messages yet. Start a task from the home page.
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg max-w-[80%] ${
                      message.role === "user"
                        ? "bg-zinc-700 ml-auto"
                        : "bg-zinc-900"
                    }`}
                  >
                    <div className="text-sm text-gray-300 whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="bg-zinc-900 p-3 rounded-lg w-fit">
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    Agent is working...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area - Sticky Bottom */}
          <div className="p-4 border-gray-700 bg-[#28252b] flex-shrink-0">
            <div className="bg-zinc-700 rounded-3xl flex px-3 items-center">
              <input
                type="text"
                placeholder="Type your message..."
                className="w-full p-3 bg-transparent rounded-3xl focus:outline-none font-semibold font-sans placeholder-gray-400"
              />
              <Button className="hover:bg-zinc-600" size="sm" variant="ghost">
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Panel>

        <PanelResizeHandle />

        <Panel
          defaultSize={30}
          minSize={20}
          className="border-l border-gray-700 flex flex-col"
        >
          {/* Right Panel Header */}
          <div className="h-10 px-4 border-b border-gray-700 flex items-center justify-between bg-[#28252b] flex-shrink-0">
            <span className="text-white font-sans font-medium">
              Main Content
            </span>
          </div>

          {/* Right Panel Content */}
          <div className="flex-1">
            {codeChanges.modified ? (
              <DiffEditor
                height="100%"
                theme="vs-dark"
                original={codeChanges.original}
                modified={codeChanges.modified}
                language={codeChanges.language}
                options={{
                  readOnly: true,
                  minimap: { enabled: true },
                  fontSize: 14,
                  lineNumbers: "on",
                  renderSideBySide: true,
                  enableSplitViewResizing: true,
                }}
              />
            ) : (
              <div className="text-gray-400 text-center mt-8 p-4">
                <p>Code changes will appear here once the agent completes.</p>
                {isLoading && (
                  <p className="text-sm mt-2">Waiting for agent response...</p>
                )}
              </div>
            )}
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}
<!-- END HERE -->