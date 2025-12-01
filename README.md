# 🦉 Research Copilot - Multi-Agent Academic Research Assistant

 _A Capstone Project for 5-Day AI Agents Intensive Course with Google_ 

 ## 📌 Overview
 Research Copilot is a multi-agent system designed to help researchers explore academic domains effectively.  
 When a user query about a research topic, the system:

 1. Analyze the query and extract keywords;
 2. Retrieve relevant research papers from arXiv;
 3. Analyzes abstracts to generate
  * current research themes
  * future research directions
4. Present the findings interactively through CLI interface.

## 🏆 This project demonstrates key concepts taught in the course:

✅ **Agent powered by an LLM**  
✅ **Custom tools**  
✅ **Sessions & state management**  
✅ **Observability: Logging, Tracing, Metrics**  

## 🧠 System Architecture

```plaintext
                    +-------------------------+
                    | main.py                 |
                    |- Loads env & API key    |
      User Input -->|- Init logging & session |
                    |- Init model & agent     |
                    +-------------------------+
                                |
                                v
                    +-------------------------+
                    |      Orchestrator       |
                    | core/orchestrator.py    |
                    |Controls 3-phase workflow|         
                    +-------------------------+
                                |
                                v
        |-----------------------|---------------------|
        v                       v                     v
+----------------+   +------------------+  +-------------------+ 
| Keywords Agent |   | Retrieval Agent  |  |  Foresee Agent    |
| extract/refine |   | arXiv API search |  |  Trend analysis   |  
|      & save    |   | save to session  |  | Furture direction | 
|    keywords    |   +------------------+  |    & foresee      |
+----------------+                         +-------------------+
```





## 🧩 Key Components
1. 🤖 `Keywords Agent`  
LLM-powered agent that:
* interprets user's query;
* provides serveral keywords options
* saves the keywords with a custom tool (🛠️ `save_keywords`)
* waits for explicit user confirmation
2. 🤖 `Retrieval Agent`  
Tool-using agent that:
* reads the saved keywords in session state (🛠️ `get_keywords`)
* retrieved papers via arXiv (arXiv Python API)
* collects and represent paper's metadata (title, author, year, abstract)
* saves retrieved papers into the session 
3. 🤖 `Foresee Agent`   
LLM-powered analysis agent that:
* loads all retrieved abstracts (🛠️ `get_retrieved_papers`)
* performs topic summarization
* generates 3-5 future research directions

4. ⚙️ `Orchestrator`  
Controls the workflow in three phases:
* Phase 1: Keywords negotiation
* Phase 2: Paper retrieval
* Phase 3: Research analysis and trend analysis

5. 👁️ Observability
* LoggingPlugin(ADK built-in)
* File-based logging: research_assistant.log
* Easily extendable with custom MetricsPlugin

## ⚙️ Installation & Setup
1. Clone the repo  
```bash
git clone https://github.com/QingZhang1001/research-assistant-agent.git 
cd research-assistant-agent
```
2. Add your API key
Create .env in project root:
```plaintext
API_KEY=your_google_api_key
```
## ▶️ Run the Multi-agent System
```python
uv run python -m main
```

The research assistant stats:
```bash
🦉 I am your private research assistant. 
We will first agree on search keywords, then retrieve papers from arXiv.
Type 'exit' to end the conversation.
```

