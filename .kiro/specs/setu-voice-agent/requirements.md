# Requirements Document: Setu - Voice-First Autonomous Web Agent

## Introduction

### Purpose

Setu is a Voice-First Autonomous Web Agent designed to democratize digital access for hundreds of millions of Indian citizens who face barriers in accessing Digital India services. The system enables users to complete complex web-based tasks through natural voice commands in their regional language, eliminating the need for reading, typing, or navigating complex user interfaces.

### Problem Statement

India's digital transformation has created a significant accessibility gap. While government services have moved online, millions of citizens cannot access them due to:

- Low literacy rates and unfamiliarity with English-based interfaces
- Lack of smartphone navigation skills among first-generation internet users
- Complex multi-step processes on government websites
- Language barriers with most services available only in English/Hindi
- Physical limitations preventing elderly citizens from using small touchscreens

### Goals

1. Enable voice-based access to critical Digital India services for underserved populations
2. Provide autonomous task execution that eliminates manual navigation requirements
3. Support 10+ Indian languages including dialect variations and code-mixed speech
4. Ensure security through Remote Browser Isolation and visual phishing detection
5. Deliver a lightweight solution (<10MB PWA) that works on low-end devices and slow networks
6. Maintain task completion cost under ₹1 per transaction for sustainability

## Glossary

- **Setu**: The voice-first autonomous web agent system (Hindi: "bridge")
- **Kavach_Protocol**: Security framework using Remote Browser Isolation (Hindi: "shield")
- **Client_PWA**: Progressive Web App running on user's device
- **Intelligence_Layer**: AWS-based AI services for speech, planning, and decision-making
- **Execution_Layer**: Playwright-based browser automation infrastructure
- **Intent_Gatekeeper**: Llama-3 8B model that validates and confirms user intent
- **Planning_Engine**: Claude 3 Sonnet/Llama-3 70B that generates action plans
- **Moondream**: Vision model for visual security validation
- **RBI**: Remote Browser Isolation - security technique where browsing happens remotely

## Stakeholders

| Stakeholder | Role | Responsibilities |
|-------------|------|------------------|
| Rural Citizens | Primary End Users | Use voice commands to access government services |
| Senior Citizens (60+) | Primary End Users | Complete banking and document tasks via voice |
| First-Generation Smartphone Users | Primary End Users | Access digital services without navigation skills |
| Government Service Providers | Service Owners | Provide APIs and web interfaces (IRCTC, UIDAI, etc.) |
| AWS Infrastructure Team | Platform Provider | Maintain cloud infrastructure and AI services |
| Development Team | System Builders | Build, test, and deploy Setu components |
| Security Auditors | Compliance Validators | Ensure DPDP Act 2023 compliance and security |
| NGO Partners | Distribution Channels | Deploy Setu in rural communities and train users |
| Hackathon Judges | Evaluators | Assess social impact and technical innovation |

## Functional Requirements

### FR-01: Voice Input & Multi-Language Processing

**User Story:** As a rural citizen who speaks only Gujarati, I want to give voice commands in my native language with dialect variations, so that I can access government services without learning English or Hindi.

#### Acceptance Criteria

1. WHEN a user speaks in any of 10+ supported Indian languages (Hindi, Gujarati, Tamil, Telugu, Bengali, Marathi, Kannada, Malayalam, Punjabi, Odia), THE Audio_Pipeline SHALL transcribe the speech to text
2. WHEN a user speaks with code-mixed language (Hinglish, Tanglish), THE Audio_Pipeline SHALL correctly interpret the mixed-language input
3. WHEN a user speaks with regional dialect variations, THE Audio_Pipeline SHALL normalize the dialect to standard language form
4. WHEN transcription is complete, THE Intent_Gatekeeper SHALL extract the user's intended action and target service
5. WHEN intent is ambiguous, THE System SHALL ask clarifying questions via voice in the user's language
6. WHEN intent is confirmed, THE System SHALL acknowledge the task in the user's language using Text-to-Speech
7. THE Audio_Pipeline SHALL use AWS Transcribe with language-specific models for transcription
8. THE System SHALL support continuous listening mode with wake-word activation
9. WHEN background noise exceeds threshold, THE System SHALL request the user to repeat their command
10. THE Text-to-Speech SHALL use Amazon Polly Neural voices with regional language support


