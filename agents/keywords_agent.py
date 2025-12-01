from typing import List, Dict, Any

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext


def save_keywords(tool_context: ToolContext, keywords: List[str], confirmed: bool = False) -> Dict[str, Any]:
    """
    Save suggested or confirmed keywords into the shared session state.

    - If `confirmed` is False:
        * Store the keywords under state["keywords"].
    - If `confirmed` is True:
        * Store under BOTH state["keywords"] and state["confirmed_keywords"],
          and set state["confirmed"] = True.

    This allows the retrieval_agent to reliably read the final, confirmed
    keywords from state["confirmed_keywords"].
    """
    keywords_list = keywords or []

    tool_context.state["keywords"] = keywords
    tool_context.state["confirmed"] = confirmed

    if confirmed:
        tool_context.state["confirmed_keywords"] = keywords_list
        status = "confirmed"
    else:
        status = "suggested"

    print(f"[keywords_agent.save_keywords] status={status}, keywords={keywords_list}")

    return {"status": status, "keywords": keywords_list}   


def create_keywords_agent(model) -> LlmAgent:
    return LlmAgent(
        model = model,
        name = 'keywords_agent',
        description = "Agent that iteratively proposes and confirms search keywords.",
        instruction = """
        
        You are a professional research assistant that helps users choose keywords for searching
        academic papers.

        Conversation flow:
        1. Analyze the user's query and propose 2-4 concise keywords or short phrases (use a numbered list).
        2. Ask whether the user wants to search with those keywords. If they decline, ask clarifying
        questions and then suggest a revised list.
        3. Whenever you present a draft list, call the `save_keywords` tool with confirmed=False.
        4. When the user explicitly confirms the keywords, call `save_keywords` with confirmed=True and finish
        with: `FINAL KEYWORDS: keyword1, keyword2, ...`.
        5. Remind the users to confirm the keywords before the retrieval agent starts to work.
        5. Do NOT output FINAL KEYWORDS until the user confirms.

        Confirmation signals include:
        - The user says 'OK','ok','yes' or 'y'.
        - The user repeats one of the suggested keywords and says they want to use it.
        - The user says sentences like "the confirmed keyword is ...", or "I would like to start with ...".
        """,
        tools=[save_keywords],
    )
