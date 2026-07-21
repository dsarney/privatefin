"""Minimal Streamlit entry point for PrivateFin.

Run with ``streamlit run app.py``.  Application behaviour lives in ``src.ui.app`` so
the project root remains a stable launch target without duplicating UI logic.
"""

from src.ui.app import main


if __name__ == "__main__":
    main()
