# Design Document: Setu - Voice-First Autonomous Web Agent

## Overview

Setu is a three-tier voice-first autonomous web agent that bridges the digital divide for India's underserved populations. The system combines speech recognition, large language models, and browser automation to enable voice-based access to government services without requiring users to read, type, or navigate complex interfaces.

### Design Philosophy

1. **Voice-First, Not Voice-Enabled**: Every interaction is designed for voice from the ground up
2. **Agent, Not Chatbot**: System physically executes tasks rather than providing instructions
3. **Security by Isolation**: Remote Browser Isolation (Kavach Protocol) protects users from web threats
4. **Graceful Degradation**: System functions on low-end devices and slow networks
5. **Explainable Actions**: AI explains every step in simple language before execution

### Key Innovations

- **Dialect-Native Processing**: Handles code-mixed speech (Hinglish, Tanglish) and regional dialects
- **Visual Security Layer**: Moondream vision model detects phishing and dark patterns
- **Stateful Replanning**: Planning engine adapts to website changes and execution failures
- **Cost-Optimized Architecture**: EC2 Spot instances and intelligent model selection keep costs under ₹1/task
- **Zero-Storage Client**: 10MB PWA replaces 50+ government service apps

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (User Device)                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Progressive Web App (Next.js 14 + Tailwind)                      │  │
│  │  - Voice Input UI (MediaRecorder API)                             │  │
│  │  - Audio Playback (Web Audio API)                                 │  │
│  │  - Visual Feedback (Large UI, High Contrast)                      │  │
│  │  - Offline Audio Caching (Service Worker)                         │  │
│  │  Size: <10MB │ Android 9+ │ 2G/3G Compatible                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ HTTPS/WSS (TLS 1.3)
                               │ CloudFront CDN
┌──────────────────────────────▼──────────────────────────────────────────┐
│                      INTELLIGENCE LAYER (AWS)                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  API Gateway + Lambda Functions (Node.js 18)                    │   │
│  │  - Session Management                                            │   │
│  │  - Request Routing                                               │   │
│  │  - Authentication & Rate Limiting                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Transcribe │  │   Bedrock    │  │    Polly     │                  │
│  │   (Whisper)  │  │  (LLMs)      │  │   (Neural)   │                  │
│  │              │  │              │  │              │                  │
│  │ - Hindi      │  │ - Llama-3 8B │  │ - Regional   │                  │
│  │ - Gujarati   │  │ - Llama-3 70B│  │   Voices     │                  │
│  │ - Tamil      │  │ - Claude 3   │  │ - Streaming  │                  │
│  │ - 10+ langs  │  │   Sonnet     │  │              │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  DynamoDB Tables                                                 │   │
│  │  - SessionState (TTL: 30min)                                     │   │
│  │  - ServiceTemplates (Versioned)                                  │   │
│  │  - UserPreferences (Language, Voice Speed)                       │   │
│  │  - AuditLogs (90-day retention)                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ Internal VPC
                               │ Private Subnet
┌──────────────────────────────▼──────────────────────────────────────────┐
│                      EXECUTION LAYER (AWS)                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  EC2 Auto Scaling Group (Spot Instances)                        │   │
│  │  - Instance Type: t3.medium (2 vCPU, 4GB RAM)                   │   │
│  │  - OS: Ubuntu 22.04 LTS                                          │   │
│  │  - Runtime: Python 3.11 + Playwright                             │   │
│  │  - Browser: Chromium (headless)                                  │   │
│  │  - Scaling: 2-50 instances based on queue depth                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Kavach Security Layer                                           │   │
│  │  - AWS WAF (OWASP Top 10 Rules)                                  │   │
│  │  - Moondream Vision Model (Phishing Detection)                   │   │
│  │  - Session Isolation (Ephemeral Containers)                      │   │
│  │  - Credential Encryption (AWS KMS)                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SQS Queue (Task Queue)                                          │   │
│  │  - Visibility Timeout: 5 minutes                                 │   │
│  │  - Dead Letter Queue for failed tasks                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                      MONITORING & OBSERVABILITY                           │
│  CloudWatch Logs │ X-Ray Tracing │ CloudWatch Metrics │ SNS Alerts       │
└───────────────────────────────────────────────────────────────────────────┘
```


## Component Design

### 3.1 Client PWA (Progressive Web App)

**Technology Stack:**
- Framework: Next.js 14 (App Router)
- Styling: Tailwind CSS + Shadcn/UI components
- State Management: React Context + Zustand (lightweight)
- Audio: MediaRecorder API + Web Audio API
- Offline: Service Worker with Workbox
- Build Target: <10MB total bundle size

**Key Screens:**

1. **Voice Input Screen** (Primary Interface)
   - Large circular "Press to Speak" button (80% of screen)
   - Visual waveform feedback during recording
   - Language selector (persistent, top-right)
   - Status indicator: "Listening" → "Processing" → "Executing"

2. **Task Progress Screen**
   - Live text transcript of AI actions
   - Progress bar with step indicators
   - "Pause" and "Cancel" voice commands always active
   - Screenshot preview of current browser state (optional, bandwidth-aware)

3. **Confirmation Screen**
   - Large text display of critical information (amounts, dates)
   - "Confirm" and "Cancel" buttons (voice + touch)
   - Audio playback of confirmation details

**Voice-First Interaction Model:**

```
User Flow:
1. User presses large button → starts recording
2. User speaks command → waveform provides visual feedback
3. User releases button → audio uploads to backend
4. System responds with voice confirmation → plays through speaker
5. User confirms or corrects → cycle repeats until task complete
```

**Offline Capabilities:**
- Service Worker caches app shell and critical assets
- Audio recordings stored in IndexedDB if network unavailable
- Automatic sync when connection restored
- Graceful error messages via cached audio files

**Accessibility Features:**
- Minimum touch target size: 48x48dp (WCAG AAA)
- High contrast mode (4.5:1 ratio minimum)
- Large font sizes (minimum 18sp for body text)
- Screen reader support for visually impaired users
- Haptic feedback for button presses

### 3.2 Audio Pipeline

**Architecture:**

```
MediaRecorder → Blob → S3 Upload → Transcribe → Intent Gatekeeper → Response
     ↓                                                                    ↓
  Compression                                                        Polly TTS
  (Opus codec)                                                            ↓
                                                                   CloudFront
                                                                        ↓
                                                                   Audio Player
```

**AWS Transcribe Configuration:**
- Model: Whisper Large-v3 (via Transcribe)
- Streaming: Yes (for real-time feedback)
- Language Detection: Automatic with language hints
- Custom Vocabulary: Government service terms, Indian names, place names
- Profanity Filtering: Disabled (may interfere with legitimate words)

**Supported Languages:**
1. Hindi (hi-IN)
2. Gujarati (gu-IN)
3. Tamil (ta-IN)
4. Telugu (te-IN)
5. Bengali (bn-IN)
6. Marathi (mr-IN)
7. Kannada (kn-IN)
8. Malayalam (ml-IN)
9. Punjabi (pa-IN)
10. Odia (or-IN)
11. English (en-IN) - Indian accent

**Intent Gatekeeper (Llama-3 8B):**

Purpose: Fast, cost-effective intent extraction and validation

Input: Transcribed text + conversation history
Output: Structured intent JSON

Example Intent JSON:
```json
{
  "intent_type": "book_train_ticket",
  "confidence": 0.92,
  "service": "irctc",
  "parameters": {
    "from_station": "Patna Junction",
    "to_station": "New Delhi",
    "travel_date": "2024-12-16",
    "passenger_count": 1,
    "class": "sleeper"
  },
  "missing_parameters": [],
  "clarification_needed": false,
  "user_language": "hi-IN",
  "original_text": "मुझे पटना से दिल्ली की ट्रेन टिकट बुक करनी है अगले सोमवार को"
}
```

**Intent Validation Rules:**
- Confidence threshold: 0.80 (below this, ask clarifying questions)
- Malicious intent detection: Reject intents involving "transfer all money", "delete account", etc.
- Parameter validation: Check date formats, numeric ranges, required fields
- Service availability: Verify requested service is supported

**Audio Compression:**
- Codec: Opus (best compression for speech)
- Bitrate: 16 kbps (sufficient for voice)
- Sample Rate: 16 kHz (Transcribe requirement)
- Channels: Mono
- Expected size: ~120 KB per minute of audio


### 3.3 Planning Engine

**Model Selection Strategy:**

| Task Complexity | Model | Use Case | Cost per 1K tokens |
|----------------|-------|----------|-------------------|
| Simple | Llama-3 8B | Intent extraction, simple confirmations | ₹0.001 |
| Medium | Llama-3 70B | Multi-step planning, form filling | ₹0.008 |
| Complex | Claude 3 Sonnet | Complex reasoning, error recovery | ₹0.30 |

**Planning Engine Architecture:**

```python
# Pseudocode for Planning Engine

