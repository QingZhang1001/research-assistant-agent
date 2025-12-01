from typing import List, Dict, Any

import arxiv
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext


# ============================================================================
# Helper functions
# ============================================================================
def _paper_to_dict(result: arxiv.Result) -> Dict[str, Any]:
    """Convert an arXiv result to a plain dict."""
    return {
        "entry_id": result.entry_id,
        "title": result.title.strip(),
        "authors": [author.name for author in result.authors],
        "published": result.published.isoformat() if result.published else None,
        "abstract": result.summary.strip(),
        "pdf_url": result.pdf_url,
    }


def _paper_to_summary(paper: Dict[str, Any]) -> str:
    """Return a short, human-readable summary for the paper."""
    authors = ", ".join(paper["authors"][:3])
    if len(paper["authors"]) > 3:
        authors += ", et al."
    published = paper["published"] or "unknown date"
    return f"- {paper['title']} ({published}) • {authors}"


# ============================================================================
# Tools
# ============================================================================
def get_keywords(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Read confirmed keywords from session state.
    Prioritises `confirmed_keywords`, falling back to `keywords`.
    """
    keywords = (
        tool_context.state.get("confirmed_keywords")
        or tool_context.state.get("keywords")
        or []
    )
    print(f"[retrieval_agent.get_keywords] Keywords in state: {keywords}")
    return {"status": "success", "keywords": keywords}


def retrieve_papers(tool_context: ToolContext, keywords: List[str]) -> Dict[str, Any]:
    """
    Retrieve papers from arXiv using the provided (or stored) keywords.
    """

    keywords_list = keywords or tool_context.state.get("confirmed_keywords") or tool_context.state.get("keywords") or []
    print(f"[retrieval_agent.retrieve_papers] Using keywords: {keywords_list}")

    if not keywords_list:
        return {
            "query": "",
            "total": 0,
            "papers": [],
            "summaries": [],
            "error": "No keywords provided or found in session state.",
        }

    query_str = " OR ".join(keywords_list)

    papers: List[Dict[str, Any]] = []
    summaries: List[str] = []

    try:
        search = arxiv.Search(
            query=query_str,
            max_results=10, 
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
        for result in search.results():
            paper_dict = _paper_to_dict(result)
            papers.append(paper_dict)
            summaries.append(_paper_to_summary(paper_dict))

        tool_context.state["retrieved_papers"] = papers

    except arxiv.HTTPError as exc:
        return {
            "query": query_str,
            "total": 0,
            "papers": [],
            "summaries": [],
            "error": f"arXiv request failed: {exc}",
        }

    return {
        "query": query_str,
        "total": len(papers),
        "papers": papers,
        "summaries": summaries,
    }


def create_retrieval_agent(model) -> LlmAgent:
    return LlmAgent(
        model=model,
        name="retrieval_agent",
        description="Agent that retrieves papers from arXiv with specific keywords.",
        instruction="""
            You are a professional research assistant that helps users find research papers with specific keywords.
            Always follow these steps:
            1. Call `get_keywords` to obtain the confirmed keywords from the shared session state.
            2. Pass those keywords to `retrieve_papers` to fetch papers from arXiv.
            3. Return a clear, numbered list of papers to the user. For each paper, show at least: title, authors, published year, and a short abstract based on the `summary` field.
        """,
        tools=[get_keywords, retrieve_papers],
    )

