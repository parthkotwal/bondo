import json
from typing import List
from app.prompts.mentor_prompt import MENTOR_SYSTEM_PROMPT
from app.services.llm_client import call_llm
from app.services.rag import search_docs
from app.models.docs import DocSnippet
from app.models.mentor import MentorHelpResponse

def build_user_message(code: str, error: str | None, doc_snippets: List[DocSnippet]) -> str:
    """
    Combine code, error, and doc snippets into a single user message for the LLM.
    """
    doc_texts = [
        f"[DOC {i}]\nTitle: {s.title}\nURL: {s.url}\nText:\n{s.text}"
        for i, s in enumerate(doc_snippets)
    ]
    docs_block = "\n\n".join(doc_texts)

    return f"""
    User Code: 
    {code}
    
    Error Output:
    {error or "(none)"}
    
    Relevant Documentation Snippets:
    {docs_block}
    
    Now, explain the issue and provide a fix as per your given instructions.
    """.strip()
    
    
def mentor_help(code: str, error: str | None, library_name: str) -> MentorHelpResponse:
    """
    High-level orchestrator:
      - retrieve documentation
      - build prompt
      - call LLM
      - parse JSON response
    """
    # 1. Retrieve docs via RAG
    rag_results = search_docs(
        query=error if error else code,
        top_k=5,
    )

    # 2. Build system message for this library
    system_prompt = MENTOR_SYSTEM_PROMPT.format(
        library_name=library_name
    )

    # 3. Build user message
    user_content = build_user_message(
        code=code,
        error=error,
        doc_snippets=rag_results,
    )

    # 4. Call OpenAI using JSON response mode
    response_raw = call_llm(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
    )

    # 5. Parse JSON
    try:
        data = json.loads(response_raw)
    except Exception as e:
        # fallback if model returned invalid JSON
        data = {
            "explanation": f"LLM parsing error: {e}. Raw: {response_raw}",
            "suggested_fix": None,
            "doc_references": [],
        }

    # 6. Convert doc references if present
    doc_refs = []
    for s in data.get("doc_references", []):
        if isinstance(s, dict):
            doc_refs.append(
                DocSnippet(
                    id=s.get("id", "unknown"),
                    title=s.get("title", "Unknown title"),
                    text=s.get("text", ""),
                    url=s.get("url"),
                    score=s.get("score", 0.0),
                )
            )
        else:
            # fallback for malformed model output
            doc_refs.append(
                DocSnippet(
                    id="unknown",
                    title=str(s),
                    text="",
                    url=None,
                    score=0.0,
                )
            )

    return MentorHelpResponse(
        explanation=data.get("explanation", ""),
        suggested_fix=data.get("suggested_fix"),
        doc_references=doc_refs,
    )