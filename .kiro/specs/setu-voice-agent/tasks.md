# Implementation Plan: Setu - Voice-First Autonomous Web Agent

## Overview

This implementation plan breaks down the Setu voice-first autonomous web agent into incremental, testable tasks. The approach follows a phased rollout strategy starting with MVP functionality (single service, single language) and progressively adding features. Each task builds on previous work, with property-based tests integrated throughout to ensure correctness.

## Tasks

- [ ] 1. Set up project infrastructure and development environment
  - Initialize monorepo structure with frontend (Next.js) and backend (Python) workspaces
  - Configure AWS CDK/Terraform for infrastructure as code
  - Set up local development environment with Ollama for R&D
  - Configure CI/CD pipeline with GitHub Actions
  - Set up testing frameworks: pytest + Hypothesis (Python), Jest + fast-check (TypeScript)
  - _Requirements: NFR-06_

- [ ] 2. Implement core data models and database schemas
  - [ ] 2.1 Create DynamoDB table definitions for SessionState, ServiceTemplates, UserPreferences, and AuditLogs
    - Define table schemas with partition keys, sort keys, and TTL attributes
    - Implement GSIs for common query patterns
    - _Requirements: FR-08, FR-09, FR-10_
  
  - [ ] 2.2 Implement Python data models for session state, intent, and action plans
    - Create Pydantic models for type safety and validation
    - Implement serialization/deserialization methods
    - _Requirements: FR-06, FR-07, FR-09_
  
  - [ ]* 2.3 Write property tests for data model serialization
    - **Property: Serialization round trip** - For any valid system object, serializing then deserializing should produce an equivalent object
    - **Validates: Requirements FR-09.2**
  
  - [ ] 2.4 Create service template structure for IRCTC
    - Define template JSON schema with selectors, page flows, and error patterns
    - Implement template validation logic
    - _Requirements: FR-08.1, FR-08.3, FR-08.4, FR-08.5_
  
  - [ ]* 2.5 Write property test for template structure completeness
    - **Property 32: Template Structure Completeness** - For any service template, it should include all required fields
    - **Validates: Requirements FR-08.3, FR-08.4, FR-08.5, FR-08.10**

- [ ] 3. Build audio pipeline with AWS Transcribe integration
  - [ ] 3.1 Implement audio upload to S3 with compression
    - Create Lambda function to receive audio blobs from client
    - Implement Opus codec compression
    - Upload to S3 with session-based key structure
    - _Requirements: FR-01_
  
  - [ ] 3.2 Integrate AWS Transcribe for speech-to-text
    - Configure Transcribe with language-specific models
    - Implement streaming transcription for real-time feedback
    - Add custom vocabulary for government service terms
    - _Requirements: FR-01.1, FR-01.7_
  
  - [ ]* 3.3 Write property test for universal transcription
    - **Property 1: Universal Transcription** - For any audio input in supported language, transcription should succeed or request repetition
    - **Validates: Requirements FR-01.1, FR-01.2, FR-01.3, FR-01.9**
  
  - [ ] 3.4 Implement background noise detection and handling
    - Analyze audio quality metrics from Transcribe
    - Request user repetition when noise exceeds threshold
    - _Requirements: FR-01.9_

