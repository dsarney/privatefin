"""Prompt building and local LLM client layer.

Re-export the prompt builder and Ollama adapter used by the Streamlit UI.
"""

from .ollama_client import OllamaClient
from .prompt_builder import build_advisory_prompt
