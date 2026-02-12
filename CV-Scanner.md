# Cv scanner

## The Architectural Plan

### 1. Unified Storage: PostgreSQL + `pgvector`

Instead of having two separate databases, you will use **PostgreSQL** as your single source of truth.

- **Relational Side:** Stores user profiles (linked via Gmail OAuth), account settings, and metadata about uploaded CVs (filename, upload date, owner ID).
- **Vector Side (`pgvector`):** Stores the "Embeddings" of the CVs. This allows the AI to "mathematically" compare one resume to another or to a job description.
- **Usage:** When a user logs in via Gmail, your FastAPI backend checks the Relational tables. When they ask "Who are my top 5 candidates?", the backend queries the Vector columns.

### 2. Orchestration: LangChain as the "Brain"

LangChain won't just send a prompt; it will manage the **logic flow**:

- **Document Loaders:** Automatically handle different file types (PDF, Docx) from your FastAPI endpoints.
- **Chains & Parsers:** LangChain will take Claude's raw analysis and force it into a structured format that matches your **Zod** schemas on the frontend.
- **Memory:** It will store the "Chat History" in Postgres so the user can ask follow-up questions about a specific score.

---

## 5 Signature Features & How They Work

### Feature 1: "Candidate Match-Up" (Cross-CV Comparison)

- **The Tech:** LangChain + `pgvector`
- **How it works:** Instead of just scoring one CV, you compare a new upload against your entire database of previous candidates.
- **Benefit:** You can tell a recruiter: "This person is in the top 5% of all Python developers we've seen this month."

### Feature 2: "Explainable Scoring" (Conversational Deep-Dive)

- **The Tech:** LangChain Conversation Retrieval Chain
- **How it works:** After the scorecard (Pass/Fail) appears, the user clicks a "Why?" button. This opens a chat. LangChain retrieves the specific context of that CV from the database and uses Claude to explain, "The candidate failed the Fintech criteria because their experience is in Retail, not Finance."

### Feature 3: "Automated High-Flyer Alerts"

- **The Tech:** FastAPI Background Tasks + External APIs (Twilio/Viber)
- **How it works:** Once the LangChain analysis is complete, if the `score > 80`, FastAPI triggers a background task. This task formats a message and hits the **Viber/WhatsApp API** immediately.
- **Benefit:** Recruiters get instant notifications for "A-Player" candidates without refreshing the dashboard.

### Feature 4: "Adaptive Scoring Persona"

- **The Tech:** LangChain Prompt Templates
- **How it works:** You can store different "Hiring Profiles" in Postgres (e.g., "Strict Technical Search" vs. "Junior Growth Search"). LangChain swaps the prompt instructions dynamically based on which profile the user selects in the React UI.

### Feature 5: "Semantic Search Dashboard"

- **The Tech:** TanStack Table + Vector Search
- **How it works:** Instead of searching for keywords like "React," the user types "Experienced frontend lead with fintech background." The backend performs a **Semantic Search** in the vector database to find the best matches even if those exact words aren't in the CV.

---

## The "User Flow" Summary

1. **Auth:** User logs in (React + FastAPI + Gmail OAuth).
2. **Upload:** User drops a CV (React Hook Form + Axios).
3. **Process:** FastAPI cleans the text → LangChain generates embeddings → Saves to **pgvector**.
4. **Analyze:** LangChain runs the "Evaluation Chain" against your 3 criteria.
5. **Trigger:** Logic check: `if score > 80`: Send Viber/WhatsApp; `else`: Just update the UI.
6. **Review:** User views the scorecard and uses the Chat feature to ask questions.

**Would you like me to detail the "Multi-Agent" strategy—where one agent parses, one scores, and one handles the notification—to make the system even more robust?**