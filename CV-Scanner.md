# CV Screening Agent

> An open-source, AI-powered CV screening platform with multi-provider support and customizable evaluation templates.

---

## The Architectural Plan

### 1. Unified Storage: PostgreSQL + `pgvector`

Instead of having two separate databases, you will use **PostgreSQL** as your single source of truth.

- **Relational Side:** Stores user profiles (linked via Gmail OAuth), account settings, API keys (encrypted), evaluation templates, and metadata about uploaded CVs (filename, upload date, owner ID).
- **Vector Side (`pgvector`):** Stores the "Embeddings" of the CVs. This allows the AI to "mathematically" compare one resume to another or to a job description.
- **Usage:** When a user logs in via Gmail, your FastAPI backend checks the Relational tables. When they ask "Who are my top 5 candidates?", the backend queries the Vector columns.

### 2. Multi-Provider AI System (BYOK - Bring Your Own Key)

Users provide their own API keys for AI providers. This makes the platform **open-source friendly** and eliminates the risk of exposing shared API keys.

#### Supported Providers

| Provider | Use Cases | Models |
|----------|-----------|--------|
| **Anthropic Claude** | Complex reasoning, CV evaluation | claude-sonnet-4-20250514, claude-3-5-haiku |
| **OpenAI GPT** | General purpose, embeddings | gpt-4o, gpt-4o-mini, text-embedding-3-small |
| **Google Gemini** | Fast parsing, cost-effective | gemini-2.0-flash, gemini-2.0-pro |
| **Groq** | Ultra-fast inference | llama-3.3-70b, mixtral-8x7b |
| **Ollama** | Local/private models | llama3, mistral, codellama |

#### Hybrid API Key Architecture

```
User Settings:
├── api_keys:                    # One key per provider (encrypted)
│   ├── claude: "sk-ant-..."
│   ├── openai: "sk-..."
│   ├── gemini: "AIza..."
│   ├── groq: "gsk_..."
│   └── ollama: "http://localhost:11434"
│
└── agent_config:                # Per-agent provider selection
    ├── parser_agent: { provider: "gemini", model: "gemini-2.0-flash" }
    ├── scorer_agent: { provider: "claude", model: "claude-sonnet-4-20250514" }
    ├── chat_agent: { provider: "openai", model: "gpt-4o" }
    └── embeddings: { provider: "openai", model: "text-embedding-3-small" }
```

**Benefits:**
- Users enter API keys once per provider
- Assign different providers/models to different agents
- Optimize for cost (cheaper models for parsing) vs. quality (better models for scoring)
- Privacy option with Ollama for fully local processing

### 3. Customizable Evaluation Templates

Users can create fully custom evaluation criteria or use system-provided templates.

#### Template Types

| Type | Description | Editable |
|------|-------------|----------|
| **System Templates** | Pre-built, shipped with app | No (read-only) |
| **User Templates** | Created by users | Yes (full control) |

#### System Template: "AI-First Fintech" ⭐ (Default)

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Education** | 15 | High School+, bootcamps, self-taught with portfolio |
| **Fintech Experience** | 20 | Finance, banking, crypto, DeFi, fintech startups |
| **Technical Skills** | 25 | TypeScript, Python, React, Node.js, FastAPI |
| **Soft Skills & Adaptability** | 20 | Fast learner, stress handling, teamwork |
| **AI-Native Development** | 20 | AI tools (Copilot, Cursor), RAG, MCP, agents |

**Pass/Fail Logic:** Score ≥ 60 AND 3+ criteria met (must include Technical Skills)

#### Custom Template Structure

```typescript
interface EvaluationTemplate {
  id: string;
  name: string;
  description: string;
  isSystemTemplate: boolean;
  userId: string | null;
  
  criteria: Criterion[];
  passingScore: number;          // default: 60
  minimumCriteriaMet: number;    // default: 3
  requiredCriteria: string[];    // e.g., ["technical_skills"]
}

interface Criterion {
  id: string;
  name: string;
  description: string;
  maxPoints: number;
  keywords: string[];            // AI hints
  evaluationGuidelines: string;  // Detailed instructions
}
```

### 4. Orchestration: LangChain as the "Brain"

LangChain won't just send a prompt; it will manage the **logic flow**:

- **Document Loaders:** Automatically handle different file types (PDF, Docx) from your FastAPI endpoints.
- **Chains & Parsers:** LangChain will take the AI's raw analysis and force it into a structured format that matches your **Zod** schemas on the frontend.
- **Memory:** It will store the "Chat History" in Postgres so the user can ask follow-up questions about a specific score.
- **Multi-Provider Support:** LangChain abstracts the AI provider, allowing seamless switching between Claude, GPT, Gemini, Groq, or Ollama.

