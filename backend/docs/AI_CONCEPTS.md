# AI Concepts in CV Screening Agent

> A quick reference guide for understanding RAG, Vector Databases, and Embeddings as they apply to our project.

---

## Table of Contents
1. [Embeddings](#embeddings)
2. [Vector Database (pgvector)](#vector-database-pgvector)
3. [RAG (Retrieval-Augmented Generation)](#rag-retrieval-augmented-generation)
4. [How It All Works Together](#how-it-all-works-together-in-our-system)

---

## Embeddings

### What Are Embeddings?

**Embeddings** are numerical representations of text (or images, audio, etc.) as arrays of floating-point numbers. They capture the **semantic meaning** of content.

```
"Software Engineer with React experience"
    ↓ Embedding Model (e.g., OpenAI text-embedding-3-small)
[0.023, -0.156, 0.892, 0.045, ..., -0.234]  ← 1536 numbers
```

### Why Use Embeddings?

Text is hard for computers to compare. But with embeddings:

| Text Comparison | Embedding Comparison |
|-----------------|---------------------|
| "React developer" vs "Frontend engineer" | Cosine similarity ≈ 0.89 (high!) |
| "React developer" vs "Plumber" | Cosine similarity ≈ 0.12 (low) |

Embeddings understand that "React developer" and "Frontend engineer" are **semantically similar** even though they share no words.

### How We Use Embeddings in CV Screening Agent

```
┌─────────────────────────────────────────────────────────────────┐
│  CV Upload                                                      │
│  "Senior React Developer with 5 years fintech experience..."   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Embedding Generation                                           │
│  OpenAI text-embedding-3-small → [0.023, -0.156, ..., -0.234]  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Store in cv_embeddings Table                                   │
│  cv_id: uuid, embedding: vector[1536], chunk_text: "..."       │
└─────────────────────────────────────────────────────────────────┘
```

### Our Database Table

```python
# backend/app/db/models/cv.py
class CVEmbedding(Base):
    cv_id: Mapped[uuid.UUID]           # Which CV this belongs to
    chunk_text: Mapped[str]             # The text that was embedded
    chunk_index: Mapped[int]            # Order in the document
    embedding: Mapped[Vector]           # The actual embedding (1536 floats)
    model: Mapped[str]                  # e.g., "text-embedding-3-small"
```

---

## Vector Database (pgvector)

### What Is a Vector Database?

A **vector database** stores embeddings and enables **similarity search**. Instead of exact matching (SQL `WHERE name = 'John'`), you find items that are **semantically similar**.

### What Is pgvector?

**pgvector** is an extension for PostgreSQL that adds:
- `vector` data type (stores arrays of floats)
- Similarity operators (`<->` for L2 distance, `<=>` for cosine distance)
- Indexing for fast similarity search (HNSW, IVFFlat)

### Why pgvector Instead of Pinecone/Weaviate?

| Option | Pros | Cons |
|--------|------|------|
| **pgvector** | One database for everything, simpler, free | Less specialized |
| **Pinecone** | Purpose-built, scalable | Extra service, costs money |
| **Weaviate** | Full-featured | Complex setup |

For our scale, pgvector is perfect - we already use PostgreSQL.

### How Vector Search Works

```sql
-- Find CVs similar to a job description
SELECT cv_id, chunk_text
FROM cv_embeddings
ORDER BY embedding <=> '[0.023, -0.156, ..., -0.234]'  -- cosine distance
LIMIT 10;
```

This returns the 10 CVs whose embeddings are **closest** to the query embedding.

### Indexing for Speed

Without an index, PostgreSQL scans ALL embeddings (slow for millions of CVs).

```sql
-- Create HNSW index for fast approximate nearest neighbor search
CREATE INDEX ON cv_embeddings 
USING hnsw (embedding vector_cosine_ops);
```

| Index Type | Speed | Accuracy | Use Case |
|------------|-------|----------|----------|
| **None** | O(n) scan | 100% | Small datasets (<10k) |
| **IVFFlat** | Fast | ~95% | Medium datasets |
| **HNSW** | Very fast | ~99% | Large datasets |

---

## RAG (Retrieval-Augmented Generation)

### What Is RAG?

**RAG** = **R**etrieval-**A**ugmented **G**eneration

It's a pattern where you:
1. **Retrieve** relevant context from a database
2. **Augment** the LLM prompt with that context
3. **Generate** a response using the LLM

### Why RAG?

LLMs have limitations:
- **Knowledge cutoff** - Don't know recent events
- **No access to your data** - Can't see your CVs, documents
- **Hallucination** - May make things up

RAG solves this by **giving the LLM relevant context**.

### RAG vs Fine-Tuning

| Approach | Description | Use Case |
|----------|-------------|----------|
| **RAG** | Retrieve context, inject into prompt | Dynamic data, many users |
| **Fine-Tuning** | Train model on your data | Static knowledge, specific style |

RAG is cheaper, faster to set up, and works with data that changes.

### How RAG Works in CV Screening Agent

```
┌─────────────────────────────────────────────────────────────────┐
│  USER QUESTION                                                  │
│  "Why did this candidate get a low fintech score?"             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  1. EMBED THE QUESTION                                          │
│  "fintech experience evaluation" → [0.045, 0.892, ..., -0.123] │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. RETRIEVE RELEVANT CV CHUNKS (Vector Search)                 │
│  SELECT chunk_text FROM cv_embeddings                           │
│  WHERE cv_id = 'xxx' ORDER BY embedding <=> query_embedding    │
│                                                                 │
│  Results:                                                       │
│  - "Worked at retail company for 3 years..."                   │
│  - "Experience with inventory management software..."          │
│  - "No banking or financial services mentioned..."             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. AUGMENT THE PROMPT                                          │
│                                                                 │
│  System: You are a CV analyst. Use the context below.          │
│                                                                 │
│  Context:                                                       │
│  - "Worked at retail company for 3 years..."                   │
│  - "Experience with inventory management software..."          │
│                                                                 │
│  Question: Why did this candidate get a low fintech score?     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. GENERATE RESPONSE (LLM)                                     │
│                                                                 │
│  Claude: "The candidate received a low fintech score because   │
│  their experience is primarily in retail, not financial        │
│  services. There's no mention of banking, payments, crypto,    │
│  or other fintech-related work in their CV."                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## How It All Works Together in Our System

### The Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        CV UPLOAD FLOW                           │
└─────────────────────────────────────────────────────────────────┘

    [User uploads CV.pdf]
            ↓
    [Extract text with pdfplumber]
            ↓
    [Split into chunks (e.g., 500 tokens each)]
            ↓
    [Generate embedding for each chunk]
            ↓
    [Store in cv_embeddings table with pgvector]
            ↓
    [Evaluate CV with Claude AI]
            ↓
    [Store evaluation in cv_evaluations table]


┌─────────────────────────────────────────────────────────────────┐
│                     CHAT / Q&A FLOW (RAG)                       │
└─────────────────────────────────────────────────────────────────┘

    [User asks: "What are this candidate's strengths?"]
            ↓
    [Embed the question]
            ↓
    [Vector search: find relevant CV chunks]
            ↓
    [Build prompt with retrieved context]
            ↓
    [Claude generates answer using the context]
            ↓
    [Store in chat_history table]
```

### Our Database Tables Involved

| Table | Role |
|-------|------|
| `cvs` | Stores the original CV text |
| `cv_embeddings` | Stores vector embeddings for each chunk (pgvector) |
| `cv_evaluations` | Stores the AI-generated evaluation scores |
| `chat_history` | Stores the RAG-powered Q&A conversations |

### Code Example (Conceptual)

```python
# 1. Generate embedding for a CV chunk
async def embed_text(text: str) -> list[float]:
    response = await openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding  # [0.023, -0.156, ..., -0.234]

# 2. Store embedding in pgvector
embedding = await embed_text(cv_chunk)
cv_embedding = CVEmbedding(
    cv_id=cv.id,
    chunk_text=cv_chunk,
    chunk_index=0,
    embedding=embedding,
    model="text-embedding-3-small"
)
session.add(cv_embedding)

# 3. Search for similar chunks (RAG retrieval)
query_embedding = await embed_text(user_question)
result = await session.execute(
    select(CVEmbedding)
    .where(CVEmbedding.cv_id == cv_id)
    .order_by(CVEmbedding.embedding.cosine_distance(query_embedding))
    .limit(5)
)
relevant_chunks = result.scalars().all()

# 4. Build RAG prompt
context = "\n".join([chunk.chunk_text for chunk in relevant_chunks])
prompt = f"""
Context from the CV:
{context}

Question: {user_question}

Answer based on the context above.
"""

# 5. Generate response with Claude
response = await claude.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)
```

---

## LangChain

### What Is LangChain?

**LangChain** is a framework for building applications with Large Language Models (LLMs). Think of it as **Express.js but for AI** - it provides structure, abstractions, and utilities for common LLM patterns.

Instead of writing raw API calls to Claude/OpenAI, LangChain gives you:
- **Chains** - Composable sequences of operations
- **Prompts** - Templated, reusable prompts with variables
- **Output Parsers** - Convert LLM text output to structured data (JSON, Pydantic)
- **Document Loaders** - Load PDFs, Word docs, web pages, etc.
- **Text Splitters** - Break documents into chunks for embeddings
- **Retrievers** - Search vector databases (RAG)
- **Memory** - Conversation history management
- **Agents** - LLMs that can use tools and make decisions

### Why Use LangChain?

**Without LangChain (raw API calls):**
```python
# Manual, verbose, hard to maintain
import anthropic

client = anthropic.Anthropic()
prompt = f"""
You are a CV evaluator. Score this CV:

CV Text: {cv_text}

Return JSON with scores for each criterion.
"""
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)
# Manually parse the JSON from response.content[0].text
# Handle errors, retries, etc.
```

**With LangChain:**
```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Structured, reusable, composable
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
parser = PydanticOutputParser(pydantic_object=CVEvaluation)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a CV evaluator. {format_instructions}"),
    ("human", "Evaluate this CV:\n\n{cv_text}")
])

chain = prompt | llm | parser  # Composable pipeline!

result: CVEvaluation = chain.invoke({
    "cv_text": cv_text,
    "format_instructions": parser.get_format_instructions()
})
# result is already a Pydantic object, validated!
```

### LangChain Core Concepts

| Concept | What It Does | Example |
|---------|--------------|---------|
| **LLM/Chat Model** | Wrapper around AI providers | `ChatAnthropic`, `ChatOpenAI` |
| **Prompt Template** | Reusable prompts with variables | `"Evaluate this CV: {cv_text}"` |
| **Output Parser** | Converts text → structured data | JSON, Pydantic models |
| **Chain** | Sequence of operations | `prompt \| llm \| parser` |
| **Document Loader** | Loads files into text | `PyPDFLoader`, `Docx2txtLoader` |
| **Text Splitter** | Chunks text for embeddings | `RecursiveCharacterTextSplitter` |
| **Embeddings** | Generate vectors from text | `OpenAIEmbeddings` |
| **Vector Store** | Store & search embeddings | `PGVector` (pgvector) |
| **Retriever** | Search for relevant documents | `vectorstore.as_retriever()` |
| **Memory** | Conversation history | `ConversationBufferMemory` |
| **Agent** | LLM that uses tools | Tool-calling, decision making |

### How We Use LangChain in CV Screening Agent

```
┌─────────────────────────────────────────────────────────────────┐
│                      CV PROCESSING PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

    [PDF Upload]
          ↓
    [PyPDFLoader] ──────────────────── Document Loader
          ↓
    [RecursiveCharacterTextSplitter] ─ Text Splitter (chunks)
          ↓
    [OpenAIEmbeddings] ────────────── Embedding Model
          ↓
    [PGVector] ────────────────────── Vector Store (pgvector)
          ↓
    [ChatAnthropic + PydanticParser] ─ Evaluation Chain
          ↓
    [CVEvaluation] ────────────────── Structured Output


┌─────────────────────────────────────────────────────────────────┐
│                      RAG CHAT PIPELINE                          │
└─────────────────────────────────────────────────────────────────┘

    [User Question]
          ↓
    [PGVector Retriever] ──────────── Find relevant CV chunks
          ↓
    [ChatPromptTemplate] ──────────── Build prompt with context
          ↓
    [ChatAnthropic] ───────────────── Generate answer
          ↓
    [PostgresChatMessageHistory] ──── Store conversation
```

### LangChain Components We'll Use

| Component | Package | Purpose in Our App |
|-----------|---------|-------------------|
| `ChatAnthropic` | `langchain-anthropic` | CV evaluation with Claude |
| `ChatOpenAI` | `langchain-openai` | Alternative provider |
| `OpenAIEmbeddings` | `langchain-openai` | Generate embeddings |
| `PGVector` | `langchain-postgres` | Store/search embeddings in pgvector |
| `PyPDFLoader` | `langchain-community` | Load PDF files |
| `RecursiveCharacterTextSplitter` | `langchain-text-splitters` | Chunk documents |
| `PydanticOutputParser` | `langchain-core` | Parse LLM output to Pydantic |
| `ChatPromptTemplate` | `langchain-core` | Build prompts |
| `RunnableSequence` | `langchain-core` | Chain operations with `|` |

### LangChain vs Direct API Calls

| Aspect | Direct API | LangChain |
|--------|------------|-----------|
| **Setup** | Simple | More dependencies |
| **Code** | Verbose | Concise, composable |
| **Output Parsing** | Manual JSON parsing | Automatic Pydantic validation |
| **Error Handling** | Manual | Built-in retries |
| **Provider Switching** | Rewrite code | Change one line |
| **RAG** | Build from scratch | Built-in retrievers |
| **Memory** | Implement yourself | Built-in classes |
| **Best For** | Simple scripts | Production applications |

### Code Example: CV Evaluation Chain

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

# 1. Define output structure
class CriterionScore(BaseModel):
    name: str
    score: int
    max_score: int
    reasoning: str

class CVEvaluation(BaseModel):
    criteria: list[CriterionScore]
    total_score: int
    passed: bool
    recommendation: str

# 2. Set up the chain
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
parser = PydanticOutputParser(pydantic_object=CVEvaluation)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a CV evaluator for an AI-first fintech company.
    
Evaluate the CV against these criteria:
{criteria}

{format_instructions}"""),
    ("human", "CV Text:\n\n{cv_text}")
])

# 3. Create the chain (composable!)
evaluation_chain = prompt | llm | parser

# 4. Use the chain
result = await evaluation_chain.ainvoke({
    "cv_text": cv_text,
    "criteria": criteria_description,
    "format_instructions": parser.get_format_instructions()
})

# result is a validated CVEvaluation Pydantic object!
print(result.total_score)  # 75
print(result.passed)       # True
```

---

## Quick Reference

| Term | One-Line Definition |
|------|---------------------|
| **Embedding** | A list of numbers representing the meaning of text |
| **Vector** | Same as embedding - an array of floats |
| **pgvector** | PostgreSQL extension for storing and searching vectors |
| **Cosine Similarity** | Measure of how similar two vectors are (0 to 1) |
| **RAG** | Pattern: Retrieve context → Augment prompt → Generate response |
| **HNSW** | Fast index for approximate nearest neighbor search |
| **Chunk** | A piece of a document (e.g., a paragraph from a CV) |
| **LangChain** | Framework for building LLM applications with chains |
| **Chain** | Composable sequence of operations (`prompt \| llm \| parser`) |
| **Output Parser** | Converts LLM text to structured data (Pydantic) |

---

## Further Reading

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangChain + Anthropic](https://python.langchain.com/docs/integrations/chat/anthropic/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Explained (LangChain)](https://python.langchain.com/docs/tutorials/rag/)
- [What Are Vector Databases? (Pinecone)](https://www.pinecone.io/learn/vector-database/)