### FR-02: Autonomous Web Execution

**User Story:** As a senior citizen who cannot navigate complex government websites, I want the AI agent to physically control the browser and complete my task, so that I don't have to read forms or click buttons myself.

#### Acceptance Criteria

1. WHEN a task plan is generated, THE Execution_Layer SHALL launch a Playwright browser instance in the remote environment
2. WHEN navigating to a service website, THE Playwright_Engine SHALL load the target URL and wait for page readiness
3. WHEN a login form is encountered, THE Playwright_Engine SHALL locate username and password fields and input credentials provided by the user
4. WHEN a multi-step form is encountered, THE Playwright_Engine SHALL fill each field according to the action plan
5. WHEN a dropdown or selection is required, THE Playwright_Engine SHALL identify options and select the correct value
6. WHEN a CAPTCHA is encountered, THE System SHALL pause execution and request user assistance via voice
7. WHEN a confirmation page is displayed, THE System SHALL read the confirmation details to the user via voice
8. WHEN user confirmation is required before submission, THE System SHALL wait for explicit voice approval
9. THE Execution_Layer SHALL support at least 5 government services: IRCTC, DigiLocker, SBI NetBanking, UIDAI, and electricity bill payment portals
10. WHEN execution is in progress, THE System SHALL provide live audio updates of each step being performed
11. WHEN an unexpected error occurs during execution, THE Planning_Engine SHALL replan and retry the task
12. THE System SHALL capture screenshots at each major step for audit trail purposes


### FR-03: Security - Kavach Protocol

**User Story:** As a user concerned about online fraud, I want the system to protect me from phishing websites and credential theft, so that my sensitive information remains secure.

#### Acceptance Criteria

1. THE Kavach_Protocol SHALL implement Remote Browser Isolation where all web browsing occurs on AWS infrastructure, not the user's device
2. WHEN a website is loaded, THE Moondream vision model SHALL analyze the page visually for phishing indicators
3. WHEN a phishing attempt is detected, THE System SHALL immediately terminate the session and warn the user via voice
4. WHEN dark patterns are detected (hidden fees, misleading buttons), THE System SHALL alert the user before proceeding
5. WHEN credentials are provided by the user, THE System SHALL store them only in ephemeral session memory with automatic destruction after task completion
6. WHEN a voice command requests credential storage, THE System SHALL refuse and explain the security risk
7. THE System SHALL encrypt all data in transit using TLS 1.3
8. WHEN a session ends, THE Execution_Layer SHALL destroy the browser instance and clear all session data within 60 seconds
9. THE System SHALL never transmit or store Personally Identifiable Information (PII) beyond the active session
10. WHEN suspicious voice patterns are detected (voice cloning, coercion indicators), THE System SHALL pause and request additional verification
11. THE System SHALL implement AWS WAF rules to protect against common web attacks
12. THE System SHALL log all security events to CloudWatch for audit purposes without storing PII


### FR-04: Guided Decision Support

**User Story:** As a first-generation internet user, I want the AI to explain what each form field means and warn me about mistakes, so that I can make informed decisions without prior knowledge.

#### Acceptance Criteria

1. WHEN a form field is encountered, THE System SHALL explain the field's purpose in simple language via voice
2. WHEN a user provides input that appears incorrect (e.g., invalid date format), THE System SHALL warn the user and suggest corrections
3. WHEN multiple options are available, THE System SHALL explain the implications of each choice
4. WHEN a financial transaction is about to occur, THE System SHALL clearly state the amount and ask for explicit confirmation
5. WHEN a user is about to make a potentially irreversible action, THE System SHALL provide a warning and request confirmation
6. THE System SHALL proactively suggest optimal choices based on common user patterns (e.g., "Most users select Tatkal for urgent bookings")
7. WHEN a task is complete, THE System SHALL provide a voice summary of what was accomplished
8. WHEN an error occurs, THE System SHALL explain the error in non-technical language and suggest next steps
9. THE System SHALL maintain conversation context to avoid asking redundant questions
10. WHEN a user asks "why" during any step, THE System SHALL explain the reasoning behind the current action


### FR-05: Accessibility & Reach

**User Story:** As a user with a low-end Android phone and slow 2G internet in a rural area, I want to use Setu without downloading large apps or requiring fast internet, so that I can access services despite infrastructure limitations.

#### Acceptance Criteria

