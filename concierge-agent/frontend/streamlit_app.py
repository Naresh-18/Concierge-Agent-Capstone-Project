# frontend/streamlit_app.py

import streamlit as st
import requests

st.set_page_config(page_title="Concierge Agent Demo")
st.title("🧠 Concierge Agent Demo")

if "session_id" not in st.session_state:
    st.session_state.session_id = None

query = st.text_area(
    "Ask the concierge (e.g., plan a healthy vegetarian dinner for 4 with a shopping list)"
)

if st.button("Send"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        payload = {
            "session_id": st.session_state.session_id,
            "query": query,
        }
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/ask",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            out = resp.json()
            st.session_state.session_id = out.get("session_id")

            # -------- Pretty Plan --------
            st.subheader("🗺️ Plan (Steps)")
            plan = out.get("plan", [])
            if plan:
                for i, step in enumerate(plan, start=1):
                    desc = step.get("description", "")
                    st.markdown(f"{i}. {desc}")
            else:
                st.write("No plan returned.")

            # -------- Combined Shopping List --------
            st.subheader("🛒 Suggested Shopping List")
            items = set()
            for r in out.get("results", []):
                result = r.get("result", {})
                # From ShoppingTool
                if isinstance(result.get("items"), list):
                    for it in result["items"]:
                        items.add(it)
                # From RecipeTool
                if "recipe" in result:
                    for it in result["recipe"].get("ingredients", []):
                        items.add(it)

            if items:
                for it in sorted(items):
                    st.markdown(f"- {it}")
            else:
                st.write("No shopping items extracted.")

            # -------- Raw JSON (optional) --------
            with st.expander("🔍 Raw JSON (debug)"):
                st.json(out)

        except requests.exceptions.RequestException as e:
            st.error(f"Error contacting backend: {e}")
