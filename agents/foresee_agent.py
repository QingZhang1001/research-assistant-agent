from typing import Optional, List,Dict, Any
import uuid

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext

def get_retrieved_papers(tool_context: ToolContext) -> List[Dict[str, Any]]:
    """ Read retrieved paper with the tool `retrieve_papers` from session state. 

        Expects `retrieval_agent.retrieval_papers` to have stored a list of paper dicts under `state["retrieved_papers"]`.
        Returns:
            {
                "status": "success",
                "total": <int>,
                "abstract": [<str>, ...],
                "papers": [<paper_dict>, ...],
            }
            
    """

    abstracts: List[str] = []
    papers = tool_context.state.get("retrieved_papers") or []
    for paper in papers:
        abstract = paper.get("abstract") or ""
        
        if abstract:
            abstracts.append(abstract)
    print(f"[foresee_agent.get_retrieved_papers] got {len(papers)} papers")
    return {
        "status": "success",
        "total": len(papers),
        "abstracts": abstracts,
        "papers": papers
        }

  

# Create an Agent with LLM to summarise the state quo of research in this domain and foresee the future directions.

def create_foresee_agent(model) -> LlmAgent:
    return LlmAgent(
        model=model,
        name='foresee_agent',
        description="Agent that analyzes retrieved papers to summarize research trends and future trends",
        instruction="""
        You are a professional and helpful research assistant. 

        Your tasks are:
        1. Call the `get_retrieved_papers` tool to obtain the list of research directions.
        2. Analyze and summarize the abstracts to summarize:
            - the main research themes/topics,
            - the typical methods or approaches used,
            - the current research hotspots.
        3. Based on this analysis, foresee 3-5 concrete future research directions.
           Make them specific and actionable (e.g., "Apply X methodology to problem Y in population Z", rather than vague statements).
        4. Present your answer in a clear structure, for example:
            ## Current Research Themes
            1. ...
 
            ## Research Hotspots
            - ...

            ## Possible Future Directions
            1. ...  

            Always ground your analysis in the given abstracts. If no papers are available, briefly explain that to the user instead of guessing.
         
            """,

        tools=[get_retrieved_papers]
    )
