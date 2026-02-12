# Agents - Legal Team
import os
import streamlit as st
import tempfile
from openai import OpenAI
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.chunking.document import DocumentChunking

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL_ID = "qwen/qwen3-coder"
OPENROUTER_EMBEDDING_MODEL_ID = "openai/text-embedding-3-small"
OPENROUTER_API_KEY = "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"

api_key = OPENROUTER_API_KEY
os.environ["OPENROUTER_API_KEY"] = api_key
os.environ["OPENAI_API_KEY"] = api_key


def is_openrouter_auth_error(error: Exception) -> bool:
    error_text = str(error).lower()
    return "failed to authenticate request with clerk" in error_text or "authentication" in error_text


def validate_openrouter_embedding_access(api_key: str) -> tuple[bool, str]:
    try:
        client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        client.embeddings.create(
            model=OPENROUTER_EMBEDDING_MODEL_ID,
            input="auth-check",
            dimensions=1536,
        )
        return True, ""
    except Exception as e:
        if is_openrouter_auth_error(e):
            return False, "OpenRouter authentication failed (502 Clerk). Check key/credits and retry."
        return False, str(e)

# Initialize Streamlit
# Customizing the page title and header
st.set_page_config(page_title="AI Legal Team Agents", page_icon="⚖️", layout="wide")

# Title with emojis for visual appeal
st.markdown("<h1 style='text-align: center; color: #3e8e41;'>👨‍⚖️ AI Legal Team Agents</h1>", unsafe_allow_html=True)