- [ ] 4. Implement Intent Gatekeeper with Llama-3 8B
  - [ ] 4.1 Create intent extraction service using AWS Bedrock
    - Integrate Llama-3 8B model via Bedrock API
    - Design prompt template for intent extraction
    - Parse model output into structured intent JSON
    - _Requirements: FR-01.4, FR-06.1, FR-06.2_
  
  - [ ] 4.2 Implement intent validation and confidence scoring
    - Calculate confidence scores from model output
    - Implement malicious intent detection rules
    - Validate extracted parameters against expected types
    - _Requirements: FR-06.3, FR-06.8_
  
  - [ ]* 4.3 Write property test for intent extraction completeness
    - **Property 2: Intent Extraction Completeness** - For any valid user request, intent should be extracted with service, action, and parameters
    - **Validates: Requirements FR-01.4, FR-06.1, FR-06.5**
  
  - [ ]* 4.4 Write property test for malicious intent rejection
    - **Property 37: Malicious Intent Rejection** - For any malicious intent, it should be rejected with explanation
    - **Validates: Requirements FR-06.8**
  
  - [ ] 4.5 Implement clarifying question generation for low-confidence intents
    - Generate context-aware questions in user's language
    - Handle multi-turn clarification conversations
    - _Requirements: FR-01.5, FR-06.3_
  
  - [ ]* 4.6 Write property test for low confidence clarification
    - **Property 3: Low Confidence Clarification** - For any intent below 0.80 confidence, clarifying questions should be generated
    - **Validates: Requirements FR-01.5, FR-06.3**

- [ ] 5. Build Planning Engine with Claude 3 Sonnet / Llama-3 70B
  - [ ] 5.1 Implement model selection logic based on task complexity
    - Create complexity scoring algorithm
    - Route to Llama-3 8B, Llama-3 70B, or Claude 3 Sonnet
    - _Requirements: FR-07, NFR-04_
  
  - [ ] 5.2 Create action plan generation with service templates
    - Design prompt template with service template context
    - Generate structured JSON action plans
    - Validate plan structure and completeness
    - _Requirements: FR-07.1, FR-07.3, FR-08.6_
  
  - [ ]* 5.3 Write property test for valid action plan generation
    - **Property 16: Valid Action Plan Generation** - For any confirmed intent, a structured JSON plan should be generated
    - **Validates: Requirements FR-07.1, FR-07.3**
  
  - [ ] 5.4 Implement stateful replanning for execution failures
    - Capture execution context (completed steps, error, page state)
    - Generate new plan incorporating failure context
    - Preserve completed work to avoid redundancy
    - _Requirements: FR-02.11, FR-07.4, FR-07.5_
  
  - [ ]* 5.5 Write property test for stateful replanning
    - **Property 17: Stateful Replanning** - For any execution failure, new plan should include context and continue from failure point
    - **Validates: Requirements FR-02.11, FR-07.4, FR-07.5**

- [ ] 6. Checkpoint - Verify AI pipeline functionality
  - Test end-to-end flow: audio → transcribe → intent → plan
  - Ensure all tests pass, ask the user if questions arise

- [ ] 7. Implement Playwright Execution Engine
  - [ ] 7.1 Create EC2 worker setup with Playwright and Chromium
    - Build AMI with Ubuntu 22.04, Python 3.11, Playwright
    - Configure Auto Scaling Group with Spot instances
    - Set up SQS queue for task distribution
    - _Requirements: FR-02, FR-07.7, FR-07.8_
  
  - [ ] 7.2 Implement core Playwright execution loop
    - Create PlaywrightExecutor class with browser lifecycle management
    - Implement action handlers: navigate, click, input, select, wait
    - Add screenshot capture at each major step
    - _Requirements: FR-02.1, FR-02.2, FR-02.12_
  
  - [ ]* 7.3 Write property test for browser isolation
    - **Property 5: Browser Isolation** - For any task execution, browser should run on AWS and user device should never connect directly
    - **Validates: Requirements FR-03.1**
  
  - [ ]* 7.4 Write property test for page navigation reliability
    - **Property 7: Page Navigation Reliability** - For any URL, navigation should complete and wait for page readiness
    - **Validates: Requirements FR-02.2**
  
  - [ ] 7.3 Implement form filling logic for all field types
    - Handle text inputs, dropdowns, radio buttons, checkboxes
    - Implement smart selector fallback strategies
    - Add field validation before submission
    - _Requirements: FR-02.3, FR-02.4, FR-02.5_
  
  - [ ]* 7.6 Write property test for comprehensive form filling
    - **Property 6: Comprehensive Form Filling** - For any form with fields in plan, all fields should be located and filled
    - **Validates: Requirements FR-02.3, FR-02.4, FR-02.5**
  
  - [ ] 7.7 Implement CAPTCHA detection and user assistance flow
    - Detect CAPTCHA presence using common selectors
    - Pause execution and request user input via WebSocket
    - Resume execution after receiving CAPTCHA solution
    - _Requirements: FR-02.6_
  
  - [ ] 7.8 Implement retry logic with exponential backoff
    - Add retry decorator for transient failures
    - Implement exponential backoff (1s, 2s, 4s, 8s)
    - Log retry attempts for monitoring
    - _Requirements: FR-07.10_
  
  - [ ]* 7.9 Write property test for exponential backoff retry
    - **Property 41: Exponential Backoff Retry** - For any transient failure, retries should occur with exponentially increasing delays
    - **Validates: Requirements FR-07.10**

