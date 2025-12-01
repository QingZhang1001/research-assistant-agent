from typing import Optional, List, Any
import uuid
from pprint import pformat


from google.genai import types
import asyncio


# Import Metric Plugin
# from observability.metrics_plugin import MetricsPlugin


# ============================================================================
# Helper utilities
# ============================================================================
def _render_tool_output(tool_name: str, output: Any) -> str:
    """Convert tool outputs (dict/list/str/etc.) into printable text."""
    if isinstance(output, str):
        return output
    if isinstance(output, (dict, list, tuple)):
        return pformat(output, width=100)
    return repr(output)



# ============================================================================
# Create Orchestrator Workflow
# ============================================================================

async def ainput(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: input(prompt))


async def run_orchestrator_session(
    session_service,
    keywords_runner,
    retrieval_runner,
    foresee_runner,
    app_name: str,
    user_id: str,
) -> None:
    # metrics = MetricsPlugin()
    session_id = f"demo_session_{uuid.uuid4().hex[:8]}"  # create unique session id
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    print(f"\n🦉 I am your private research assistant. We will first agree on search keywords, then retrieve papers from arXiv.")
    print(f"Type 'exit' to end the conversation.\n")

    #===================
    # Phase 1: Keyword Extraction and Confirmation
    #===================
    print("Step 1: Please briefly describe your research topic.")
    user_query = (await ainput("You > ")).strip()
    if user_query.lower() in {"exit", "quit"}:
        return

    confirmed_keywords: Optional[List[str]] = None
    while not confirmed_keywords:
        content = types.Content(parts=[types.Part(text=user_query)])
        print("\n🔎 Keywords Agent is analyzing your query...\n")

        # Run the keywords_agent for this turn
        async for event in keywords_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,

        ):
            # metrics.on_keywords_event(event)
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        # This is the Keywords Agent speaking to the user
                        print(f"\n🦉 Keywords Agent > {part.text}")

            tool_response = getattr(event, "tool_response", None)
            if tool_response and getattr(tool_response, "output", None):
                rendered = _render_tool_output(
                    tool_response.tool_name, tool_response.output
                )
                print(f"🛠️ Tool `{tool_response.tool_name}` output:\n{rendered}")

        # After running the keywords_agent, check the shared session state to see
        # if the keywords have been confirmed.
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        state = session.state or {}

        if state.get("confirmed"):
            # Prefer confirmed_keywords, fall back to keywords if needed
            ck = state.get("confirmed_keywords") or state.get("keywords") or []
            if ck:
                confirmed_keywords = list(ck)

        if confirmed_keywords:
            break

        # If we reach here, keywords are not yet confirmed
        print(
            "\nThe keywords are not confirmed yet. "
            "You can refine your request or say which keywords you prefer."
        )
        user_query = (await ainput("You (keyword refinement) > ")).strip()
        if user_query.lower() in {"exit", "quit"}:
            return


    # ========================
    # Phase 2: Retrieval
    # ========================
    print("\n✅ Confirmed keywords:", ", ".join(confirmed_keywords))
    print("Step 2: I will now retrieve papers from arXiv using these keywords.")

    keywords_str = ", ".join(confirmed_keywords)
    retrieval_prompt = (
        "Please retrieve papers from arXiv using these keywords: "
        f"{keywords_str}. Use the `retrieve_papers` tool and then summarize the "
        "results in a numbered list with title, authors, year, and abstract."
    )

    retrieval_content = types.Content(parts=[types.Part(text=retrieval_prompt)])
    async for event in retrieval_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=retrieval_content,
    ):
        # metrics.on_retrieval_tool(tool_response)
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"\n🦉 Retrieval Agent > {part.text}")

        tool_response = getattr(event, "tool_response", None)
        if tool_response and getattr(tool_response, "output", None):
            rendered = _render_tool_output(
                tool_response.tool_name, tool_response.output
            )
            print(f"🛠️ Tool `{tool_response.tool_name}` output:\n{rendered}")


    # =============================
    # Phase 3: Analyze and Foresee
    # =============================
    # Before this phase, there need to be a banner remind user to let the foresee_app to take action.
    print("Step 3: I can give you a summarize of these research and show you potential future directions, press 'Enter' to start.")
    _ = (await ainput("Press Enter to continue, or type 'skip' to skip this step > ")).strip().lower()
    if _ in {"skip", "no", "n"}:
        return
    foresee_prompt = (
        "Please analyze the retrieved papers using your tool `get_retrieved_papers`. "
        f"The confirmed search keywords were: {keywords_str}. "
        "First summarize the current research themes and hotspots, then propose 3–5 "
        "concrete future research directions."
    )
    
    foresee_content=types.Content(parts=[types.Part(text=foresee_prompt)])
    async for event in foresee_runner.run_async(
        user_id=user_id, 
        session_id=session_id,
        new_message=foresee_content,
    ):
        # metrics.mark_foresee_used()
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"\n🦉 Foresee Agent > {part.text}")

                
        tool_response = getattr(event, "tool_response", None)
        if tool_response and getattr(tool_response, "output", None):
            rendered = _render_tool_output(
                tool_response.tool_name, tool_response.output
            )
            print(f"🛠️ Tool `{tool_response.tool_name}` output:\n{rendered}")


                