# Adding a short, stylish description with a bit of color
st.markdown("""
    <div style='text-align: center; font-size: 18px; color: #4B0082;'>
        Upload your legal document and let the <b>AI LegalAdvisor</b>, <b>AI ContractsAnalyst</b>, 
        <b>AI LegalStrategist</b>, and <b>AI Team Lead</b> do the work for you. You can also ask 
        questions in between for enhanced collaboration and insights.
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "vector_db" not in st.session_state:
    st.session_state.vector_db = LanceDb(
        table_name="law",
        uri="tmp/lancedb",
        embedder=OpenAIEmbedder(
            id=OPENROUTER_EMBEDDING_MODEL_ID,
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
        ),
    )

if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = None

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

if "validated_api_key" not in st.session_state:
    st.session_state.validated_api_key = ""

# Sidebar for API Config & File Upload
with st.sidebar:

    # Set a title for the sidebar
    st.header("Configuration")
    st.success("OpenRouter API key configured.")


    chunk_size_in = st.sidebar.number_input("Chunk Size", min_value=1, max_value=5000, value=1000)
    overlap_in = st.sidebar.number_input("Overlap", min_value=1, max_value=1000, value=200)

    st.header("📄 Document Upload")

    uploaded_file = st.file_uploader("Upload a Legal Document (PDF)", type=["pdf"])
    
    if uploaded_file:
        if uploaded_file.name not in st.session_state.processed_files:
            with st.spinner("Processing document..."):
                try:
                    if not api_key:
                        st.error("Please enter your OpenRouter API key before uploading a file.")
                        st.stop()

                    if st.session_state.validated_api_key != api_key:
                        is_valid_key, validation_message = validate_openrouter_embedding_access(api_key)
                        if not is_valid_key:
                            st.error(validation_message)
                            st.stop()
                        st.session_state.validated_api_key = api_key

                    # Save to a temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_path = temp_file.name
                    
                    # Process the uploaded document into knowledge base
                    if st.session_state.vector_db.exists():
                        st.session_state.vector_db.drop()
                    st.session_state.vector_db.create()

                    st.session_state.knowledge_base = Knowledge(
                        vector_db=st.session_state.vector_db
                    )
                    st.session_state.knowledge_base.insert(
                        path=temp_path,
                        reader=PDFReader(
                            chunking_strategy=DocumentChunking(chunk_size=chunk_size_in, overlap=overlap_in)
                        ),
                        upsert=True,
                    )
                    st.session_state.processed_files.add(uploaded_file.name)

                    st.success("✅ Document processed and stored in knowledge base!")

                except Exception as e:
                    if is_openrouter_auth_error(e):
                        st.error(
                            "OpenRouter authentication failed during document processing. "
                            "Verify key/credits and try again."
                        )
                    else:
                        st.error(f"Error processing document: {e}")
                    
# Initialize AI Agents (After Document Upload)
if st.session_state.knowledge_base:
    legal_researcher = Agent(
        name="LegalAdvisor",
        model=OpenRouter(id=OPENROUTER_MODEL_ID, api_key=api_key),
        knowledge=st.session_state.knowledge_base,
        search_knowledge=True,
        description="Legal Researcher AI - Finds and cites relevant legal cases, regulations, and precedents using all data in the knowledge base.",
        instructions=[
        "Extract all available data from the knowledge base and search for legal cases, regulations, and citations.",
        "If needed, use DuckDuckGo for additional legal references.",
        "Always provide source references in your answers."
        ],  
        tools=[DuckDuckGoTools()],
        markdown=True
    )

    contract_analyst = Agent(
        name="ContractAnalyst",
        model=OpenRouter(id=OPENROUTER_MODEL_ID, api_key=api_key),
        knowledge=st.session_state.knowledge_base,
        search_knowledge=True,
        description="Contract Analyst AI - Reviews contracts and identifies key clauses, risks, and obligations using the full document data.",
        instructions=[
            "Extract all available data from the knowledge base and analyze the contract for key clauses, obligations, and potential ambiguities.",
            "Reference specific sections of the contract where possible."
        ],
        markdown=True
    )

    legal_strategist = Agent(
        name="LegalStrategist",
        model=OpenRouter(id=OPENROUTER_MODEL_ID, api_key=api_key),
        knowledge=st.session_state.knowledge_base,
        search_knowledge=True,
        description="Legal Strategist AI - Provides comprehensive risk assessment and strategic recommendations based on all the available data from the contract.",
        instructions=[
            "Using all data from the knowledge base, assess the contract for legal risks and opportunities.",
            "Provide actionable recommendations and ensure compliance with applicable laws."
        ],
        markdown=True
    )

    team_lead = Agent(
        name="teamlead",
        model=OpenRouter(id=OPENROUTER_MODEL_ID, api_key=api_key),
        description="Team Lead AI - Integrates responses from the Legal Researcher, Contract Analyst, and Legal Strategist into a comprehensive report.",
        instructions=[
            "Combine and summarize all insights provided by the Legal Researcher, Contract Analyst, and Legal Strategist. "
            "Ensure the final report includes references to all relevant sections from the document."
        ],
        markdown=True
    )

    def get_team_response(query):
        research_response = legal_researcher.run(query)
        contract_response = contract_analyst.run(query)
        strategy_response = legal_strategist.run(query)

        final_response = team_lead.run(
        f"Summarize and integrate the following insights gathered using the full contract data:\n\n"
        f"Legal Researcher:\n{research_response}\n\n"
        f"Contract Analyst:\n{contract_response}\n\n"
        f"Legal Strategist:\n{strategy_response}\n\n"
        "Provide a structured legal analysis report that includes key terms, obligations, risks, and recommendations, with references to the document."
        )
        return final_response

# Analysis Options
if st.session_state.knowledge_base:
    st.header("🔍 Select Analysis Type")
    analysis_type = st.selectbox(
        "Choose Analysis Type:",
        ["Contract Review", "Legal Research", "Risk Assessment", "Compliance Check", "Custom Query"]
    )

    query = None
    if analysis_type == "Custom Query":
        query = st.text_area("Enter your custom legal question:")
    else:
        predefined_queries = {
            "Contract Review": (
                "Analyze this document, contract, or agreement using all available data from the knowledge base. "
                "Identify key terms, obligations, and risks in detail."
            ),
            "Legal Research": (
                "Using all available data from the knowledge base, find relevant legal cases and precedents related to this document, contract, or agreement. "
                "Provide detailed references and sources."
            ),
            "Risk Assessment": (
                "Extract all data from the knowledge base and identify potential legal risks in this document, contract, or agreement. "
                "Detail specific risk areas and reference sections of the text."
            ),
            "Compliance Check": (
                "Evaluate this document, contract, or agreement for compliance with legal regulations using all available data from the knowledge base. "
                "Highlight any areas of concern and suggest corrective actions."
            )
        }
        query = predefined_queries[analysis_type]

    if st.button("Analyze"):
        if not query:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    response = get_team_response(query)
                except Exception as e:
                    if is_openrouter_auth_error(e):
                        st.error(
                            "OpenRouter authentication failed (502 Clerk). Verify your API key, "
                            "account credits, and try again in a minute."
                        )
                    else:
                        st.error(f"Analysis failed: {e}")
                    st.stop()

                # Display results using Tabs
                tabs = st.tabs(["Analysis", "Key Points", "Recommendations"])

                with tabs[0]:
                    st.subheader("📑 Detailed Analysis")
                    st.markdown(response.content if response.content else "No response generated.")

                with tabs[1]:
                    st.subheader("📌 Key Points Summary")
                    key_points_response = team_lead.run(
                        f"Summarize the key legal points from this analysis:\n{response.content}"
                    )
                    st.markdown(key_points_response.content if key_points_response.content else "No summary generated.")

                with tabs[2]:
                    st.subheader("📋 Recommendations")
                    recommendations_response = team_lead.run(
                        f"Provide specific legal recommendations based on this analysis:\n{response.content}"
                    )
                    st.markdown(recommendations_response.content if recommendations_response.content else "No recommendations generated.")

# Sticky footer credits
st.markdown(
    """
    <style>
      [data-testid="stAppViewContainer"] .main .block-container {
        padding-bottom: 4rem;
      }
      .sticky-footer {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100%;
        font-size: 14px;
        color: #666;
        background: rgba(255, 255, 255, 0.95);
        border-top: 1px solid #e5e7eb;
        padding: 8px 12px;
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
      }
      .sticky-footer-content {
        width: min(900px, 100%);
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        transform: translateX(15%);
      }
      .footer-links {
        display: flex;
        justify-content: center;
        gap: 10px;
      }
      .sticky-footer a {
        color: #1d4ed8;
        text-decoration: none;
      }
      .sticky-footer a:hover {
        text-decoration: underline;
      }
    </style>
    <div class="sticky-footer">
      <div class="sticky-footer-content">
        <div>Designed and devloped by <b>anurag</b></div>
        <div class="footer-links">
          <a href="https://github.com/anurag-m1" target="_blank">GitHub</a>
          <span>|</span>
          <a href="https://instagram.com/ca_anuragsingh" target="_blank">Instagram</a>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