- [ ] 8. Implement Security Layer - Kavach Protocol
  - [ ] 8.1 Set up AWS WAF with OWASP Top 10 rules
    - Configure WAF WebACL with managed rule groups
    - Add rate limiting and geo-blocking rules
    - Attach WAF to API Gateway and CloudFront
    - _Requirements: FR-03.11_
  
  - [ ] 8.2 Integrate Moondream vision model for phishing detection
    - Deploy Moondream model on Lambda or EC2
    - Implement screenshot analysis pipeline
    - Define phishing indicator detection rules
    - _Requirements: FR-03.2_
  
  - [ ]* 8.3 Write property test for visual security validation
    - **Property 11: Visual Security Validation** - For any page load, Moondream should analyze for phishing before allowing interaction
    - **Validates: Requirements FR-03.2**
  
  - [ ] 8.4 Implement secure credential management with AWS KMS
    - Create KMS key for credential encryption
    - Implement in-memory credential storage with encryption
    - Add automatic credential destruction on session end
    - _Requirements: FR-03.5, FR-03.7_
  
  - [ ]* 8.5 Write property test for ephemeral credential storage
    - **Property 12: Ephemeral Credential Storage** - For any credentials, they should be encrypted in memory and destroyed within 60s of session end
    - **Validates: Requirements FR-03.5, FR-03.8, FR-03.9**
  
  - [ ] 8.6 Implement session cleanup and data destruction
    - Create cleanup service that destroys browser, credentials, and session data
    - Implement TTL-based automatic cleanup
    - Add manual cleanup trigger for explicit session termination
    - _Requirements: FR-03.8, FR-09.6, FR-09.8_
  
  - [ ]* 8.7 Write property test for session cleanup completeness
    - **Property 15: Session Cleanup Completeness** - For any terminated session, all data should be destroyed within 60 seconds
    - **Validates: Requirements FR-03.8, FR-09.6, FR-09.8**

- [ ] 9. Build Text-to-Speech system with Amazon Polly
  - [ ] 9.1 Implement TTS synthesis with Polly Neural voices
    - Configure Polly with regional language voices
    - Implement text-to-speech conversion
    - Upload synthesized audio to S3
    - Return CloudFront URLs for fast delivery
    - _Requirements: FR-01.6, FR-01.10_
  
  - [ ] 9.2 Create response templates for different message types
    - Define templates for confirmation, question, warning, error, success
    - Implement template rendering with parameter substitution
    - Support all 10 Indian languages
    - _Requirements: FR-01.6, FR-04_
  
  - [ ]* 9.3 Write property test for language-consistent responses
    - **Property 4: Language-Consistent Responses** - For any intent in language L, all TTS responses should be in language L
    - **Validates: Requirements FR-01.6**
  
  - [ ] 9.4 Implement audio streaming for long responses
    - Break long text into sentence chunks
    - Stream audio chunks to client as they're generated
    - Implement adaptive bitrate based on network conditions
    - _Requirements: FR-05.8_
  
  - [ ]* 9.5 Write property test for adaptive audio streaming
    - **Property 27: Adaptive Audio Streaming** - For any TTS response, bitrate should adapt to network conditions
    - **Validates: Requirements FR-05.8**