1. THE Client_PWA SHALL have a total size of less than 10MB including all assets
2. THE Client_PWA SHALL function on Android 9+ devices with minimum 2GB RAM
3. THE Client_PWA SHALL work on 2G/3G networks with graceful degradation
4. THE Client_PWA SHALL cache essential assets for offline voice input recording
5. THE System SHALL require zero reading ability from the user (fully voice-driven)
6. THE System SHALL require zero typing ability from the user (all input via voice)
7. THE Client_PWA SHALL support installation as a home screen app without Google Play Store
8. THE Client_PWA SHALL use adaptive bitrate for audio streaming based on network conditions
9. WHEN network connectivity is lost, THE System SHALL queue voice inputs and sync when connection is restored
10. THE Client_PWA SHALL provide visual feedback with large, high-contrast UI elements for users with visual impairments
11. THE System SHALL support voice commands for all navigation (no touch required for core functionality)
12. THE Client_PWA SHALL replace the need for 50+ individual service apps through unified voice interface

### FR-06: Intent Extraction and Validation

**User Story:** As a user who may not articulate my needs clearly, I want the system to understand my intent and confirm it with me, so that the correct task is executed.

#### Acceptance Criteria

1. WHEN voice input is transcribed, THE Intent_Gatekeeper SHALL parse the text to identify the target service and desired action
2. THE Intent_Gatekeeper SHALL use Llama-3 8B model for fast intent classification
3. WHEN intent confidence is below 80%, THE System SHALL ask clarifying questions
4. WHEN multiple intents are detected, THE System SHALL ask the user to choose one
5. THE Intent_Gatekeeper SHALL extract required parameters (dates, amounts, names) from the voice input
6. WHEN required parameters are missing, THE System SHALL ask for them specifically
7. THE System SHALL confirm the complete intent with the user before proceeding to planning
8. THE Intent_Gatekeeper SHALL detect and reject malicious intents (e.g., "transfer all my money")
9. WHEN a user changes their mind mid-task, THE System SHALL allow task cancellation via voice command
10. THE Intent_Gatekeeper SHALL maintain a history of recent intents for context-aware processing


### FR-07: Planning and Execution Engine

**User Story:** As a user who wants to book a train ticket, I want the system to automatically plan all the steps needed and execute them, so that I don't have to know how to navigate IRCTC website.

#### Acceptance Criteria

1. WHEN intent is confirmed, THE Planning_Engine SHALL generate a step-by-step action plan for task completion
2. THE Planning_Engine SHALL use Claude 3 Sonnet or Llama-3 70B via AWS Bedrock for complex reasoning
3. THE Planning_Engine SHALL output a structured JSON action plan with sequential steps
4. WHEN a step fails during execution, THE Planning_Engine SHALL replan the remaining steps
5. THE Planning_Engine SHALL maintain stateful context across replanning iterations
6. WHEN a website structure changes, THE Planning_Engine SHALL adapt the plan dynamically
7. THE Execution_Layer SHALL execute each step in the action plan using Playwright browser automation
8. THE Execution_Layer SHALL run on AWS EC2 Spot instances for cost optimization
9. WHEN a step requires user input (CAPTCHA, OTP), THE System SHALL pause and request it via voice
10. THE Execution_Layer SHALL implement retry logic with exponential backoff for transient failures
11. THE System SHALL support parallel execution of independent steps when possible
12. WHEN execution is complete, THE System SHALL verify task success by checking confirmation indicators on the webpage

### FR-08: Service Template Management

**User Story:** As a system administrator, I want to maintain templates for each supported government service, so that the planning engine has structured knowledge of how to interact with each website.

#### Acceptance Criteria

1. THE System SHALL maintain service templates for IRCTC, DigiLocker, SBI NetBanking, UIDAI, and electricity bill payment portals
2. WHEN a new service is added, THE System SHALL allow template creation with service metadata (URL, authentication method, form structure)
3. THE Service_Template SHALL include CSS selectors for common elements (login fields, submit buttons, form inputs)
4. THE Service_Template SHALL include expected page flows and navigation paths
5. THE Service_Template SHALL include error indicators and success confirmation patterns
6. THE Planning_Engine SHALL use service templates to generate more accurate action plans
7. WHEN a template becomes outdated, THE System SHALL log template mismatch events for manual review
8. THE Service_Template SHALL be stored in DynamoDB for fast retrieval
9. THE System SHALL support template versioning for rollback capability
10. THE Service_Template SHALL include language-specific field labels for multi-language support