class PlanningEngine:
    def __init__(self, bedrock_client, service_templates):
        self.bedrock = bedrock_client
        self.templates = service_templates
        self.model_selector = ModelSelector()
    
    def generate_plan(self, intent, context):
        # Select appropriate model based on task complexity
        model = self.model_selector.select(intent.complexity)
        
        # Retrieve service template
        template = self.templates.get(intent.service)
        
        # Build prompt with template and intent
        prompt = self.build_prompt(intent, template, context)
        
        # Generate action plan
        response = self.bedrock.invoke_model(
            model_id=model,
            body=prompt
        )
        
        # Parse and validate plan
        plan = self.parse_plan(response)
        return plan
    
    def replan(self, original_plan, execution_state, error):
        # Stateful replanning based on execution failure
        context = {
            "completed_steps": execution_state.completed,
            "failed_step": execution_state.current,
            "error_message": error.message,
            "page_state": execution_state.page_snapshot
        }
        
        # Use more powerful model for error recovery
        model = "anthropic.claude-3-sonnet"
        
        prompt = self.build_replan_prompt(original_plan, context)
        response = self.bedrock.invoke_model(model_id=model, body=prompt)
        
        new_plan = self.parse_plan(response)
        return new_plan
```

**Action Plan JSON Structure:**

```json
{
  "plan_id": "plan_abc123",
  "service": "irctc",
  "task": "book_train_ticket",
  "estimated_duration": 120,
  "steps": [
    {
      "step_id": 1,
      "action": "navigate",
      "target": "https://www.irctc.co.in",
      "description": "Opening IRCTC website",
      "user_message": "मैं IRCTC वेबसाइट खोल रहा हूं",
      "wait_for": "page_load"
    },
    {
      "step_id": 2,
      "action": "click",
      "selector": "#loginButton",
      "description": "Clicking login button",
      "user_message": "लॉगिन बटन पर क्लिक कर रहा हूं",
      "wait_for": "element_visible"
    },
    {
      "step_id": 3,
      "action": "input",
      "selector": "#username",
      "value": "{{user.irctc_username}}",
      "description": "Entering username",
      "user_message": "आपका यूज़रनेम डाल रहा हूं",
      "sensitive": false
    },
    {
      "step_id": 4,
      "action": "input",
      "selector": "#password",
      "value": "{{user.irctc_password}}",
      "description": "Entering password",
      "user_message": "पासवर्ड डाल रहा हूं",
      "sensitive": true
    },
    {
      "step_id": 5,
      "action": "wait_for_user",
      "reason": "captcha",
      "description": "CAPTCHA verification needed",
      "user_message": "कृपया CAPTCHA कोड बोलें",
      "timeout": 60
    },
    {
      "step_id": 6,
      "action": "search_trains",
      "from": "{{intent.from_station}}",
      "to": "{{intent.to_station}}",
      "date": "{{intent.travel_date}}",
      "description": "Searching for trains",
      "user_message": "ट्रेन खोज रहा हूं"
    },
    {
      "step_id": 7,
      "action": "confirm_with_user",
      "data": "{{available_trains}}",
      "description": "Present train options",
      "user_message": "ये ट्रेनें उपलब्ध हैं। कौन सी बुक करूं?",
      "wait_for": "user_choice"
    }
  ],
  "rollback_strategy": "logout_and_retry",
  "max_retries": 3
}
```

**Stateful Context Management:**

The planning engine maintains context across replanning iterations:

```python
class ExecutionContext:
    def __init__(self):
        self.completed_steps = []
        self.current_step = None
        self.page_state = {}
        self.user_inputs = {}
        self.errors = []
    
    def snapshot(self):
        return {
            "completed": [s.to_dict() for s in self.completed_steps],
            "current": self.current_step.to_dict() if self.current_step else None,
            "page_url": self.page_state.get("url"),
            "page_title": self.page_state.get("title"),
            "visible_elements": self.page_state.get("elements", [])
        }
```


### 3.4 Playwright Execution Engine

**Runtime Environment:**
- OS: Ubuntu 22.04 LTS
- Python: 3.11
- Playwright: 1.40+
- Browser: Chromium 120+ (headless)
- Instance Type: EC2 t3.medium (2 vCPU, 4GB RAM)
- Spot Instance: Yes (70% cost savings)

**EC2 Configuration:**

```yaml
AutoScalingGroup:
  MinSize: 2
  MaxSize: 50
  DesiredCapacity: 5
  InstanceType: t3.medium
  SpotPrice: $0.0416/hour (vs $0.0416 on-demand)
  LaunchTemplate:
    ImageId: ami-ubuntu-22.04
    UserData: |
      #!/bin/bash
      apt-get update
      apt-get install -y python3.11 python3-pip
      pip3 install playwright boto3 redis
      playwright install chromium
      python3 /opt/setu/execution_worker.py
  
  ScalingPolicies:
    - Type: TargetTrackingScaling
      TargetValue: 70  # CPU utilization
    - Type: TargetTrackingScaling
      TargetValue: 100  # SQS queue depth
```

**Execution Loop Pseudocode:**

```python
# Pseudocode for Playwright Execution Engine

class PlaywrightExecutor:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.security_checker = MoondreamSecurityChecker()
    
    async def execute_plan(self, plan, session_id):
        try:
            # Launch isolated browser context
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                locale='en-IN'
            )
            
            self.page = await self.context.new_page()
            
            # Execute each step in the plan
            for step in plan.steps:
                await self.execute_step(step, session_id)
                
                # Security check after each navigation
                if step.action == 'navigate':
                    await self.security_check(session_id)
                
                # Update session state
                await self.update_session_state(session_id, step)
            
            return {"status": "success", "result": await self.get_result()}
        
        except Exception as e:
            # Log error and trigger replanning
            await self.log_error(session_id, e)
            return {"status": "error", "error": str(e)}
        
        finally:
            # Always cleanup browser resources
            await self.cleanup()
    
    async def execute_step(self, step, session_id):
        action = step.action
        
        if action == "navigate":
            await self.page.goto(step.target, wait_until='networkidle')
            await self.notify_user(step.user_message, session_id)
        
        elif action == "click":
            element = await self.page.wait_for_selector(step.selector, timeout=10000)
            await element.click()
            await self.notify_user(step.user_message, session_id)
        
        elif action == "input":
            element = await self.page.wait_for_selector(step.selector, timeout=10000)
            await element.fill(step.value)
            if not step.sensitive:
                await self.notify_user(step.user_message, session_id)
        
        elif action == "select":
            await self.page.select_option(step.selector, step.value)
            await self.notify_user(step.user_message, session_id)
        
        elif action == "wait_for_user":
            # Pause execution and wait for user input (CAPTCHA, OTP, etc.)
            user_input = await self.request_user_input(
                step.user_message, 
                session_id, 
                timeout=step.timeout
            )
            return user_input
        
        elif action == "confirm_with_user":
            # Present data to user and wait for confirmation
            confirmation = await self.request_confirmation(
                step.data,
                step.user_message,
                session_id
            )
            if not confirmation:
                raise UserCancelledException("User cancelled the task")
        
        elif action == "screenshot":
            screenshot = await self.page.screenshot()
            await self.upload_screenshot(screenshot, session_id)
        
        # Wait for any specified condition
        if step.wait_for == "page_load":
            await self.page.wait_for_load_state('networkidle')
        elif step.wait_for == "element_visible":
            await self.page.wait_for_selector(step.selector, state='visible')
    
    async def security_check(self, session_id):
        # Capture page screenshot
        screenshot = await self.page.screenshot()
        
        # Run Moondream visual analysis
        threats = await self.security_checker.analyze(screenshot)
        
        if threats.phishing_detected:
            await self.notify_user("सावधान! यह वेबसाइट असुरक्षित लग रही है", session_id)
            raise SecurityException("Phishing attempt detected")
        
        if threats.dark_patterns:
            await self.notify_user(
                f"चेतावनी: {threats.dark_pattern_description}", 
                session_id
            )
    
    async def cleanup(self):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
