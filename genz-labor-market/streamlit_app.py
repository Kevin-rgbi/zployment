"""Streamlit entrypoint.

Run:
  streamlit run streamlit_app.py

This delegates to dashboard/app.py.
"""

from dashboard.app import main


if __name__ == "__main__":
    main()
