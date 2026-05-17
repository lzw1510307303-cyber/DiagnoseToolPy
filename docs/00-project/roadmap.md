# Roadmap

## V0.1: MVP Closed Loop

Goal: Complete the minimum loop from server directory scanning to case archival.

Scope:

- Project skeleton
- FastAPI app
- Config loading
- Path whitelist validation
- Server directory scanning
- File-based task state
- Streaming log reading
- Multiline stack trace merge
- Complex header parser
- Rule-based classification
- Evidence package generation
- HTML report generation
- Case draft generation
- Manual case creation
- case.md + metadata.yaml storage
- index.yaml update
- Simple keyword retrieval

## V0.2: Retrieval and Knowledge Enhancement

Scope:

- BM25 retrieval
- Rule-based retrieval
- Similar case prompt context
- Case templates
- Markdown case import
- RAG JSONL export
- Case index rebuild UI/API

## V0.3: AI Diagnosis Integration

Scope:

- Optional LLM provider configuration
- One-click AI diagnosis
- Save AI diagnosis result
- Compare AI diagnosis with human confirmed root cause
- Generate bugfix prompt
- Generate test suggestions
- Generate monitoring suggestions

## V0.4: Optional Vector Retrieval

Scope:

- Optional embedding model support
- Optional LanceDB or FAISS backend
- Hybrid ranking
- Vector index rebuild
- Similar case reranking