```

**CAPTCHA Handling Strategy:**

1. **Detection**: Identify CAPTCHA presence using common selectors
2. **User Notification**: Pause execution and request user assistance via voice
3. **Audio Streaming**: Stream CAPTCHA image to user's device (if visual CAPTCHA)
4. **Voice Input**: User speaks CAPTCHA text
5. **Transcription**: Convert speech to text
6. **Submission**: Fill CAPTCHA field and continue execution
7. **Retry Logic**: If CAPTCHA fails, request user to try again (max 3 attempts)

**Error Recovery:**

```python
class ErrorRecovery:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
    
    async def handle_error(self, error, step, context):
        if isinstance(error, TimeoutError):
            # Element not found - page structure may have changed
            return await self.trigger_replan(context, "element_not_found")
        
        elif isinstance(error, NetworkError):
            # Network issue - retry with exponential backoff
            return await self.retry_with_backoff(step, context)
        
        elif isinstance(error, SecurityException):
            # Security threat - terminate immediately
            return await self.terminate_session(context)
        
        elif isinstance(error, UserCancelledException):
            # User cancelled - cleanup and exit gracefully
            return await self.graceful_exit(context)
        
        else:
            # Unknown error - log and replan
            await self.log_error(error, context)
            return await self.trigger_replan(context, "unknown_error")
```


### 3.5 Security Layer - Kavach Protocol

**Remote Browser Isolation (RBI) Architecture:**

```
User Device                    AWS Infrastructure
    │                                 │
    │  Voice Command                  │
    ├────────────────────────────────>│
    │                                 │
    │                          ┌──────▼──────┐
    │                          │   Browser   │
    │                          │  (Isolated) │
    │                          └──────┬──────┘
    │                                 │
    │                          Actual Website
    │                                 │
    │  Audio Response + Status        │
    │<────────────────────────────────┤
    │                                 │
```

**Key Security Principles:**

1. **Zero Trust**: User device never directly connects to target websites
2. **Ephemeral Sessions**: Browser instances destroyed after each task
3. **Credential Isolation**: Credentials encrypted in memory, never persisted
4. **Visual Validation**: AI-powered phishing detection on every page load
5. **Audit Trail**: Complete logging without storing PII

**AWS WAF Configuration:**

```yaml
WebACL:
  Name: setu-waf
  Rules:
    - Name: RateLimitRule
      Priority: 1
      Statement:
        RateBasedStatement:
          Limit: 100  # requests per 5 minutes per IP
          AggregateKeyType: IP
      Action: Block
    
    - Name: GeoBlockingRule
      Priority: 2
      Statement:
        GeoMatchStatement:
          CountryCodes: [IN]  # Only allow India traffic
      Action: Allow
    
    - Name: SQLInjectionRule
      Priority: 3
      Statement:
        ManagedRuleGroupStatement:
          VendorName: AWS
          Name: AWSManagedRulesSQLiRuleSet
      Action: Block
    
    - Name: XSSRule
      Priority: 4
      Statement:
        ManagedRuleGroupStatement:
          VendorName: AWS
          Name: AWSManagedRulesKnownBadInputsRuleSet
      Action: Block
```

**Moondream Visual Security Checker:**

```python
# Pseudocode for Moondream-based phishing detection

class MoondreamSecurityChecker:
    def __init__(self):
        self.model = load_moondream_model()
        self.phishing_indicators = [
            "login form with suspicious domain",
            "urgent action required message",
            "fake security warnings",
            "hidden fees in small text",
            "misleading button labels",
            "fake government logos"
        ]
    
    async def analyze(self, screenshot_bytes):
        # Run Moondream vision model on screenshot
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        threats = {
            "phishing_detected": False,
            "dark_patterns": False,
            "dark_pattern_description": None,
            "confidence": 0.0
        }
        
        # Check for phishing indicators
        for indicator in self.phishing_indicators:
            prompt = f"Does this webpage show: {indicator}? Answer yes or no."
            response = self.model.query(image, prompt)
            
            if "yes" in response.lower():
                threats["phishing_detected"] = True
                threats["confidence"] = response.confidence
                break
        
        # Check for dark patterns
        dark_pattern_prompt = """
        Analyze this webpage for dark patterns:
        1. Hidden fees or charges
        2. Misleading button labels (e.g., 'No' button highlighted)
        3. Fake countdown timers
        4. Forced continuity (hard to cancel)
        5. Disguised ads
        
        Describe any dark patterns found.
        """
        
        dark_pattern_response = self.model.query(image, dark_pattern_prompt)
        
        if "no dark patterns" not in dark_pattern_response.lower():
            threats["dark_patterns"] = True
            threats["dark_pattern_description"] = dark_pattern_response
        
        return threats
```

**Credential Handling:**

```python
class SecureCredentialManager:
    def __init__(self, kms_client):
        self.kms = kms_client
        self.key_id = "alias/setu-credentials"
        self.memory_store = {}  # In-memory only, never persisted
    
    def encrypt_credential(self, session_id, credential_type, value):
        # Encrypt using AWS KMS
        encrypted = self.kms.encrypt(
            KeyId=self.key_id,
            Plaintext=value.encode()
        )
        
        # Store in memory with session ID
        key = f"{session_id}:{credential_type}"
        self.memory_store[key] = encrypted['CiphertextBlob']
        
        # Set TTL for automatic cleanup
        self.set_ttl(key, ttl_seconds=1800)  # 30 minutes
    
    def get_credential(self, session_id, credential_type):
        key = f"{session_id}:{credential_type}"
        encrypted = self.memory_store.get(key)
        
        if not encrypted:
            raise CredentialNotFoundException()
        
        # Decrypt using KMS
        decrypted = self.kms.decrypt(CiphertextBlob=encrypted)
        return decrypted['Plaintext'].decode()
    
    def destroy_session_credentials(self, session_id):
        # Remove all credentials for this session
        keys_to_delete = [k for k in self.memory_store.keys() if k.startswith(session_id)]
        for key in keys_to_delete:
            del self.memory_store[key]
```

**Session Destruction Protocol:**

```python
async def destroy_session(session_id):
    # 1. Close browser and clear browser data
    await executor.cleanup()
    
    # 2. Delete credentials from memory
    credential_manager.destroy_session_credentials(session_id)
    
    # 3. Delete session state from DynamoDB
    dynamodb.delete_item(
        TableName='SessionState',
        Key={'session_id': session_id}
    )
    
    # 4. Clear any cached data
    redis.delete(f"session:{session_id}:*")
    
    # 5. Log session termination (without PII)
    logger.info(f"Session {session_id} destroyed", extra={
        "event": "session_destroyed",
        "timestamp": datetime.utcnow().isoformat()
    })
