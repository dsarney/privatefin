"""Small adapter around the Ollama SDK used for local LLM inference.

Keeping this boundary behind a class prevents Ollama-specific response formats and
connection errors from leaking into the Streamlit orchestration layer.
"""

from __future__ import annotations

from dataclasses import dataclass

import ollama


@dataclass
class OllamaClient:
    """Connect to one Ollama model served on the local loopback interface.

    Attributes:
        model: Ollama model tag used for generation.
        host: Ollama API address.  The default loopback URL is the basis of
            PrivateFin's local-inference privacy boundary.
    """

    model: str = "llama3"
    host: str = "http://localhost:11434"

    def is_available(self) -> bool:
        """Return whether the configured Ollama server responds to a health probe."""
        try:
            # Listing installed models verifies server reachability and protocol health
            # without spending time or resources generating text.
            client = ollama.Client(host=self.host)
            client.list()
            return True
        except Exception:
            return False

    def generate(self, user_prompt: str, system_prompt: str | None = None) -> str:
        """Generate one response using explicit system and user chat roles.

        Raises:
            RuntimeError: If Ollama cannot be reached or generation fails.
        """
        # Explicit roles keep behavioural instructions separate from request evidence.
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        try:
            client = ollama.Client(host=self.host)
            response = client.chat(model=self.model, messages=messages)
        except Exception as exc:
            raise RuntimeError(
                "Ollama is unavailable. Start the local Ollama server and pull the selected model."
            ) from exc

        return self._extract_content(response)

    @staticmethod
    def _extract_content(response) -> str:
        """Extract text from both historical Ollama SDK response representations."""
        # Different SDK releases have returned mapping-like and object-like messages.
        # Supporting both avoids coupling the application to one minor client version.
        if isinstance(response, dict):
            message = response.get("message", {})
            if isinstance(message, dict):
                return str(message.get("content", ""))
            return str(getattr(message, "content", ""))

        message = getattr(response, "message", None)
        if message is None:
            return str(response)
        return str(getattr(message, "content", ""))
