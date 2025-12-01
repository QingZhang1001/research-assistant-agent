import asyncio
import logging
import os
from dotenv import load_dotenv

from google.adk.apps.app import App
from google.adk.models.google_llm import Gemini
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.keywords_agent import create_keywords_agent
from agents.retrieval_agent import create_retrieval_agent
from agents.foresee_agent import create_foresee_agent
from core.orchestrator import run_orchestrator_session


APP_NAME = "agents"
USER_ID = "demo_user"


def setup_logging() -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        filename="research_assistant.log",
        filemode="a",
    )
    # Reduce noise from underlying libraries (optional)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)

def create_model() -> Gemini:
    """Create a shared Gemini model instance with retry configuration."""
    retry_config = types.HttpRetryOptions(
        attempts=3,
        exp_base=3,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )
    return Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

async def async_main() -> None:
    """Async entry point: initialize agents and run the orchestrator session."""
    load_dotenv()
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError("API_KEY not found in environment. Please set it in a .env file.")
    os.environ["GOOGLE_API_KEY"] = api_key

    setup_logging()
    logger = logging.getLogger("research_assistant")
    logger.info("Starting Research Assistant application")
    model = create_model()
    session_service = InMemorySessionService()

    logging_plugin = LoggingPlugin(name="research_assistant_logging")
    plugins = [logging_plugin]

    # Create agents
    keywords_agent = create_keywords_agent(model)
    retrieval_agent = create_retrieval_agent(model)
    foresee_agent = create_foresee_agent(model)

    # Create Apps
    keywords_app = App(
        name=APP_NAME,
        root_agent=keywords_agent,
        plugins=plugins,
    )
    retrieval_app = App(
        name=APP_NAME,
        root_agent=retrieval_agent,
        plugins=plugins,
    )
    foresee_app = App(
        name=APP_NAME,
        root_agent=foresee_agent,
        plugins=plugins,
    )
    # Create runners
    keywords_runner = Runner(
        app=keywords_app,
        session_service=session_service,
    )
    retrieval_runner = Runner(
        app=retrieval_app,
        session_service=session_service,
    )
    foresee_runner = Runner(
        app=foresee_app,
        session_service=session_service,
    )

    # Run the orchestrated multi-agent session
    await run_orchestrator_session(
        session_service=session_service,
        keywords_runner=keywords_runner,
        retrieval_runner=retrieval_runner,
        foresee_runner=foresee_runner,
        app_name=APP_NAME,
        user_id=USER_ID,
    )
    logger.info("Research Assistant session finished.")


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Exiting...")
    except Exception as e:
        logging.exception("Fatal error while running Research Assistant", exc_info=e)
        print("\n⚠️ The Research Assistant encountered an unexpected error.")
        print("It might be due to network issues or the LLM service being overloaded.")
        print(f"Details: {repr(e)}")
    
if __name__ == "__main__":
    main()