```


### 3.6 Text-to-Speech (TTS) System

**Amazon Polly Configuration:**

```python
class PollyTTSEngine:
    def __init__(self, polly_client, cloudfront_domain):
        self.polly = polly_client
        self.cloudfront = cloudfront_domain
        self.voice_mapping = {
            'hi-IN': 'Aditi',      # Hindi (Female, Neural)
            'gu-IN': 'Aditi',      # Gujarati (use Hindi voice)
            'ta-IN': 'Aditi',      # Tamil (use Hindi voice)
            'te-IN': 'Aditi',      # Telugu (use Hindi voice)
            'bn-IN': 'Aditi',      # Bengali (use Hindi voice)
            'en-IN': 'Kajal',      # English-India (Female, Neural)
        }
    
    async def synthesize(self, text, language, session_id):
        voice_id = self.voice_mapping.get(language, 'Aditi')
        
        # Request speech synthesis
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine='neural',  # Higher quality
            LanguageCode=language,
            SampleRate='24000'
        )
        
        # Stream audio to S3
        audio_key = f"tts/{session_id}/{uuid.uuid4()}.mp3"
        s3.upload_fileobj(
            response['AudioStream'],
            bucket='setu-audio',
            key=audio_key
        )
        
        # Return CloudFront URL for fast delivery
        audio_url = f"https://{self.cloudfront}/{audio_key}"
        return audio_url
```

**Response Types and Templates:**

| Response Type | Example (Hindi) | Use Case |
|--------------|----------------|----------|
| Confirmation | "मैं IRCTC वेबसाइट खोल रहा हूं" | Action notification |
| Question | "आप कौन सी ट्रेन बुक करना चाहते हैं?" | User input request |
| Warning | "सावधान! यह वेबसाइट असुरक्षित लग रही है" | Security alert |
| Error | "क्षमा करें, पेज लोड नहीं हो रहा। फिर से कोशिश कर रहा हूं" | Error notification |
| Success | "आपका टिकट बुक हो गया। PNR नंबर है..." | Task completion |
| Explanation | "यह फील्ड आपकी जन्म तिथि के लिए है" | Field explanation |

**Streaming Strategy:**

```python
async def stream_audio_response(text, language, session_id):
    # For long responses, break into chunks and stream
    chunks = split_into_sentences(text)
    
    for i, chunk in enumerate(chunks):
        audio_url = await tts_engine.synthesize(chunk, language, session_id)
        
        # Send to client immediately (don't wait for all chunks)
        await websocket.send_json({
            "type": "audio_chunk",
            "url": audio_url,
            "sequence": i,
            "total_chunks": len(chunks)
        })
```

## Data Flow Diagram

```
┌─────────────┐
│    User     │
│   Device    │
└──────┬──────┘
       │
       │ 1. Voice Input (Audio Blob)
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│  POST /api/voice-input                                       │
│  - Validates session token                                   │
│  - Rate limiting (10 req/min)                                │
│  - Routes to Lambda                                          │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 2. Invoke Lambda
       ▼
┌─────────────────────────────────────────────────────────────┐
│              Lambda: VoiceInputHandler                       │
│  - Upload audio to S3                                        │
│  - Trigger Transcribe job                                    │
│  - Return job ID to client                                   │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 3. Transcribe Audio
       ▼
┌─────────────────────────────────────────────────────────────┐
│              AWS Transcribe (Whisper)                        │
│  - Transcribe audio to text                                  │
│  - Detect language                                           │
│  - Return transcript                                         │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 4. Extract Intent
       ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: IntentExtractor (Llama-3 8B)                 │
│  - Parse transcript                                          │
│  - Extract intent and parameters                             │
│  - Validate intent                                           │
│  - Store in DynamoDB (SessionState)                          │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 5. Generate Confirmation
       ▼
┌─────────────────────────────────────────────────────────────┐
│              Amazon Polly (TTS)                              │
│  - Synthesize confirmation message                           │
│  - Upload to S3                                              │
│  - Return CloudFront URL                                     │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 6. Send Audio URL to Client
       ▼
┌─────────────┐
│    User     │ ◄─── Plays confirmation audio
│   Device    │
└──────┬──────┘
       │
       │ 7. User Confirms (Voice)
       ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: PlanningEngine (Claude 3 Sonnet)             │
│  - Retrieve service template from DynamoDB                   │
│  - Generate action plan                                      │
│  - Store plan in DynamoDB                                    │
│  - Enqueue task in SQS                                       │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 8. Task Message
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQS Task Queue                            │
│  - Holds execution tasks                                     │
│  - Triggers Auto Scaling if queue depth > 100                │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 9. Poll for Tasks
       ▼
┌─────────────────────────────────────────────────────────────┐
│         EC2: Playwright Execution Worker                     │
│  - Receive task from SQS                                     │
│  - Launch browser                                            │
│  - Execute action plan                                       │
│  - Send progress updates via WebSocket                       │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 10. Navigate to Website
       ▼
┌─────────────────────────────────────────────────────────────┐
│              Target Website (e.g., IRCTC)                    │
│  - Accessed only from EC2 (RBI)                              │
│  - User device never directly connects                       │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 11. Page Screenshot
       ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: SecurityChecker (Moondream)                  │
│  - Analyze screenshot for phishing                           │
│  - Detect dark patterns                                      │
│  - Return threat assessment                                  │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 12. Progress Updates (WebSocket)
       ▼
┌─────────────┐
│    User     │ ◄─── Receives audio updates of each step
│   Device    │
└──────┬──────┘
       │
       │ 13. Task Complete
       ▼
┌─────────────────────────────────────────────────────────────┐
│         Lambda: TaskCompletionHandler                        │
│  - Generate success message                                  │
│  - Synthesize via Polly                                      │
│  - Destroy session (cleanup)                                 │
│  - Log to CloudWatch (no PII)                                │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ 14. Success Audio
       ▼
┌─────────────┐
│    User     │ ◄─── "आपका टिकट बुक हो गया"
│   Device    │
└─────────────┘
```


## Database & State Design

| Store | Technology | Data | TTL | Purpose |
|-------|-----------|------|-----|---------|
| SessionState | DynamoDB | session_id (PK), user_language, current_step, completed_steps, intent, plan_id, created_at | 30 min | Track active user sessions and execution progress |
| ServiceTemplates | DynamoDB | service_id (PK), version (SK), url, selectors, page_flows, error_patterns, updated_at | None | Store website interaction templates for each service |
| UserPreferences | DynamoDB | device_id (PK), preferred_language, voice_speed, accessibility_mode, last_used | 90 days | Remember user preferences across sessions |
| AuditLogs | CloudWatch Logs | timestamp, session_id, event_type, action, outcome, error_message (no PII) | 90 days | Compliance and debugging |
| TaskQueue | SQS | task_id, session_id, plan, priority, retry_count | 5 min visibility | Queue execution tasks for workers |
| AudioCache | S3 + CloudFront | session_id/audio_id.mp3 | 1 hour | Store TTS audio files for delivery |
| ScreenshotArchive | S3 | session_id/step_id.png | 24 hours | Audit trail and debugging |

**DynamoDB Table Schemas:**

```python
# SessionState Table
{
    "session_id": "sess_abc123",  # Partition Key
    "user_language": "hi-IN",
    "device_id": "device_xyz789",
    "intent": {
        "type": "book_train_ticket",
        "service": "irctc",
        "parameters": {...}
    },
    "plan_id": "plan_def456",
    "current_step": 5,
    "completed_steps": [1, 2, 3, 4],
    "execution_state": "in_progress",
    "created_at": 1702345678,
    "ttl": 1702347478  # 30 minutes from creation
}

# ServiceTemplates Table
{
    "service_id": "irctc",  # Partition Key
    "version": "v2.1",      # Sort Key
    "url": "https://www.irctc.co.in",
    "authentication": {
        "type": "form",
        "username_selector": "#userId",
        "password_selector": "#password",
        "submit_selector": "#loginButton"
    },
    "selectors": {
        "from_station": "#fromStation",
        "to_station": "#toStation",
        "travel_date": "#travelDate",
        "search_button": "#searchButton"
    },
    "page_flows": {
        "login": ["home", "login_form", "dashboard"],
        "book_ticket": ["dashboard", "search", "train_list", "passenger_details", "payment", "confirmation"]
    },
    "error_patterns": {
        "session_expired": "Your session has expired",
        "invalid_credentials": "Invalid username or password",
        "no_trains": "No trains available"
    },
    "updated_at": 1702345678,
    "is_active": true
}