### FR-09: Session Management and State Persistence

**User Story:** As a user whose task takes multiple steps over time, I want the system to remember my progress, so that I can resume if the session is interrupted.

#### Acceptance Criteria

1. WHEN a user starts a task, THE System SHALL create a unique session with a session ID
2. THE System SHALL store session state in DynamoDB with TTL of 30 minutes
3. WHEN a session is interrupted, THE System SHALL allow resumption using the session ID
4. THE Session_State SHALL include current step, completed steps, and pending steps
5. THE Session_State SHALL include user preferences (language, voice speed)
6. WHEN a session expires, THE System SHALL automatically destroy all session data
7. THE System SHALL support concurrent sessions for different users
8. WHEN a user explicitly ends a session, THE System SHALL immediately destroy session data
9. THE Session_State SHALL never include credentials or PII beyond the active session
10. THE System SHALL implement session locking to prevent concurrent modifications

### FR-10: Audit Logging and Compliance

**User Story:** As a compliance officer, I want comprehensive audit logs of all system actions, so that we can demonstrate DPDP Act 2023 compliance and investigate issues.

#### Acceptance Criteria

1. THE System SHALL log all user interactions to CloudWatch Logs
2. THE Audit_Log SHALL include timestamps, session IDs, actions performed, and outcomes
3. THE Audit_Log SHALL never include PII, credentials, or sensitive user data
4. WHEN a security event occurs, THE System SHALL log it with severity level
5. THE Audit_Log SHALL be retained for 90 days for compliance purposes
6. THE System SHALL implement log aggregation for analytics and monitoring
7. WHEN a task fails, THE Audit_Log SHALL include error details and stack traces
8. THE System SHALL provide audit log export capability for compliance reviews
9. THE Audit_Log SHALL be encrypted at rest using AWS KMS
10. THE System SHALL implement log access controls to restrict viewing to authorized personnel


## Non-Functional Requirements

### NFR-01: Performance and Latency

**User Story:** As a user on a slow network, I want the system to respond quickly to my voice commands, so that I don't have to wait long for each interaction.

#### Acceptance Criteria

1. THE System SHALL respond to voice input within 3 seconds for intent confirmation
2. THE Audio_Pipeline SHALL complete transcription within 2 seconds for 10-second audio clips
3. THE Planning_Engine SHALL generate action plans within 5 seconds for standard tasks
4. THE Execution_Layer SHALL complete simple form fills within 10 seconds
5. THE Text-to-Speech SHALL begin playback within 1 second of text generation
6. THE Client_PWA SHALL load initial interface within 2 seconds on 3G networks
7. THE System SHALL maintain end-to-end task completion time under 2 minutes for standard government service tasks
8. THE System SHALL implement caching for frequently accessed service templates to reduce latency

### NFR-02: Availability and Reliability

**User Story:** As a user who depends on Setu for critical tasks, I want the system to be available when I need it, so that I can complete time-sensitive transactions.

#### Acceptance Criteria

1. THE System SHALL maintain 99.5% uptime during business hours (9 AM - 9 PM IST)
2. THE System SHALL implement health checks for all critical components
3. WHEN a component fails, THE System SHALL automatically failover to backup instances
4. THE System SHALL implement circuit breakers to prevent cascade failures
5. THE System SHALL provide graceful degradation when non-critical services are unavailable
6. THE System SHALL implement automatic retry with exponential backoff for transient failures
7. THE System SHALL monitor and alert on error rates exceeding 5%
8. THE Infrastructure SHALL use AWS Auto Scaling to handle traffic spikes

### NFR-03: Scalability

**User Story:** As the system grows to serve millions of users, I want it to handle increased load without performance degradation, so that all users receive consistent service quality.

#### Acceptance Criteria

1. THE System SHALL support 10,000 concurrent users during peak hours
2. THE Execution_Layer SHALL scale horizontally using EC2 Auto Scaling Groups
3. THE System SHALL implement request queuing when capacity is reached
4. THE Database SHALL use DynamoDB with on-demand capacity mode for automatic scaling
5. THE System SHALL implement rate limiting per user to prevent abuse (10 requests per minute)
6. THE Audio_Pipeline SHALL use AWS Transcribe streaming for parallel processing
7. THE System SHALL implement connection pooling for database and API connections
8. THE Infrastructure SHALL support geographic distribution for future multi-region deployment


