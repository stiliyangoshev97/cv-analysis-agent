# CV Screening Agent - Testing Checklist

This document lists all features that need manual testing to ensure the application works fully.

> **Last Updated**: February 15, 2026
> **Test Environment**: localhost (backend :8000, frontend :5173)

---

## 🔑 Pre-requisites

Before testing, ensure:
- [ ] Backend running: `cd backend && uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] PostgreSQL running with `cv_screening_agent` database
- [ ] Valid OpenAI API key (required for embeddings)
- [ ] Valid Anthropic/OpenAI/Gemini API key (for LLM evaluation)

---

## 1. Authentication

### 1.1 Registration
- [ ] Navigate to `/register` (or register link from login)
- [ ] Register with valid email and password (min 8 chars)
- [ ] Verify error shown for duplicate email
- [ ] Verify error shown for weak password
- [ ] Verify redirect to home page after successful registration
- [ ] Verify user appears in navbar

### 1.2 Login
- [ ] Navigate to `/login`
- [ ] Login with registered email/password
- [ ] Verify error shown for wrong credentials
- [ ] Verify redirect to home page after login
- [ ] Verify JWT token stored (check localStorage)

### 1.3 Logout
- [ ] Click logout in user menu
- [ ] Verify redirected to login page
- [ ] Verify cannot access protected routes after logout
- [ ] Verify token cleared from localStorage

### 1.4 Session Persistence
- [ ] Login successfully
- [ ] Refresh the page
- [ ] Verify still logged in (token refresh works)
- [ ] Close browser, reopen
- [ ] Verify still logged in if within token expiry

### 1.5 Google OAuth (Optional)
- [ ] Click "Sign in with Google" (if configured)
- [ ] Complete Google OAuth flow
- [ ] Verify account created/linked
- [ ] Verify redirected to home page

---

## 2. Settings - API Keys

### 2.1 Navigate to Settings
- [ ] Click Settings in navbar or go to `/settings`
- [ ] Verify "API Keys" tab is active by default
- [ ] Verify setup warning banner if keys not configured

### 2.2 Add OpenAI Key
- [ ] Enter valid OpenAI API key (starts with `sk-`)
- [ ] Click "Validate" button
- [ ] Verify validation success message
- [ ] Click "Save" button
- [ ] Verify key hint shows (last 4 chars)
- [ ] Verify setup warning disappears (if only OpenAI needed)

### 2.3 Add Anthropic Key
- [ ] Enter valid Anthropic API key (starts with `sk-ant-`)
- [ ] Validate and save
- [ ] Verify key hint shows

### 2.4 Add Gemini Key (Optional)
- [ ] Enter valid Google AI API key
- [ ] Validate and save
- [ ] Verify key hint shows

### 2.5 Delete API Key
- [ ] Click delete button on a configured key
- [ ] Confirm deletion
- [ ] Verify key removed from list
- [ ] Verify setup warning reappears if required key deleted

### 2.6 Invalid Key Handling
- [ ] Enter an invalid API key
- [ ] Click validate
- [ ] Verify error message shown
- [ ] Verify save is blocked/disabled

---

## 3. Settings - LLM Preferences

### 3.1 Switch to LLM Preferences Tab
- [ ] Click "LLM Preferences" tab
- [ ] Verify default provider dropdown shows

### 3.2 Select Default Provider
- [ ] Select different provider (Anthropic/OpenAI/Gemini)
- [ ] Verify model dropdown updates with provider's models
- [ ] Save preferences
- [ ] Verify success toast

### 3.3 Per-Agent Configuration (If Available)
- [ ] Configure different model for Chat vs Scorer
- [ ] Save preferences
- [ ] Verify settings persist after page refresh

---

## 4. CV Upload & Evaluation

### 4.1 Single CV Upload
- [ ] Navigate to home page (`/`)
- [ ] Drag and drop a PDF file onto dropzone
- [ ] Verify file appears in staged list
- [ ] Click "Scan CVs" button
- [ ] Verify upload progress shown
- [ ] Verify evaluation completes (spinner → results)
- [ ] Verify CV appears in list with score

### 4.2 Batch CV Upload
- [ ] Drop multiple PDF files (2-5 files)
- [ ] Verify all files appear in staged list
- [ ] Click "Scan CVs"
- [ ] Verify sequential processing
- [ ] Verify all CVs appear in list after completion

### 4.3 File Validation
- [ ] Try uploading non-PDF file (e.g., .txt, .jpg)
- [ ] Verify rejection with error message
- [ ] Try uploading file > 10MB (if limit exists)
- [ ] Verify rejection

### 4.4 Error Handling
- [ ] Upload CV without OpenAI key configured
- [ ] Verify error message about missing API key
- [ ] Verify redirect to settings (if implemented)

---

## 5. CV List & Detail View

### 5.1 CV List
- [ ] Verify all uploaded CVs appear in list
- [ ] Verify CV cards show:
  - [ ] Filename or candidate name
  - [ ] Score with color (green/yellow/red)
  - [ ] Pass/Fail badge
  - [ ] Upload date
- [ ] Verify pagination/scroll works for many CVs

### 5.2 CV Detail View
- [ ] Click on a CV card
- [ ] Verify modal/page opens with full details
- [ ] Verify criteria breakdown shown:
  - [ ] Each criterion name
  - [ ] Score and max points
  - [ ] Reasoning text
- [ ] Verify overall score and status

### 5.3 Delete CV
- [ ] Click delete button on CV
- [ ] Confirm deletion
- [ ] Verify CV removed from list
- [ ] Verify toast notification

---

## 6. Chat - Ask AI

### 6.1 Ask Question
- [ ] Open CV detail view
- [ ] Find chat input or "Ask AI" button
- [ ] Type a question (e.g., "What is their Python experience?")
- [ ] Submit question
- [ ] Verify loading state
- [ ] Verify AI response appears
- [ ] Verify response is relevant to CV content

### 6.2 Chat History
- [ ] Ask multiple questions
- [ ] Verify chat history shows all Q&A pairs
- [ ] Refresh page
- [ ] Verify chat history persists

### 6.3 Clear History
- [ ] Click "Clear History" button (if available)
- [ ] Confirm action
- [ ] Verify chat history cleared

---

## 7. Chat - Explain Criterion

### 7.1 Explain Score
- [ ] Open CV detail view
- [ ] Click "Why?" button on a criterion (e.g., "Technical Skills")
- [ ] Verify loading state
- [ ] Verify explanation appears
- [ ] Verify explanation references CV content

### 7.2 Multiple Explanations
- [ ] Request explanations for different criteria
- [ ] Verify each explanation is unique and relevant

---

## 8. Chat - Compare CVs

### 8.1 Select CVs for Comparison
- [ ] Upload at least 2 CVs
- [ ] Select CVs for comparison (checkbox or multi-select)
- [ ] Click "Compare" button
- [ ] Verify comparison modal/page opens

### 8.2 View Comparison
- [ ] Verify both CVs shown side-by-side (or listed)
- [ ] Verify AI comparison summary
- [ ] Verify individual scores visible
- [ ] Ask follow-up question about comparison

---

## 9. Dark Mode

### 9.1 Toggle Dark Mode
- [ ] Find theme toggle in header
- [ ] Click to switch to dark mode
- [ ] Verify all UI elements update colors
- [ ] Verify text is readable
- [ ] Verify no white flashes

### 9.2 System Preference
- [ ] Set system to dark mode
- [ ] Refresh app (or set to "System" preference)
- [ ] Verify app follows system preference

### 9.3 Persistence
- [ ] Toggle dark mode
- [ ] Refresh page
- [ ] Verify preference persisted

---

## 10. Error Handling & Edge Cases

### 10.1 Network Errors
- [ ] Stop backend server
- [ ] Try to upload CV
- [ ] Verify error toast/message
- [ ] Restart server
- [ ] Verify app recovers

### 10.2 Session Expiry
- [ ] Login
- [ ] Wait for token expiry (or manually clear token)
- [ ] Try to perform action
- [ ] Verify redirect to login

### 10.3 Rate Limiting
- [ ] Make many rapid requests (10+ per second)
- [ ] Verify rate limit error shown
- [ ] Wait and retry
- [ ] Verify request succeeds

### 10.4 Large CV
- [ ] Upload a large CV (10+ pages)
- [ ] Verify processing completes (may be slow)
- [ ] Verify full text extracted

---

## 11. Responsive Design (Optional)

### 11.1 Mobile View
- [ ] Resize browser to mobile width (< 768px)
- [ ] Verify layout adapts
- [ ] Verify navigation works (hamburger menu?)
- [ ] Verify CV upload works on mobile

### 11.2 Tablet View
- [ ] Resize to tablet width (768-1024px)
- [ ] Verify layout adapts

---

## 12. Backend API Sanity Checks

Use curl or Postman to verify backend directly:

### 12.1 Health Check
```bash
curl http://localhost:8000/api/cv/health
# Expected: {"status": "healthy", "database": "connected", ...}
```

### 12.2 Setup Status (Authenticated)
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/settings/setup-status
# Expected: {"is_complete": true/false, "openai_configured": true/false, ...}
```