### 5. Multi-Agent Architecture

| Agent | Responsibility | Recommended Provider |
|-------|---------------|---------------------|
| **Parser Agent** | Extract and clean text from PDFs/DOCX | Gemini (fast, cheap) |
| **Scorer Agent** | Evaluate CV against criteria | Claude (best reasoning) |
| **Chat Agent** | Answer questions about scores | GPT-4o or Claude |
| **Notification Agent** | Send alerts for high scores | Uses Scorer's provider |
| **Embeddings** | Generate vectors for semantic search | OpenAI embeddings |

---

## 6 Signature Features & How They Work

### Feature 1: "Candidate Match-Up" (Cross-CV Comparison)

- **The Tech:** LangChain + `pgvector`
- **How it works:** Instead of just scoring one CV, you compare a new upload against your entire database of previous candidates.
- **Benefit:** You can tell a recruiter: "This person is in the top 5% of all Python developers we've seen this month."

### Feature 2: "Explainable Scoring" (Conversational Deep-Dive)

- **The Tech:** LangChain Conversation Retrieval Chain
- **How it works:** After the scorecard (Pass/Fail) appears, the user clicks a "Why?" button. This opens a chat. LangChain retrieves the specific context of that CV from the database and uses the Chat Agent to explain, "The candidate failed the Fintech criteria because their experience is in Retail, not Finance."

### Feature 3: "Automated High-Flyer Alerts"

- **The Tech:** FastAPI Background Tasks + External APIs (Email/WhatsApp)
- **How it works:** Once the LangChain analysis is complete, if the `score >= threshold`, FastAPI triggers a background task. This task formats a message and sends via **Email and/or WhatsApp** immediately.
- **Benefit:** Recruiters get instant notifications for "A-Player" candidates without refreshing the dashboard.

### Feature 4: "Custom Evaluation Templates"

- **The Tech:** PostgreSQL + LangChain Prompt Templates + React UI
- **How it works:** Users create custom evaluation templates with their own criteria, point allocations, and passing thresholds. The system includes a default "AI-First Fintech" template. LangChain dynamically builds the evaluation prompt based on the selected template.
- **Benefit:** Same platform works for any industry or role type.

### Feature 5: "Semantic Search Dashboard"

- **The Tech:** TanStack Table + Vector Search
- **How it works:** Instead of searching for keywords like "React," the user types "Experienced frontend lead with fintech background." The backend performs a **Semantic Search** in the vector database to find the best matches even if those exact words aren't in the CV.

### Feature 6: "Multi-Provider AI Configuration"

- **The Tech:** User Settings + Encrypted API Key Storage
- **How it works:** Users bring their own API keys (BYOK) for Claude, GPT, Gemini, Groq, or Ollama. They can assign different providers to different agents for cost/quality optimization.
- **Benefit:** Open-source friendly, no shared API keys, privacy option with local models.

---

## User Interface Flow

### Flow 1: First-Time Setup (Onboarding)

```
1. Register/Login
   └── Email/Password or Google OAuth

2. Welcome Screen
   └── "Set up your AI providers to get started"

3. API Keys Setup Page
   ├── Add at least ONE provider key
   ├── Validate key on entry (test API call)
   ├── Show masked key: "sk-ant-...x7Kj"
   └── [Save & Continue]

4. Agent Configuration (Optional - Advanced)
   ├── Parser Agent: Select provider + model
   ├── Scorer Agent: Select provider + model
   ├── Chat Agent: Select provider + model
   └── Embeddings: Select provider + model
   └── [Use Defaults] or [Save Custom]

5. Redirect to Dashboard
```

### Flow 2: CV Upload & Evaluation

```
1. Dashboard
   └── [Upload CV] button

2. Upload Page
   ├── Drag & Drop zone for PDF
   ├── Template Selector dropdown:
   │   ├── ⭐ AI-First Fintech (System)
   │   ├── My Custom Template 1
   │   └── [+ Create New Template]
   └── [Evaluate] button

3. Processing Screen
   ├── "Parsing document..." (Parser Agent)
   ├── "Evaluating candidate..." (Scorer Agent)
   └── "Generating insights..."

4. Scorecard Result
   ├── Pass/Fail Badge
   ├── Total Score (circular progress)
   ├── Criteria breakdown (expandable)
   ├── [Why?] → Opens chat
   ├── [Re-evaluate with different template]
   └── [Download Report]
```

### Flow 3: Template Management

