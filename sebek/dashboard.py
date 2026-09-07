"""SEBEK Dashboard - Streamlit UI for the Local Intelligence Engine.

Provides a web interface for:
- Real-time chat with RAG-augmented responses from Ollama
- Vector database status and file indexing metrics
- System health monitoring
- Direct command interface to SEBEK core

Usage:
    streamlit run -m sebek.dashboard
"""

import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

import streamlit as st
import requests

from sebek.config import Config
from sebek.utils.logging import get_logger, setup_root_logger
from sebek.utils.vectordb import initialize_vector_db, safe_similarity_search
from sebek.utils.errors import OllamaError, VectorDBError

# Setup logging
setup_root_logger()
logger = get_logger(__name__)

# Try to import vector DB
try:
    from langchain_community.vectorstores import Chroma
    HAS_MEMORY = True
except ImportError:
    HAS_MEMORY = False
    logger.warning("LangChain/Chroma not available - memory features disabled")


# ============================================================================
# Configuration & Initialization
# ============================================================================

def setup_page_config() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="SEBEK Command Center",
        page_icon="🦅",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = None
    if "master_map" not in st.session_state:
        st.session_state.master_map = {}


def load_master_map() -> Dict[str, Any]:
    """Load file index map from disk.

    Returns:
        dict: File index metadata, or empty dict if not found.
    """
    map_path = Path("sebek_master_map.json")
    if map_path.exists():
        try:
            with open(map_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load master map: {e}")
    return {}


def get_vector_db() -> Optional[Chroma]:
    """Get or initialize vector database.

    Returns:
        Chroma: Initialized vector store, or None if unavailable.
    """
    if st.session_state.vector_db is None:
        if HAS_MEMORY:
            try:
                st.session_state.vector_db = initialize_vector_db()
            except VectorDBError as e:
                logger.error(f"Vector DB initialization failed: {e}")
                return None
    return st.session_state.vector_db


# ============================================================================
# Ollama Integration
# ============================================================================

def query_sebek(prompt: str, retrieved_context: str = "") -> str:
    """Query SEBEK LLM with optional RAG context.

    Args:
        prompt: User query/command.
        retrieved_context: Optional context from vector DB retrieval.

    Returns:
        str: LLM response, or error message on failure.

    Raises:
        OllamaError: If Ollama API is unreachable.
    """
    total_files = st.session_state.master_map.get("total_files_across_all_territories", 0)
    system_context = f"System Context: You are SEBEK. You guard a vault with {total_files} files. "

    # Build full prompt with context
    full_prompt = system_context
    if retrieved_context:
        full_prompt += "\n--- RECALLED VAULT MEMORY ---\n" + retrieved_context
        full_prompt += "\n-----------------------------\n"
    full_prompt += "\nUser query: " + prompt

    payload = {
        "model": Config.ollama.chat_model,
        "prompt": full_prompt,
        "stream": False,
        "temperature": Config.ollama.temperature,
    }

    try:
        response = requests.post(
            f"{Config.ollama.url}/api/generate",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("response", "Error: No response from SEBEK.")
    except requests.exceptions.ConnectionError:
        raise OllamaError(
            f"Could not connect to SEBEK engine at {Config.ollama.url}. "
            "Is Ollama running?"
        )
    except requests.exceptions.Timeout:
        raise OllamaError("SEBEK engine request timed out. Try a simpler query.")
    except requests.exceptions.RequestException as e:
        raise OllamaError(f"SEBEK engine error: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        raise OllamaError(f"Invalid response from SEBEK engine: {e}")


# ============================================================================
# UI Components
# ============================================================================

def render_system_status() -> None:
    """Render system status indicators."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🦅 SEBEK Engine",
            value="ONLINE",
            delta="Operational",
        )

    with col2:
        st.metric(
            label="🔒 Network",
            value="SECURE",
            delta="Local Only",
        )

    with col3:
        total_files = st.session_state.master_map.get(
            "total_files_across_all_territories", 0
        )
        st.metric(
            label="📁 Files Indexed",
            value=total_files,
        )

    with col4:
        memory_status = "ONLINE" if st.session_state.vector_db else "OFFLINE"
        st.metric(
            label="🧠 Long-Term Memory",
            value=memory_status,
        )


def render_comms_link() -> None:
    """Render chat interface tab."""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💬 Direct Interface")
        st.write("Send commands or queries to SEBEK")

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        if prompt := st.chat_input("Enter command or query for SEBEK..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Retrieve context from vector DB
            retrieved_context = ""
            vector_db = get_vector_db()
            if vector_db:
                try:
                    results = safe_similarity_search(
                        vector_db,
                        prompt,
                        k=Config.vectordb.similarity_k,
                        logger_instance=logger,
                        max_chars=Config.vectordb.max_query_chars,
                    )
                    if results:
                        retrieved_context = "\n".join(
                            [result.page_content for result in results]
                        )
                except Exception as e:
                    logger.warning(f"Failed to retrieve context: {e}")
            else:
                logger.debug("Vector DB not available for context retrieval")

            # Query SEBEK
            try:
                sebek_reply = query_sebek(prompt, retrieved_context)
                with st.chat_message("assistant"):
                    st.markdown(sebek_reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": sebek_reply}
                )
            except OllamaError as e:
                error_msg = f"⚠️ {str(e)}"
                with st.chat_message("assistant"):
                    st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
                logger.error(f"Query failed: {e}")

    with col2:
        st.subheader("🔧 System Status")
        render_system_status()


def render_vault_explorer() -> None:
    """Render vault explorer tab."""
    st.subheader("🗄️ Vault Explorer")

    st.write("View information about indexed documents and memory status.")

    if st.session_state.vector_db:
        col1, col2 = st.columns(2)

        with col1:
            st.info("✅ Vector Database: ONLINE")
            st.caption(
                f"Location: {Config.vectordb.db_dir}\n"
                f"Model: {Config.ollama.embedding_model}"
            )

        with col2:
            st.success("✅ Long-Term Memory: ACTIVE")
            st.caption(
                f"Chunks: {Config.vectordb.chunk_size} chars\n"
                f"Retrieval: Top {Config.vectordb.similarity_k} similar"
            )
    else:
        st.warning("⚠️ Vector Database not available. Memory features disabled.")
        st.caption(
            "To enable memory:\n"
            f"1. Ensure Chroma is installed\n"
            f"2. Ingest documents using: python -m sebek.ingestion_cli\n"
            f"3. Restart this app"
        )

    st.divider()

    # File index info
    st.subheader("📊 Indexed Files")
    total_files = st.session_state.master_map.get(
        "total_files_across_all_territories", 0
    )
    st.metric("Total Files", total_files)

    if st.session_state.master_map:
        with st.expander("View Index Metadata"):
            st.json(st.session_state.master_map)


# ============================================================================
# Main App
# ============================================================================

def main() -> None:
    """Main Streamlit application."""
    # Setup
    setup_page_config()
    initialize_session_state()

    # Load configuration and data
    st.session_state.master_map = load_master_map()

    # Header
    st.title("🦅 SEBEK Local Intelligence Engine")
    st.markdown("### Digital Sovereign Operating System (DSOS) - Control Interface")

    # Tabs
    tab1, tab2 = st.tabs(["💬 Comms Link", "🗄️ Vault Explorer"])

    with tab1:
        render_comms_link()

    with tab2:
        render_vault_explorer()

    # Footer
    st.divider()
    st.caption(
        "SEBEK v0.1.0 | "
        "[GitHub](https://github.com/rfd-core/rfd-sovereign-stack) | "
        "[Docs](https://github.com/rfd-core/rfd-sovereign-stack/docs)"
    )


if __name__ == "__main__":
    main()