# UserPreferences Table
{
    "device_id": "device_xyz789",  # Partition Key
    "preferred_language": "hi-IN",
    "voice_speed": 1.0,  # 0.5 to 2.0
    "accessibility_mode": {
        "high_contrast": true,
        "large_text": true,
        "screen_reader": false
    },
    "last_used": 1702345678,
    "ttl": 1710121678  # 90 days from last use
}
```

**State Transitions:**

```
Session Lifecycle:
created → intent_extracted → plan_generated → executing → completed/failed → destroyed

Execution States:
queued → in_progress → waiting_for_user → in_progress → completed
                    ↓
                  failed → replanning → in_progress
```

## API Design

### REST Endpoints

#### 1. POST /api/sessions

Create a new session

**Request:**
```json
{
  "device_id": "device_xyz789",
  "language": "hi-IN"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "session_token": "eyJhbGc...",
  "expires_at": 1702347478
}
```

#### 2. POST /api/voice-input

Submit voice input for processing

**Request:**
```json
{
  "session_id": "sess_abc123",
  "audio_format": "opus",
  "audio_data": "base64_encoded_audio",
  "duration_ms": 5000
}
```

**Response:**
```json
{
  "transcription_job_id": "job_123",
  "status": "processing",
  "estimated_completion_ms": 2000
}
```

#### 3. GET /api/transcription/{job_id}

Get transcription result

**Response:**
```json
{
  "job_id": "job_123",
  "status": "completed",
  "transcript": "मुझे पटना से दिल्ली की ट्रेन टिकट बुक करनी है",
  "language": "hi-IN",
  "confidence": 0.95,
  "intent": {
    "type": "book_train_ticket",
    "service": "irctc",
    "parameters": {
      "from": "Patna",
      "to": "Delhi"
    },
    "missing_parameters": ["travel_date", "passenger_count"]
  }
}
```

#### 4. POST /api/confirm-intent

Confirm intent and start execution

**Request:**
```json
{
  "session_id": "sess_abc123",
  "intent_confirmed": true,
  "additional_parameters": {
    "travel_date": "2024-12-16",
    "passenger_count": 1
  }
}
```

**Response:**
```json
{
  "plan_id": "plan_def456",
  "estimated_duration_seconds": 120,
  "steps_count": 12,
  "execution_started": true
}
```

#### 5. GET /api/session/{session_id}/status

Get current session status

**Response:**
```json
{
  "session_id": "sess_abc123",
  "status": "executing",
  "current_step": 5,
  "total_steps": 12,
  "progress_percentage": 42,
  "current_action": "Filling passenger details",
  "last_update": 1702345678
}
```

#### 6. DELETE /api/session/{session_id}

Cancel and destroy session

**Response:**
```json
{
  "session_id": "sess_abc123",
  "status": "destroyed",
  "cleanup_completed": true
}
```

### WebSocket Endpoint

#### WS /api/ws/session/{session_id}

Real-time updates during execution

**Client → Server Messages:**
```json
{
  "type": "user_input",
  "data": "12345",  // CAPTCHA, OTP, etc.
  "input_type": "captcha"
}

{
  "type": "confirmation",
  "confirmed": true
}

{
  "type": "cancel",
  "reason": "user_requested"
}
```

**Server → Client Messages:**
```json
{
  "type": "progress_update",
  "step": 5,
  "action": "Filling passenger details",
  "audio_url": "https://cdn.setu.ai/audio/sess_abc123/step5.mp3"
}

{
  "type": "user_input_required",
  "input_type": "captcha",
  "prompt": "कृपया CAPTCHA कोड बोलें",
  "audio_url": "https://cdn.setu.ai/audio/captcha_prompt.mp3",
  "timeout_seconds": 60
}

{
  "type": "security_warning",
  "severity": "high",
  "message": "Phishing attempt detected",
  "audio_url": "https://cdn.setu.ai/audio/security_warning.mp3"
}

{
  "type": "task_complete",
  "result": {
    "pnr": "1234567890",
    "confirmation": "Ticket booked successfully"
  },
  "audio_url": "https://cdn.setu.ai/audio/success.mp3"
}

{
  "type": "error",
  "error_code": "EXECUTION_FAILED",
  "message": "Unable to complete task",
  "retry_possible": true
}
```


## Infrastructure & Cost Model

| AWS Component | Configuration | Cost per Task | Notes |
|--------------|---------------|---------------|-------|
| **Compute** |
| EC2 Spot (t3.medium) | 2 vCPU, 4GB RAM, Ubuntu 22.04 | ₹0.15 | Playwright execution, 70% savings vs on-demand |
| Lambda (Node.js 18) | 512MB memory, 30s timeout | ₹0.05 | API handlers, intent extraction |
| **AI/ML Services** |
| Transcribe (Whisper) | Streaming, 10s audio average | ₹0.12 | Speech-to-text |
| Bedrock (Llama-3 8B) | Intent extraction, 500 tokens | ₹0.01 | Fast intent classification |
| Bedrock (Llama-3 70B) | Planning, 2000 tokens | ₹0.20 | Complex reasoning (50% of tasks) |
| Bedrock (Claude 3 Sonnet) | Error recovery, 1500 tokens | ₹0.30 | Used only for failures (10% of tasks) |
| Polly (Neural) | 200 characters average | ₹0.08 | Text-to-speech |
| **Storage & Data** |
| DynamoDB | On-demand, 10 read/write units | ₹0.02 | Session state, templates |
| S3 | Standard, 5MB per task | ₹0.01 | Audio, screenshots |
| CloudFront | 5MB transfer | ₹0.03 | CDN for audio delivery |
| **Networking** |
| API Gateway | 10 requests per task | ₹0.01 | REST API |
| Data Transfer | 10MB out | ₹0.02 | To user device |
| **Total per Task** | | **₹0.70 - ₹1.00** | Varies by complexity |

**Cost Optimization Strategies:**

1. **Intelligent Model Selection**:
   - Use Llama-3 8B (₹0.001/1K tokens) for simple tasks
   - Use Llama-3 70B (₹0.008/1K tokens) for medium complexity
   - Use Claude 3 Sonnet (₹0.30/1K tokens) only for error recovery

2. **EC2 Spot Instances**:
   - 70% cost savings vs on-demand
   - Graceful handling of spot interruptions
   - Fallback to on-demand if spot unavailable

3. **Audio Compression**:
   - Opus codec at 16 kbps reduces Transcribe costs
   - ~120 KB per minute vs 1.4 MB uncompressed

4. **Caching**:
   - Cache service templates in memory
   - Cache common TTS responses
   - CloudFront caching for static assets

5. **Session Timeouts**:
   - 30-minute TTL prevents resource waste
   - Automatic cleanup of abandoned sessions

**R&D Cost Optimization:**

For local development and testing, use Ollama to avoid cloud costs:

```bash
# Local R&D Setup (M1 Mac + RTX 2050)
ollama pull llama3:8b      # Intent extraction testing
ollama pull llama3:70b     # Planning logic development
ollama pull moondream      # Visual security testing