```
1. Settings → Evaluation Templates

2. Templates List
   ├── System Templates (read-only, view only)
   │   └── ⭐ AI-First Fintech
   └── My Templates (editable)
       ├── Junior Developer Screening
       └── [+ Create New Template]

3. Template Editor
   ├── Template Name
   ├── Description
   ├── Passing Score threshold (slider: 0-100)
   ├── Minimum Criteria Met (number input)
   ├── Criteria List:
   │   ├── [+ Add Criterion]
   │   └── Each Criterion:
   │       ├── Name
   │       ├── Max Points (slider)
   │       ├── Description
   │       ├── Keywords (tags input)
   │       ├── Required? (checkbox)
   │       └── [Delete]
   └── [Save Template]
```

### Flow 4: Settings & API Keys

```
1. Settings Page
   ├── Profile Section
   │   ├── Name, Email
   │   └── Change Password
   │
   ├── API Keys Section
   │   ├── Claude: [sk-ant-...x7Kj] [Edit] [Delete]
   │   ├── OpenAI: Not configured [+ Add]
   │   ├── Gemini: [AIza...Kx9f] [Edit] [Delete]
   │   ├── Groq: Not configured [+ Add]
   │   └── Ollama: Not configured [+ Add]
   │
   ├── Agent Configuration Section
   │   ├── Parser Agent: [Gemini ▾] [gemini-2.0-flash ▾]
   │   ├── Scorer Agent: [Claude ▾] [claude-sonnet-4-20250514 ▾]
   │   ├── Chat Agent: [OpenAI ▾] [gpt-4o ▾]
   │   └── Embeddings: [OpenAI ▾] [text-embedding-3-small ▾]
   │
   ├── Notification Settings Section
   │   ├── Email Alerts: [Toggle]
   │   ├── WhatsApp Alerts: [Toggle]
   │   ├── WhatsApp Number: [+1 555-123-4567]
   │   └── Alert Threshold: [80] (score to trigger)
   │
   └── Evaluation Templates Section
       └── [Manage Templates] → Flow 3
```

---

## The "User Flow" Summary

1. **Auth:** User logs in (React + FastAPI + Email/Google OAuth).
2. **Setup:** User adds API keys for their preferred AI providers.
3. **Configure:** User optionally assigns providers to agents (or uses defaults).
4. **Template:** User selects an evaluation template (system or custom).
5. **Upload:** User drops a CV (Drag & Drop + Axios).
6. **Process:** FastAPI cleans the text → LangChain generates embeddings → Saves to **pgvector**.
7. **Analyze:** LangChain runs the "Evaluation Chain" against the selected template's criteria.
8. **Trigger:** Logic check: `if score >= threshold`: Send Email/WhatsApp; `else`: Just update the UI.
9. **Review:** User views the scorecard and uses the Chat feature to ask questions.

---

## Database Schema Overview

```
Tables:
├── users
│   ├── id, email, password_hash, name, auth_provider
│   └── created_at, updated_at
│
├── user_api_keys (encrypted)
│   ├── id, user_id, provider (claude|openai|gemini|groq|ollama)
│   ├── encrypted_key, key_hint (last 4 chars)
│   └── created_at, updated_at
│
├── user_agent_config
│   ├── id, user_id
│   ├── parser_provider, parser_model
│   ├── scorer_provider, scorer_model
│   ├── chat_provider, chat_model
│   ├── embeddings_provider, embeddings_model
│   └── created_at, updated_at
│
├── evaluation_templates
│   ├── id, user_id (null for system), is_system_template
│   ├── name, description
│   ├── passing_score, minimum_criteria_met
│   └── created_at, updated_at
│
├── template_criteria
│   ├── id, template_id
│   ├── name, description, max_points
│   ├── keywords (jsonb), evaluation_guidelines
│   ├── is_required, sort_order
│   └── created_at
│
├── cvs
│   ├── id, user_id, filename, original_text
│   ├── status (pending|processing|evaluated|error)
│   └── uploaded_at
│
├── cv_evaluations
│   ├── id, cv_id, template_id
│   ├── score, status (pass|fail), reasoning
│   ├── criteria_results (jsonb)
│   └── evaluated_at
│
├── cv_embeddings
│   ├── id, cv_id
│   ├── embedding vector(1536)
│   └── created_at
│
├── chat_history
│   ├── id, user_id, cv_id
│   ├── role (user|assistant), message
│   └── created_at
│
└── notification_settings
    ├── id, user_id
    ├── email_enabled, whatsapp_enabled
    ├── whatsapp_number, threshold_score
    └── created_at, updated_at
```

---

## Security Considerations

### API Key Storage
- **Encryption:** AES-256 encryption at rest
- **Key Derivation:** Use user-specific salt + master key
- **Never Log:** API keys excluded from all logs
- **Masking:** UI shows only last 4 characters
- **Validation:** Test API call on key entry

### Authentication
- **JWT Tokens:** Access (30 min) + Refresh (7 days)
- **Password Hashing:** bcrypt with 12 rounds
- **OAuth:** Google OAuth 2.0 support