### NFR-04: Cost Efficiency

**User Story:** As a project stakeholder, I want to keep operational costs low, so that the service remains sustainable and affordable for underserved populations.

#### Acceptance Criteria

1. THE System SHALL maintain cost per task completion under ₹1.00 (approximately $0.012 USD)
2. THE Execution_Layer SHALL use EC2 Spot instances to reduce compute costs by 70%
3. THE System SHALL implement intelligent model selection (Llama-3 8B for simple tasks, 70B for complex)
4. THE System SHALL use CloudFront CDN for static asset delivery to reduce bandwidth costs
5. THE System SHALL implement audio compression to minimize Transcribe API costs
6. THE System SHALL use DynamoDB on-demand pricing to avoid over-provisioning
7. THE System SHALL implement session timeouts to prevent resource waste
8. THE Development_Team SHALL use Ollama for local R&D to minimize cloud costs during development

### NFR-05: Security and Privacy

**User Story:** As a user sharing sensitive information, I want my data to be protected and never stored permanently, so that my privacy is maintained.

#### Acceptance Criteria

1. THE System SHALL comply with India's Digital Personal Data Protection Act 2023
2. THE System SHALL encrypt all data in transit using TLS 1.3
3. THE System SHALL encrypt all data at rest using AWS KMS
4. THE System SHALL never store PII beyond the active session duration
5. THE System SHALL implement zero-knowledge architecture where possible
6. THE System SHALL destroy all session data within 60 seconds of session termination
7. THE System SHALL implement AWS WAF with OWASP Top 10 protection rules
8. THE System SHALL conduct regular security audits and penetration testing
9. THE System SHALL implement role-based access control (RBAC) for administrative functions
10. THE System SHALL provide users with data deletion requests capability (right to be forgotten)

### NFR-06: Maintainability and Observability

**User Story:** As a developer maintaining the system, I want comprehensive monitoring and logging, so that I can quickly diagnose and fix issues.

#### Acceptance Criteria

1. THE System SHALL implement distributed tracing using AWS X-Ray
2. THE System SHALL publish metrics to CloudWatch for all critical operations
3. THE System SHALL implement structured logging with correlation IDs
4. THE System SHALL provide dashboards for real-time system health monitoring
5. THE System SHALL implement alerting for critical errors and performance degradation
6. THE System SHALL maintain API documentation using OpenAPI specification
7. THE System SHALL implement automated testing with minimum 80% code coverage
8. THE System SHALL use Infrastructure as Code (Terraform or CloudFormation) for reproducible deployments


## User Stories

### Story 1: Ramesh - Rural Farmer Checking Aadhaar Status

**Persona:** Ramesh, 45, farmer from Gujarat, speaks only Gujarati, has basic smartphone but cannot read English

**Goal:** Check Aadhaar card status and download e-Aadhaar

**Journey:**
1. Opens Setu PWA and says "મારું આધાર કાર્ડ ડાઉનલોડ કરવું છે" (I want to download my Aadhaar card)
2. System confirms: "તમે UIDAI પરથી તમારું e-આધાર ડાઉનલોડ કરવા માંગો છો?" (You want to download your e-Aadhaar from UIDAI?)
3. Ramesh confirms: "હા" (Yes)
4. System asks for Aadhaar number via voice, Ramesh speaks the 12 digits
5. System navigates UIDAI website, fills form, handles CAPTCHA with Ramesh's help
6. System downloads e-Aadhaar and confirms: "તમારું e-આધાર ડાઉનલોડ થઈ ગયું છે" (Your e-Aadhaar has been downloaded)

**Requirements Validated:** FR-01, FR-02, FR-04, FR-05, FR-06, FR-07

### Story 2: Lakshmi - Senior Citizen Paying Electricity Bill

**Persona:** Lakshmi, 68, retired teacher from Tamil Nadu, has smartphone but struggles with small text and navigation

**Goal:** Pay monthly electricity bill online