# Estimated savings: ₹50,000/month during development
```

**Scaling Cost Projections:**

| Users | Tasks/Day | Monthly Cost | Cost per User |
|-------|-----------|--------------|---------------|
| 1,000 | 5,000 | ₹3,500 | ₹3.50 |
| 10,000 | 50,000 | ₹35,000 | ₹3.50 |
| 100,000 | 500,000 | ₹3,50,000 | ₹3.50 |
| 1,000,000 | 5,000,000 | ₹35,00,000 | ₹3.50 |

Note: Cost per user remains constant due to pay-per-use pricing model.

## Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                         │
│  - Frontend (Next.js PWA)                                        │
│  - Backend (Lambda functions)                                    │
│  - Execution Worker (Python + Playwright)                        │
│  - Infrastructure (Terraform/CloudFormation)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Push to main branch
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Actions CI/CD                        │
│  1. Run tests (unit, integration, property-based)                │
│  2. Build frontend (Next.js build)                               │
│  3. Build Lambda packages (zip)                                  │
│  4. Build EC2 AMI (Packer)                                       │
│  5. Run security scans (Snyk, OWASP)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ All checks pass
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS CodePipeline                              │
│  Stage 1: Source (GitHub)                                        │
│  Stage 2: Build (CodeBuild)                                      │
│  Stage 3: Deploy to Staging                                      │
│  Stage 4: Integration Tests                                      │
│  Stage 5: Manual Approval                                        │
│  Stage 6: Deploy to Production                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Deploy artifacts
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Infrastructure                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Amplify     │  │   Lambda     │  │  EC2 ASG     │          │
│  │  (Frontend)  │  │  (Backend)   │  │  (Workers)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CloudFormation/Terraform                                 │   │
│  │  - VPC, Subnets, Security Groups                          │   │
│  │  - DynamoDB Tables                                        │   │
│  │  - S3 Buckets                                             │   │
│  │  - CloudFront Distribution                                │   │
│  │  - WAF Rules                                              │   │
│  │  - IAM Roles and Policies                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Deployment Environments:**

1. **Development**: Local (Ollama + mock services)
2. **Staging**: AWS (Mumbai region, reduced capacity)
3. **Production**: AWS (Mumbai region, full capacity)

**Rollback Strategy:**

- Blue-Green deployment for Lambda functions
- Rolling updates for EC2 Auto Scaling Group
- CloudFront cache invalidation for frontend updates
- Database migrations with backward compatibility
- Automated rollback on error rate > 5%

## Phased Rollout Plan

### v0.1 - MVP (Hackathon Demo) - Week 1-2

**Scope:**
- Single service: IRCTC train booking
- Single language: Hindi
- Basic voice input/output
- Manual CAPTCHA handling
- No security layer (demo only)

**Components:**
- Basic PWA with voice input
- Transcribe integration
- Llama-3 8B for intent
- Llama-3 70B for planning
- Playwright execution (single EC2 instance)
- Polly TTS

**Goal:** Demonstrate end-to-end voice-to-booking flow

### v0.5 - Alpha - Week 3-4

**Scope:**
- 3 services: IRCTC, DigiLocker, UIDAI
- 3 languages: Hindi, Gujarati, Tamil
- Kavach Protocol (RBI + basic security)
- Session management
- Error recovery

**Components:**
- Enhanced PWA with offline support
- DynamoDB for state management
- Moondream for phishing detection
- SQS task queue
- Auto Scaling for EC2

**Goal:** Internal testing with 50 users

### v1.0 - Beta - Week 5-8

**Scope:**
- 5 services: IRCTC, DigiLocker, SBI, UIDAI, Electricity
- 10 languages (all supported)
- Full Kavach Protocol
- Guided decision support
- Audit logging

**Components:**
- Production-ready PWA (<10MB)
- Complete API suite
- CloudWatch monitoring
- X-Ray tracing
- WAF protection

**Goal:** Public beta with 1,000 users

### v1.5 - Production - Week 9-12

**Scope:**
- Performance optimization
- Cost optimization
- Advanced error recovery
- Analytics dashboard
- User feedback system

**Components:**
- Multi-region support (future)
- Advanced caching
- Predictive scaling
- A/B testing framework

**Goal:** Scale to 10,000 concurrent users


## Open Design Questions

### 1. CAPTCHA Handling Strategy (Target: v0.5)

**Question:** Should we implement automated CAPTCHA solving using ML models, or continue with user-assisted approach?

**Options:**
- A) User-assisted (current): Pause and ask user to speak CAPTCHA
- B) ML-based: Use OCR/vision models to solve automatically
- C) Hybrid: Try ML first, fallback to user assistance

**Trade-offs:**
- Option A: Simple, reliable, but interrupts flow
- Option B: Seamless, but may fail on complex CAPTCHAs and violate ToS
- Option C: Best UX, but complex implementation

**Decision needed by:** v0.5 (Alpha)

### 2. Multi-Region Deployment (Target: v1.5)

**Question:** Should we deploy to multiple AWS regions for lower latency and disaster recovery?

**Considerations:**
- Mumbai region serves most of India adequately
- Multi-region adds complexity and cost
- Latency to Northeast India and Andaman/Nicobar could be improved
- Data residency requirements for DPDP Act 2023

**Decision needed by:** v1.5 (Production)

### 3. Voice Biometrics for Authentication (Target: v2.0)

**Question:** Should we implement voice biometrics to authenticate users instead of passwords?

**Benefits:**
- More accessible for low-literacy users
- Eliminates need to speak passwords aloud
- Stronger security than weak passwords

**Concerns:**
- Voice can be recorded and replayed
- Accuracy with background noise
- Privacy implications of storing voice prints
- DPDP Act 2023 compliance for biometric data

**Decision needed by:** v2.0 (Future)

### 4. Offline Mode Capabilities (Target: v2.0)

**Question:** How much functionality should work completely offline?

**Current:** Voice recording works offline, syncs when online
**Possible:** Local speech recognition using on-device models

**Trade-offs:**
- On-device models: Larger app size (100MB+), lower accuracy
- Cloud-only: Requires connectivity, better accuracy
- Hybrid: Complex, but best UX

**Decision needed by:** v2.0 (Future)

### 5. Service Template Maintenance Strategy (Target: v1.0)

**Question:** How should we handle website changes that break templates?

**Options:**
- A) Manual updates by dev team
- B) Automated detection + manual fix
- C) AI-powered template adaptation
- D) Crowdsourced template updates

**Current approach:** Option B (automated detection + manual fix)

**Decision needed by:** v1.0 (Beta) - need sustainable long-term strategy

### 6. Cost Optimization for Scale (Target: v1.5)

**Question:** At what scale should we switch from Bedrock to self-hosted models?

**Analysis:**
- Current: Bedrock (pay-per-use) - optimal for <100K users
- Break-even: ~500K users/month
- Self-hosted: EC2 GPU instances + model optimization

**Decision needed by:** v1.5 (Production) - before scaling to 1M users

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Audio Processing Properties

**Property 1: Universal Transcription**
*For any* audio input in a supported language (including code-mixed and dialect variations), the Audio_Pipeline should successfully transcribe it to text with confidence score above 0.7 or request user repetition if confidence is below threshold.
**Validates: Requirements FR-01.1, FR-01.2, FR-01.3, FR-01.9**

**Property 2: Intent Extraction Completeness**
*For any* transcribed text representing a valid user request, the Intent_Gatekeeper should extract a structured intent containing service type, action, and all extractable parameters.
**Validates: Requirements FR-01.4, FR-06.1, FR-06.5**

**Property 3: Low Confidence Clarification**
*For any* intent with confidence below 0.80, the System should generate clarifying questions in the user's language and wait for user response before proceeding.
**Validates: Requirements FR-01.5, FR-06.3**

**Property 4: Language-Consistent Responses**
*For any* confirmed intent in language L, all TTS responses should be generated in the same language L throughout the session.
**Validates: Requirements FR-01.6**

### Execution Properties

**Property 5: Browser Isolation**
*For any* task execution, the browser instance should run on AWS infrastructure and the user's device should never directly connect to the target website.
**Validates: Requirements FR-03.1**

**Property 6: Comprehensive Form Filling**
*For any* form with fields specified in the action plan, the Playwright_Engine should locate and fill all fields according to the plan, handling text inputs, dropdowns, and selections.
**Validates: Requirements FR-02.3, FR-02.4, FR-02.5**

**Property 7: Page Navigation Reliability**
*For any* URL in an action plan, the Playwright_Engine should navigate to it and wait for page readiness (networkidle state) before proceeding to the next step.
**Validates: Requirements FR-02.2**

**Property 8: Progress Transparency**
*For any* executing step in an action plan, the System should send an audio progress update to the user describing the current action.
**Validates: Requirements FR-02.10**

**Property 9: Screenshot Audit Trail**
*For any* major step in task execution (navigation, form submission, confirmation), the System should capture and store a screenshot with session_id and step_id.
**Validates: Requirements FR-02.12**

**Property 10: User Confirmation for Critical Actions**
*For any* action involving financial transactions or irreversible changes, the System should request explicit user confirmation via voice before proceeding.
**Validates: Requirements FR-02.8, FR-04.4, FR-04.5**

### Security Properties

**Property 11: Visual Security Validation**
*For any* page load during execution, the Moondream vision model should analyze the screenshot for phishing indicators and dark patterns before allowing interaction.
**Validates: Requirements FR-03.2**

**Property 12: Ephemeral Credential Storage**
*For any* credentials provided during a session, they should be stored only in encrypted memory and completely destroyed within 60 seconds of session termination.
**Validates: Requirements FR-03.5, FR-03.8, FR-03.9**

**Property 13: TLS Encryption**
*For any* data transmission between client and server, TLS 1.3 encryption should be used.
**Validates: Requirements FR-03.7**

**Property 14: PII-Free Logging**
*For any* log entry created by the System, it should not contain Personally Identifiable Information, credentials, or sensitive user data.
**Validates: Requirements FR-03.12, FR-10.3**

**Property 15: Session Cleanup Completeness**
*For any* terminated session (expired, completed, or cancelled), all associated data (browser instance, credentials, session state, cached data) should be destroyed within 60 seconds.
**Validates: Requirements FR-03.8, FR-09.6, FR-09.8**

### Planning and Replanning Properties

**Property 16: Valid Action Plan Generation**
*For any* confirmed intent, the Planning_Engine should generate a structured JSON action plan containing sequential steps with all required fields (step_id, action, selector/target, description, user_message).
**Validates: Requirements FR-07.1, FR-07.3**

**Property 17: Stateful Replanning**
*For any* execution failure, the Planning_Engine should generate a new plan that includes context from the failed attempt (completed steps, error message, page state) and continues from the failure point.
**Validates: Requirements FR-02.11, FR-07.4, FR-07.5**

**Property 18: Template-Guided Planning**
*For any* service with an available template, the Planning_Engine should use the template's selectors and page flows to generate more accurate plans than without the template.
**Validates: Requirements FR-08.6**

### Guided Decision Support Properties

**Property 19: Field Explanation**
*For any* form field encountered during execution, the System should generate a simple-language explanation of the field's purpose and speak it to the user.
**Validates: Requirements FR-04.1**

**Property 20: Input Validation Warnings**
*For any* user-provided input that fails validation (invalid format, out of range, etc.), the System should warn the user and suggest corrections before proceeding.
**Validates: Requirements FR-04.2**

**Property 21: Option Implication Explanation**
*For any* decision point with multiple options, the System should explain the implications of each choice to the user.
**Validates: Requirements FR-04.3**

**Property 22: Task Completion Summary**
*For any* successfully completed task, the System should generate and speak a summary of what was accomplished, including key details (PNR numbers, confirmation codes, etc.).
**Validates: Requirements FR-04.7**

**Property 23: Non-Technical Error Explanation**
*For any* error that occurs during execution, the System should generate an explanation in non-technical language and suggest next steps to the user.
**Validates: Requirements FR-04.8**

**Property 24: Context-Aware Interaction**
*For any* question asked by the System, if the user has already provided that information in the current session, the System should not ask again.
**Validates: Requirements FR-04.9**

### Accessibility Properties

**Property 25: Zero-Read Zero-Type Interface**
*For any* core user interaction (task initiation, confirmation, cancellation), it should be completable entirely through voice commands without reading text or typing.
**Validates: Requirements FR-05.5, FR-05.6, FR-05.11**

**Property 26: Offline Voice Recording**
*For any* voice input when network is unavailable, the Client_PWA should record and cache the audio locally, then sync when connectivity is restored.
**Validates: Requirements FR-05.9**

**Property 27: Adaptive Audio Streaming**
*For any* TTS audio response, the bitrate should adapt based on current network conditions (lower bitrate on 2G, higher on WiFi).
**Validates: Requirements FR-05.8**

### Session Management Properties

**Property 28: Unique Session Creation**
*For any* task initiation, the System should create a unique session with a globally unique session_id.
**Validates: Requirements FR-09.1**

**Property 29: Session State Completeness**
*For any* active session, the stored session state should include current_step, completed_steps, pending_steps, intent, plan_id, and user_preferences.
**Validates: Requirements FR-09.4, FR-09.5**

**Property 30: Session Resumption**
*For any* interrupted session within its TTL period, the System should allow resumption from the last completed step using the session_id.
**Validates: Requirements FR-09.3**

**Property 31: Concurrent Session Isolation**
*For any* two concurrent sessions from different users, modifications to one session should not affect the state of the other session.
**Validates: Requirements FR-09.7, FR-09.10**

### Service Template Properties

**Property 32: Template Structure Completeness**
*For any* service template, it should include service_id, url, authentication config, CSS selectors for common elements, page flows, error patterns, and language-specific field labels.
**Validates: Requirements FR-08.3, FR-08.4, FR-08.5, FR-08.10**

**Property 33: Template Mismatch Detection**
*For any* execution where a selector from the template is not found on the page, the System should log a template mismatch event with the service_id and missing selector.
**Validates: Requirements FR-08.7**

### Audit and Compliance Properties

**Property 34: Comprehensive Interaction Logging**
*For any* user interaction (voice input, confirmation, cancellation), the System should create a log entry in CloudWatch containing timestamp, session_id, action, and outcome.
**Validates: Requirements FR-10.1, FR-10.2**

**Property 35: Security Event Logging**
*For any* security event (phishing detection, suspicious voice pattern, WAF block), the System should log it with severity level (low, medium, high, critical).
**Validates: Requirements FR-10.4**

**Property 36: Error Detail Logging**
*For any* task failure, the Audit_Log should include error details, stack trace, and execution context without including PII.
**Validates: Requirements FR-10.7**

### Intent Validation Properties

**Property 37: Malicious Intent Rejection**
*For any* intent classified as malicious (e.g., "transfer all money", "delete account"), the Intent_Gatekeeper should reject it and explain the security concern to the user.
**Validates: Requirements FR-06.8**

**Property 38: Missing Parameter Detection**
*For any* intent with required parameters missing, the System should identify the missing parameters and ask the user to provide them specifically.
**Validates: Requirements FR-06.6**

**Property 39: Multi-Intent Disambiguation**
*For any* transcribed text containing multiple possible intents, the System should present the options to the user and ask them to choose one.
**Validates: Requirements FR-06.4**

**Property 40: Intent Confirmation Before Planning**
*For any* extracted intent, the System should confirm it with the user and receive explicit approval before generating an action plan.
**Validates: Requirements FR-06.7**

### Retry and Recovery Properties

**Property 41: Exponential Backoff Retry**
*For any* transient failure (network timeout, temporary page unavailability), the Execution_Layer should retry with exponentially increasing delays (1s, 2s, 4s, 8s) up to a maximum of 3 attempts.
**Validates: Requirements FR-07.10**

**Property 42: User Input Pause**
*For any* step requiring user input (CAPTCHA, OTP, manual verification), the System should pause execution, request input via voice, and wait for user response with a timeout.
**Validates: Requirements FR-07.9**

**Property 43: Success Verification**
*For any* completed execution, the System should verify task success by checking for confirmation indicators on the webpage before reporting completion to the user.
**Validates: Requirements FR-07.12**


## Error Handling

### Error Categories and Responses

| Error Category | Examples | System Response | User Experience |
|---------------|----------|-----------------|-----------------|
| **Transcription Errors** | Low confidence, background noise, unsupported language | Request user to repeat, suggest quieter environment | "मुझे आपकी आवाज़ साफ़ नहीं सुनाई दी। कृपया फिर से बोलें" |
| **Intent Errors** | Ambiguous intent, unsupported service, malicious intent | Ask clarifying questions, explain limitations, reject with reason | "मुझे समझ नहीं आया। क्या आप IRCTC पर टिकट बुक करना चाहते हैं?" |
| **Planning Errors** | Missing template, invalid parameters, service unavailable | Request missing info, suggest alternatives, graceful degradation | "इस सेवा के लिए मुझे और जानकारी चाहिए" |
| **Execution Errors** | Element not found, timeout, network failure | Retry with backoff, replan, request user assistance | "पेज लोड नहीं हो रहा। फिर से कोशिश कर रहा हूं" |
| **Security Errors** | Phishing detected, suspicious activity, credential theft attempt | Immediate termination, warn user, log incident | "सावधान! यह वेबसाइट असुरक्षित है। मैं इसे बंद कर रहा हूं" |
| **Session Errors** | Session expired, concurrent modification, invalid session ID | Create new session, resolve conflict, request re-authentication | "आपका सेशन समाप्त हो गया। कृपया फिर से शुरू करें" |
| **Infrastructure Errors** | AWS service outage, database unavailable, queue full | Retry, fallback to backup, queue request, notify user | "सिस्टम व्यस्त है। कृपया थोड़ी देर बाद कोशिश करें" |

### Error Recovery Strategies

#### 1. Automatic Retry with Exponential Backoff

```python
async def retry_with_backoff(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            delay = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(delay)
            logger.info(f"Retry attempt {attempt + 1} after {delay}s")
```

#### 2. Stateful Replanning

When execution fails, the Planning_Engine generates a new plan that:
- Preserves completed steps (no redundant work)
- Includes error context for better decision-making
- Adapts to changed page structure
- Suggests alternative approaches

#### 3. Graceful Degradation

When non-critical features fail:
- Continue with core functionality
- Notify user of limitations
- Log degraded state for monitoring
- Restore when service recovers

Example: If Moondream security check fails, continue with execution but log warning.

#### 4. User-Assisted Recovery

For errors requiring human judgment:
- Explain the problem in simple language
- Provide options (retry, skip, cancel)
- Accept voice commands for choice
- Resume from user's decision

Example: CAPTCHA solving, ambiguous form fields, unexpected page layouts.

### Error Logging and Monitoring

All errors are logged to CloudWatch with:
- Error type and severity
- Session ID (for tracing)
- Stack trace (for debugging)
- Context (page URL, current step)
- No PII or credentials

CloudWatch Alarms trigger on:
- Error rate > 5% (warning)
- Error rate > 10% (critical)
- Security events (immediate alert)
- Infrastructure failures (immediate alert)

## Testing Strategy

### Dual Testing Approach

Setu uses both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and integration points
**Property Tests**: Verify universal properties across all inputs

Together, they provide comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness.

### Property-Based Testing

**Framework**: Hypothesis (Python) for backend, fast-check (TypeScript) for frontend

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each test tagged with: `Feature: setu-voice-agent, Property {number}: {property_text}`
- Shrinking enabled to find minimal failing examples
- Seed-based reproducibility for CI/CD

**Example Property Test**:

```python
from hypothesis import given, strategies as st
import pytest

@given(
    language=st.sampled_from(['hi-IN', 'gu-IN', 'ta-IN', 'te-IN', 'bn-IN']),
    text=st.text(min_size=10, max_size=500)
)
@pytest.mark.property_test
@pytest.mark.tag("Feature: setu-voice-agent, Property 4: Language-Consistent Responses")
def test_language_consistent_responses(language, text):
    """
    Property 4: For any confirmed intent in language L, all TTS responses 
    should be generated in the same language L throughout the session.
    """
    # Create session with specified language
    session = create_session(language=language)
    
    # Confirm intent
    intent = extract_intent(text, language)
    confirm_intent(session, intent)
    
    # Generate multiple responses
    responses = [
        generate_confirmation(session),
        generate_progress_update(session, "step 1"),
        generate_completion_message(session)
    ]
    
    # Verify all responses are in the same language
    for response in responses:
        assert response.language == language
        assert is_valid_language_text(response.text, language)
```

### Unit Testing Strategy

**Framework**: pytest (Python), Jest (TypeScript)

**Coverage Areas**:

1. **API Endpoints**: Test each REST/WebSocket endpoint with valid/invalid inputs
2. **Intent Extraction**: Test specific examples of intents in each language
3. **Planning Logic**: Test plan generation for each supported service
4. **Playwright Actions**: Test each action type (click, input, select, navigate)
5. **Security Checks**: Test phishing detection with known phishing pages
6. **Session Management**: Test session creation, resumption, expiration
7. **Error Handling**: Test each error category with specific error conditions

**Example Unit Test**:

```python
def test_irctc_login_flow():
    """Test IRCTC login with valid credentials"""
    executor = PlaywrightExecutor()
    plan = {
        "steps": [
            {"action": "navigate", "target": "https://www.irctc.co.in"},
            {"action": "click", "selector": "#loginButton"},
            {"action": "input", "selector": "#username", "value": "testuser"},
            {"action": "input", "selector": "#password", "value": "testpass"},
            {"action": "click", "selector": "#submitButton"}
        ]
    }
    
    result = await executor.execute_plan(plan, session_id="test_123")
    
    assert result["status"] == "success"
    assert "dashboard" in result["final_url"]
```

### Integration Testing

**Scope**: End-to-end flows across multiple components

**Test Scenarios**:
1. Complete train booking flow (voice → transcribe → plan → execute → confirm)
2. Phishing detection and session termination
3. Session interruption and resumption
4. Multi-language switching within session
5. Error recovery and replanning
6. Concurrent user sessions

**Environment**: Staging environment with mock government websites

### Performance Testing

**Tools**: Locust (load testing), AWS X-Ray (tracing)

**Metrics**:
- Transcription latency: < 2s for 10s audio
- Intent extraction: < 1s
- Plan generation: < 5s
- Page navigation: < 3s
- End-to-end task: < 2 minutes

**Load Tests**:
- 1,000 concurrent users
- 10,000 requests per minute
- Sustained load for 1 hour
- Spike testing (sudden 10x increase)

### Security Testing

**Automated Scans**:
- OWASP ZAP for web vulnerabilities
- Snyk for dependency vulnerabilities
- AWS Inspector for infrastructure security

**Manual Testing**:
- Penetration testing by security experts
- Phishing page detection accuracy
- Credential leakage prevention
- Session hijacking attempts

**Compliance Testing**:
- DPDP Act 2023 compliance audit
- PII handling verification
- Data retention policy validation
- Audit log completeness

### Accessibility Testing

**Automated**:
- Lighthouse accessibility score > 90
- WCAG 2.1 AA compliance
- Color contrast ratio > 4.5:1

**Manual**:
- Screen reader compatibility (TalkBack, VoiceOver)
- Voice-only navigation (no touch required)
- Low-vision user testing
- Low-literacy user testing

### Test Coverage Goals

| Component | Unit Test Coverage | Property Test Coverage | Integration Test Coverage |
|-----------|-------------------|----------------------|--------------------------|
| Audio Pipeline | 80% | 5 properties | 3 scenarios |
| Intent Extraction | 85% | 8 properties | 4 scenarios |
| Planning Engine | 80% | 6 properties | 5 scenarios |
| Execution Layer | 90% | 10 properties | 8 scenarios |
| Security Layer | 95% | 5 properties | 6 scenarios |
| Session Management | 85% | 6 properties | 4 scenarios |
| API Layer | 90% | 3 properties | 10 scenarios |

### Continuous Testing

**CI/CD Pipeline**:
1. Pre-commit: Linting, type checking
2. On PR: Unit tests, property tests (100 iterations)
3. On merge: Full test suite, integration tests
4. Nightly: Extended property tests (1000 iterations), performance tests
5. Weekly: Security scans, accessibility audits

**Test Data Management**:
- Synthetic test data (no real user data)
- Mock government websites for testing
- Recorded audio samples in all languages
- Known phishing pages for security testing

### Monitoring and Observability in Production

**Real-Time Monitoring**:
- CloudWatch dashboards for key metrics
- X-Ray tracing for request flows
- Error rate alerts (> 5%)
- Latency alerts (> 3s for critical paths)

**User Experience Monitoring**:
- Task completion rate
- Average task duration
- User cancellation rate
- Error recovery success rate

**Cost Monitoring**:
- Cost per task tracking
- AWS service usage by component
- Spot instance interruption rate
- Model selection distribution (8B vs 70B vs Claude)