### 12.3 List CVs
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/cv/
# Expected: {"items": [...], "total": N, ...}
```

### 12.4 List Profiles
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/profiles/
# Expected: {"profiles": [...], "total": N}
```

---

## ❌ Known Issues / Not Yet Implemented

These features have backend support but NO frontend UI:

| Feature | Backend Endpoint | Frontend Status |
|---------|------------------|-----------------|
| Evaluation Profiles/Templates | `/api/profiles/*` | ❌ Not implemented |
| Template selector on upload | Upload accepts `template_id` | ❌ Not implemented |
| Similar CVs | `/api/cv/{id}/similar` | ❌ Not implemented |
| CV Ranking | `/api/cv/{id}/ranking` | ❌ Not implemented |
| Semantic Search | `/api/cv/search` | ❌ Not implemented |
| Re-evaluate CV | `/api/cv/{id}/re-evaluate` | ❌ Not implemented |
| Notification Settings form | `/api/notifications/settings` | ⚠️ Partial (page exists) |
| Test Notification | `/api/notifications/test` | ❌ Not implemented |

---

## ✅ Test Completion Checklist

After testing, verify:

- [ ] All authentication flows work
- [ ] API keys can be added/validated/deleted
- [ ] LLM preferences save correctly
- [ ] CV upload works with valid API keys
- [ ] CV evaluation shows correct scores
- [ ] Chat features work (ask, explain, compare)
- [ ] Dark mode works
- [ ] Error handling is graceful
- [ ] No console errors in browser
- [ ] No 500 errors in backend logs

---

## 📝 Test Notes

Use this section to document any issues found during testing:

```
Date: ____________
Tester: ____________

Issues Found:
1. 
2. 
3. 

Notes:
-
-
```