- [ ] 10. Implement Session Management system
  - [ ] 10.1 Create session creation and lifecycle management
    - Generate unique session IDs
    - Store session state in DynamoDB with TTL
    - Implement session locking for concurrent access
    - _Requirements: FR-09.1, FR-09.2, FR-09.10_
  
  - [ ]* 10.2 Write property test for unique session creation
    - **Property 28: Unique Session Creation** - For any task initiation, a globally unique session_id should be created
    - **Validates: Requirements FR-09.1**
  
  - [ ] 10.3 Implement session resumption logic
    - Retrieve session state from DynamoDB
    - Validate session is within TTL
    - Resume execution from last completed step
    - _Requirements: FR-09.3_
  
  - [ ]* 10.4 Write property test for session resumption
    - **Property 30: Session Resumption** - For any interrupted session within TTL, resumption should work from last completed step
    - **Validates: Requirements FR-09.3**
  
  - [ ] 10.5 Implement concurrent session isolation
    - Add session locking with DynamoDB conditional writes
    - Ensure modifications to one session don't affect others
    - _Requirements: FR-09.7, FR-09.10_
  
  - [ ]* 10.6 Write property test for concurrent session isolation
    - **Property 31: Concurrent Session Isolation** - For any two concurrent sessions, modifications should not affect each other
    - **Validates: Requirements FR-09.7, FR-09.10**

- [ ] 11. Build Guided Decision Support features
  - [ ] 11.1 Implement form field explanation generation
    - Extract field labels and context from page
    - Generate simple-language explanations using LLM
    - Synthesize explanations via TTS
    - _Requirements: FR-04.1_
  
  - [ ]* 11.2 Write property test for field explanation
    - **Property 19: Field Explanation** - For any form field, a simple-language explanation should be generated
    - **Validates: Requirements FR-04.1**
  
  - [ ] 11.3 Implement input validation and warning system
    - Validate user inputs against expected formats
    - Generate correction suggestions for invalid inputs
    - Warn user before proceeding with questionable inputs
    - _Requirements: FR-04.2_
  
  - [ ]* 11.4 Write property test for input validation warnings
    - **Property 20: Input Validation Warnings** - For any invalid input, warning and correction suggestions should be provided
    - **Validates: Requirements FR-04.2**
  
  - [ ] 11.5 Implement confirmation flow for critical actions
    - Detect financial transactions and irreversible actions
    - Generate clear confirmation messages with details
    - Wait for explicit user approval before proceeding
    - _Requirements: FR-02.8, FR-04.4, FR-04.5_
  
  - [ ]* 11.6 Write property test for user confirmation on critical actions
    - **Property 10: User Confirmation for Critical Actions** - For any financial or irreversible action, explicit confirmation should be required
    - **Validates: Requirements FR-02.8, FR-04.4, FR-04.5**
  
  - [ ] 11.7 Implement task completion summary generation
    - Extract key details from confirmation pages (PNR, confirmation codes)
    - Generate comprehensive summary of what was accomplished
    - Speak summary to user via TTS
    - _Requirements: FR-04.7_
  
  - [ ]* 11.8 Write property test for task completion summary
    - **Property 22: Task Completion Summary** - For any completed task, a summary should be generated and spoken
    - **Validates: Requirements FR-04.7**

- [ ] 12. Checkpoint - Verify backend services integration
  - Test complete execution flow with all components
  - Ensure all tests pass, ask the user if questions arise