Example interactions:
```bash
Step 1: Please briefly describe your research topic.
You > I would like to know more about how machine learning applied on 3D genom   
🔎 Keywords Agent is analyzing your query...

🦉 Keywords Agent > Here are a few keywords for your search:

1.  3D genomics
2.  Machine learning genomics
3.  3D genome computational analysis
4.  AI in 3D genomics

Would you like to search with these keywords?

You (keyword refinement) > Machine learning genomics.

🦉 Keywords Agent > OK. The confirmed keyword is "Machine learning genomics".

🦉 Keywords Agent > FINAL KEYWORDS: Machine learning genomics

✅ Confirmed keywords: Machine learning genomics
Step 2: I will now retrieve papers from arXiv using these keywords.

🦉 Retrieval Agent > I found 10 papers based on your keywords: "Machine learning genomics". Here is a summary:

1.  **Title:** Changing Data Sources in the Age of Machine Learning for Official Statistics
    **Authors:** Cedric De Boom, Michael Reusens
    **Published Year:** 2023
    **Abstract:** This paper overviews the risks associated with changing data sources in machine learning for official statistics, including technical effects like concept drift and bias, and offers precautionary measures to maintain data integrity and reliability.

2.  **Title:** DOME: Recommendations for supervised machine learning validation in biology
    **Authors:** Ian Walsh, Dmytro Fishman, Dario Garcia-Gasulla, Tiina Titma, Gianluca Pollastri, The ELIXIR Machine Learning focus group, Jen Harrow, Fotis E. Psomopoulos, Silvio C. E. Tosatto
    **Published Year:** 2020
    **Abstract:** This paper presents community-wide recommendations for validating supervised machine learning in biology, using the DOME framework (data, optimization, model, evaluation) to help researchers and readers better understand and assess the performance and limitations of ML methods.

    ......

Step 3: I can give you a summarize of these research and show you potential future directions, press 'Enter' to start.
Press Enter to continue, or type 'skip' to skip this step > 

🦉 Foresee Agent > The search results indicate that the initial query "Machine learning genomics" did not yield papers directly related to "3D genomics." The retrieved papers cover a range of machine learning applications and challenges, but not specifically in the context of 3D genome organization.

Here's a summary of the current research themes and observations from the provided abstracts:

## Current Research Themes
1.  **Data Integrity and Reliability:** Several papers touch upon the importance of data quality, changing data sources, and robust validation methods in machine learning. This is crucial for applications in official statistics and biology.
2.  **Model Interpretability and Explainability:** There's a growing interest in understanding how machine learning models make decisions, with research exploring physics-inspired approaches and methods for learning interpretable models from biological data (e.g., whole genome sequences).
3.  **Efficient Machine Learning Methods:** Papers discuss techniques for efficient approximation in large-scale machine learning and the use of learning curves for decision-making to optimize resource allocation.

......
```

## 🛠️ Project Structure

```plaintext
research_assistant_agent/
├── main.py                   # Unified entrypoint
├── core/
│   └── orchestrator.py       # Multi-agent workflow controller
├── agents/
│   ├── keywords_agent.py     # Extracts/negotiates keywords
│   ├── retrieval_agent.py    # arXiv paper search
│   └── foresee_agent.py      # Trend analysis & future research
├── observability/
│   └── metrics_plugin.py     # (Optional) custom metrics
├── .env                      # API key
└── research_assistant.log    # Logs
```

## 📈 Limitations & Future Work
This project was developed by a noob using free and publicly available tools, specifically **Gemini-2.5-flash-lite** and **arXiv API** as the external search API. While the system demonstrate the core concept of a multi-agent workflow, serveral important limitations remain.

### ⚠️ Limitations
* Keyword negotiation accuracy is untested.
* Paper ranking depands entirely on arXiv's API.
* Retrieval capped at 10 papers to avoid rate limits and HTTP errors, limiting trend analysis to a small sample.
* Analsysis based on abstracts only, limiting the depth of research analysis.
* Some planned agents were not build (e.g, MetadataAgent, Methodology Flowchart Agent) due to deadline constraints.
* CLI-only interface - no web UI yet.

### 🚀 Future improvements
* Conduct user testing for keyword extraction quality (Human-in-the-loop).
* Add custom relevance ranking.
* Retrieve largeer batches with caching and rate limiting.
* Add MetadataAgent + Methodology Flowchart Agent.
* Provide a Web UI (`Streamlit`/ `Gradio`/ `FastAPI`)
 

## 🙌 Acknowledgements
This project was developed as part of the   
**5-Day AI Agents Intensive Course with Google**.

Thanks to Goolge ADK contributions and open-source authors of `arxiv` and `google-genai`.

## 👥 Contributors
- **Qing Zhang** - Project developer
- **ChatGPT / Google ADK Agents** - Guidance and debugging

 