**Journey:**
1. Opens Setu and says "மின்சாரம் பில் கட்டணம்" (Electricity bill payment)
2. System asks which electricity board, Lakshmi says "TANGEDCO"
3. System explains: "நான் TANGEDCO வலைதளத்திற்கு செல்கிறேன்" (I'm going to TANGEDCO website)
4. System asks for consumer number, Lakshmi provides it via voice
5. System retrieves bill amount and says: "உங்கள் பில் ₹1,240. இதை செலுத்த விரும்புகிறீர்களா?" (Your bill is ₹1,240. Do you want to pay this?)
6. Lakshmi confirms, provides payment details via voice
7. System completes payment and reads confirmation number aloud

**Requirements Validated:** FR-01, FR-02, FR-04, FR-05, FR-07, NFR-01

### Story 3: Arjun - First-Time Internet User Booking Train Ticket

**Persona:** Arjun, 28, daily wage worker from Bihar, first smartphone, speaks Hinglish, never used IRCTC

**Goal:** Book train ticket from Patna to Delhi for job interview

**Journey:**
1. Opens Setu and says "Bhai, mujhe Patna se Delhi train ticket book karna hai" (Brother, I need to book train ticket from Patna to Delhi)
2. System confirms intent and asks for travel date
3. Arjun says "Agle hafte Monday ko" (Next week Monday)
4. System calculates date and confirms: "16 December ko travel karna hai?" (Travel on 16th December?)
5. System explains: "IRCTC pe login karne ke liye aapka username aur password chahiye" (Need your username and password to login to IRCTC)
6. Arjun provides credentials via voice
7. System navigates IRCTC, searches trains, explains options: "Rajdhani Express sabse fast hai but thoda costly. Sampark Kranti affordable hai" (Rajdhani Express is fastest but costly. Sampark Kranti is affordable)
8. Arjun chooses Sampark Kranti
9. System fills passenger details, handles CAPTCHA, completes booking
10. System reads PNR number and confirms: "Aapka ticket book ho gaya. PNR number hai..." (Your ticket is booked. PNR number is...)

**Requirements Validated:** FR-01, FR-02, FR-04, FR-06, FR-07, FR-08, NFR-01


### Story 4: Priya - Working Professional Accessing DigiLocker

**Persona:** Priya, 32, works in Bangalore, comfortable with technology but prefers voice while multitasking

**Goal:** Retrieve driving license from DigiLocker while cooking dinner

**Journey:**
1. While cooking, says "Hey Setu, get my driving license from DigiLocker"
2. System confirms and asks for DigiLocker credentials
3. Priya provides username and password via voice
4. System navigates DigiLocker, locates driving license document
5. System asks: "Should I download the PDF or just show you the details?"
6. Priya says "Just tell me the license number and expiry date"
7. System reads the information aloud
8. Priya says "Download it too"
9. System downloads and confirms completion

**Requirements Validated:** FR-01, FR-02, FR-06, FR-07, FR-09, NFR-01

### Story 5: Rajesh - Detecting Phishing Attempt

**Persona:** Rajesh, 52, small business owner from Maharashtra, target of online fraud attempts

**Goal:** Pay business tax online

**Journey:**
1. Opens Setu and says "व्यवसाय कर भरायचा आहे" (Want to pay business tax)
2. System starts navigating to tax portal
3. Moondream detects suspicious visual elements on a fake tax website
4. System immediately stops and warns: "सावधान! ही वेबसाइट बनावट दिसते. मी तुमचे पैसे सुरक्षित ठेवण्यासाठी हे थांबवत आहे" (Warning! This website looks fake. I'm stopping this to keep your money safe)
5. System terminates session and suggests official government portal
6. Rajesh thanks the system and confirms to proceed with official portal
7. System completes task on verified government website

**Requirements Validated:** FR-03, FR-04, NFR-05

### Story 6: Meena - Low Connectivity Rural Area

**Persona:** Meena, 38, Anganwadi worker from Odisha, has 2G connectivity, low-end Android phone

**Goal:** Check scholarship status for her daughter

**Journey:**
1. Opens Setu PWA (loads quickly despite 2G)
2. Says in Odia "ମୋ ଝିଅର ସ୍କଲାରସିପ୍ ଷ୍ଟାଟସ୍ ଦେଖିବା" (Check my daughter's scholarship status)
3. Network drops during voice input, but PWA caches the audio
4. When connection returns, audio uploads and processing continues
5. System asks for scholarship application number
6. Meena provides it, system navigates scholarship portal
7. Despite slow network, system provides audio updates: "ପେଜ୍ ଲୋଡ୍ ହେଉଛି, ଦୟାକରି ଅପେକ୍ଷା କରନ୍ତୁ" (Page is loading, please wait)
8. System retrieves status and reads it aloud: "ଆପଣଙ୍କ ଝିଅର ସ୍କଲାରସିପ୍ ଅନୁମୋଦିତ ହୋଇଛି" (Your daughter's scholarship is approved)

**Requirements Validated:** FR-01, FR-05, FR-09, NFR-01, NFR-02, NFR-04


## Constraints and Assumptions

### Technical Constraints

1. **AWS Dependency**: System is built entirely on AWS infrastructure and cannot easily migrate to other cloud providers
2. **Browser Automation Limitations**: Some websites with advanced bot detection may block Playwright automation
3. **CAPTCHA Dependency**: System cannot automatically solve CAPTCHAs and requires user assistance
4. **Language Model Accuracy**: AI models may occasionally misinterpret intent or generate incorrect plans
5. **Network Requirements**: Minimum 2G connectivity required for basic functionality
6. **Device Requirements**: Android 9+ or iOS 13+ for PWA installation
7. **Audio Quality**: Background noise above 60dB may affect transcription accuracy
8. **Service Template Maintenance**: Website changes require manual template updates

### Business Constraints

1. **Cost Target**: Must maintain under ₹1 per task to ensure sustainability
2. **Compliance**: Must comply with DPDP Act 2023 and RBI guidelines for financial transactions
3. **Service Coverage**: v1 limited to 5 government services (IRCTC, DigiLocker, SBI, UIDAI, electricity)
4. **Language Support**: v1 supports 10 Indian languages, expansion requires additional investment
5. **Hackathon Timeline**: MVP must be demonstrable within hackathon timeframe
6. **No Credential Storage**: Cannot store user credentials due to security policy
7. **Session Duration**: Maximum 30-minute session duration to prevent resource exhaustion

### Assumptions

1. **User Device**: Users have access to a smartphone with microphone and speaker
2. **Internet Access**: Users have at least intermittent internet connectivity
3. **Service Availability**: Government websites are accessible and functional
4. **User Cooperation**: Users will provide accurate information when prompted
5. **Language Proficiency**: Users can speak at least one of the supported languages
6. **AWS Service Availability**: AWS services maintain advertised SLAs
7. **Model Performance**: AI models maintain current accuracy levels
8. **Legal Compliance**: Automated form filling is legally permitted for government services
9. **User Trust**: Users trust the system with sensitive information after security explanation
10. **NGO Partnership**: NGO partners will assist with user onboarding and training

## Out of Scope (v1)

The following features are explicitly out of scope for the initial version:

### Features Not Included

1. **Private Sector Services**: Banking beyond SBI, e-commerce, private bill payments
2. **Financial Transactions**: Direct money transfers, investments, loan applications
3. **Document Upload**: Uploading user documents (photos, PDFs) to government portals
4. **Multi-User Sessions**: Family accounts or shared access
5. **Offline Mode**: Complete offline functionality without any internet
6. **Video Calls**: Visual verification or video KYC processes
7. **Handwriting Recognition**: Processing handwritten documents
8. **Advanced Analytics**: User behavior analytics or personalization
9. **Third-Party Integrations**: Integration with non-government services
10. **Mobile App**: Native iOS/Android apps (PWA only for v1)
11. **Multi-Device Sync**: Syncing sessions across multiple devices
12. **Voice Biometrics**: Voice-based authentication or identity verification
13. **Proactive Notifications**: Reminders for bill payments or document renewals
14. **Service Recommendations**: AI-suggested services based on user profile
15. **Community Features**: User forums, feedback sharing, or social features

### Technical Limitations

1. **Real-Time Collaboration**: Multiple users working on the same task simultaneously
2. **Advanced Error Recovery**: Automatic recovery from all website changes without template updates
3. **Universal Website Support**: Support for any website beyond the 5 specified services
4. **Custom Workflows**: User-defined automation workflows
5. **API-First Approach**: Direct API integration with government services (using web scraping instead)
6. **Multi-Region Deployment**: Deployment outside AWS Mumbai region
7. **White-Label Solution**: Customizable branding for partner organizations
8. **Advanced Security**: Biometric authentication, hardware security keys