- [ ] 13. Build Client PWA (Progressive Web App)
  - [ ] 13.1 Set up Next.js 14 project with App Router
    - Initialize Next.js project with TypeScript
    - Configure Tailwind CSS and Shadcn/UI
    - Set up PWA configuration with next-pwa
    - Optimize bundle size to stay under 10MB
    - _Requirements: FR-05.1_
  
  - [ ] 13.2 Implement voice input UI with MediaRecorder API
    - Create large "Press to Speak" button with visual feedback
    - Implement audio recording with waveform visualization
    - Add language selector component
    - Implement offline audio caching with Service Worker
    - _Requirements: FR-01, FR-05.4_
  
  - [ ] 13.3 Implement WebSocket connection for real-time updates
    - Connect to backend WebSocket endpoint
    - Handle progress updates, user input requests, and errors
    - Implement reconnection logic for network interruptions
    - _Requirements: FR-02.10_
  
  - [ ]* 13.4 Write property test for offline voice recording
    - **Property 26: Offline Voice Recording** - For any voice input when offline, audio should be cached and synced when online
    - **Validates: Requirements FR-05.9**
  
  - [ ] 13.5 Implement audio playback with Web Audio API
    - Create audio player component for TTS responses
    - Implement streaming playback for chunked audio
    - Add playback controls (pause, resume, speed)
    - _Requirements: FR-01.6_
  
  - [ ] 13.6 Create task progress and confirmation screens
    - Build progress screen with step indicators
    - Create confirmation screen with large text and voice+touch controls
    - Implement accessibility features (high contrast, large fonts)
    - _Requirements: FR-05.10_
  
  - [ ]* 13.7 Write property test for zero-read zero-type interface
    - **Property 25: Zero-Read Zero-Type Interface** - For any core interaction, it should be completable via voice only
    - **Validates: Requirements FR-05.5, FR-05.6, FR-05.11**

- [ ] 14. Implement API Gateway and Lambda functions
  - [ ] 14.1 Create REST API endpoints
    - POST /api/sessions - Create new session
    - POST /api/voice-input - Submit voice input
    - GET /api/transcription/{job_id} - Get transcription result
    - POST /api/confirm-intent - Confirm intent and start execution
    - GET /api/session/{session_id}/status - Get session status
    - DELETE /api/session/{session_id} - Cancel and destroy session
    - _Requirements: API Design section_
  
  - [ ] 14.2 Implement WebSocket endpoint for real-time communication
    - WS /api/ws/session/{session_id} - Real-time updates
    - Handle client messages: user_input, confirmation, cancel
    - Send server messages: progress_update, user_input_required, security_warning, task_complete, error
    - _Requirements: API Design section_
  
  - [ ] 14.3 Add authentication and rate limiting
    - Implement session token validation
    - Add rate limiting (10 requests per minute per user)
    - Configure CORS for PWA domain
    - _Requirements: NFR-03_
  
  - [ ]* 14.4 Write integration tests for all API endpoints
    - Test each endpoint with valid and invalid inputs
    - Test error handling and edge cases
    - Test rate limiting behavior

- [ ] 15. Implement Audit Logging and Compliance
  - [ ] 15.1 Create CloudWatch logging infrastructure
    - Set up log groups for each component
    - Implement structured logging with correlation IDs
    - Configure log retention (90 days)
    - _Requirements: FR-10.1, FR-10.5_
  
  - [ ] 15.2 Implement comprehensive interaction logging
    - Log all user interactions with timestamps and session IDs
    - Log actions performed and outcomes
    - Ensure no PII is included in logs
    - _Requirements: FR-10.1, FR-10.2, FR-10.3_
  
  - [ ]* 15.3 Write property test for PII-free logging
    - **Property 14: PII-Free Logging** - For any log entry, it should not contain PII, credentials, or sensitive data
    - **Validates: Requirements FR-03.12, FR-10.3**
  
  - [ ] 15.4 Implement security event logging
    - Log phishing detections, suspicious patterns, WAF blocks
    - Add severity levels (low, medium, high, critical)
    - Set up CloudWatch alarms for critical events
    - _Requirements: FR-10.4_
  
  - [ ]* 15.5 Write property test for security event logging
    - **Property 35: Security Event Logging** - For any security event, it should be logged with severity level
    - **Validates: Requirements FR-10.4**

- [ ] 16. Set up monitoring and observability
  - [ ] 16.1 Configure CloudWatch dashboards
    - Create dashboards for key metrics (latency, error rate, task completion)
    - Add widgets for cost tracking
    - Set up real-time monitoring views
    - _Requirements: NFR-06_
  
  - [ ] 16.2 Implement distributed tracing with X-Ray
    - Enable X-Ray tracing for Lambda functions
    - Add tracing to Playwright execution
    - Create service map visualization
    - _Requirements: NFR-06_
  
  - [ ] 16.3 Set up alerting and notifications
    - Create SNS topics for alerts
    - Configure alarms for error rate > 5%, latency > 3s
    - Set up PagerDuty integration for critical alerts
    - _Requirements: NFR-02_

- [ ] 17. Implement Infrastructure as Code
  - [ ] 17.1 Create Terraform/CloudFormation templates
    - Define VPC, subnets, security groups
    - Create DynamoDB tables with proper configuration
    - Set up S3 buckets with lifecycle policies
    - Configure CloudFront distribution
    - Define IAM roles and policies
    - _Requirements: NFR-06_
  
  - [ ] 17.2 Set up deployment pipeline
    - Configure GitHub Actions for CI/CD
    - Implement blue-green deployment for Lambda
    - Set up rolling updates for EC2 Auto Scaling
    - Add automated rollback on high error rates
    - _Requirements: Deployment Pipeline section_

- [ ] 18. Add support for additional services and languages
  - [ ] 18.1 Create service templates for DigiLocker, SBI, UIDAI, Electricity
    - Define selectors and page flows for each service
    - Test execution flows for each service
    - _Requirements: FR-02.9, FR-08.1_
  
  - [ ] 18.2 Add support for remaining 9 Indian languages
    - Configure Transcribe for all languages
    - Add Polly voices for all languages
    - Create TTS templates in all languages
    - Test end-to-end flows in each language
    - _Requirements: FR-01.1, FR-01.10_

- [ ] 19. Performance optimization and cost reduction
  - [ ] 19.1 Implement caching strategies
    - Cache service templates in memory
    - Cache common TTS responses
    - Configure CloudFront caching for static assets
    - _Requirements: NFR-04_
  
  - [ ] 19.2 Optimize model selection for cost
    - Fine-tune complexity scoring algorithm
    - Maximize use of Llama-3 8B for simple tasks
    - Minimize Claude 3 Sonnet usage (only for error recovery)
    - _Requirements: NFR-04_
  
  - [ ] 19.3 Implement Spot instance handling
    - Add graceful handling of Spot interruptions
    - Implement task checkpointing for resumption
    - Configure fallback to on-demand instances
    - _Requirements: NFR-04_

- [ ] 20. Final integration testing and user acceptance
  - [ ] 20.1 Conduct end-to-end testing with all services
    - Test complete flows for all 5 services
    - Test in all 10 languages
    - Test on low-end Android devices
    - Test on 2G/3G networks
    - _Requirements: All FR requirements_
  
  - [ ] 20.2 Perform security audit and penetration testing
    - Run OWASP ZAP scans
    - Conduct manual penetration testing
    - Verify DPDP Act 2023 compliance
    - Test phishing detection accuracy
    - _Requirements: NFR-05_
  
  - [ ] 20.3 Conduct user acceptance testing with target users
    - Test with rural citizens, senior citizens, first-time users
    - Gather feedback on voice interaction quality
    - Measure task completion rates
    - Identify usability issues
    - _Requirements: User Stories_

- [ ] 21. Final checkpoint - Production readiness
  - Verify all tests pass (unit, property, integration)
  - Confirm cost per task is under ₹1.00
  - Validate performance meets SLAs (latency < 3s, availability > 99.5%)
  - Ensure all documentation is complete
  - Ask the user if ready for production deployment

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- The phased approach allows for early feedback and course correction
- Local R&D with Ollama minimizes cloud costs during development
