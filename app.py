import os, json, importlib
import streamlit as st
from agent import SYSTEM, build_tools, call_model, continue_with_tool_results

tools_module = importlib.import_module("tools")

MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

st.set_page_config(page_title="AI Agent Workshop", page_icon="🧭")
st.title("🧭 Minimal AI Agent")
st.caption("Model‑tool loop with Streamlit UI (deployable to HF Spaces or Streamlit Cloud).")

with st.sidebar:
    st.subheader("Settings")
    model = st.text_input("Model", MODEL)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
    st.markdown("---")
    st.markdown("**Env needed:** `LLM_API_KEY` (and optionally `LLM_BASE_URL`, `LLM_MODEL`).")

prompt = st.text_input(
    "What should the agent do?",
    "Plan 3 steps to learn GenAI safely and compute 2*(10+5). Also search 'responsible AI checklist'."
)

if st.button("Run"):
    with st.spinner("Thinking…"):
        tools = build_tools()
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ]
        resp = call_model(messages, tools, model=model, temperature=temperature)
        choice = resp.choices[0]
        tool_calls = choice.message.tool_calls or []

        # Execute any requested tools
        tool_results_msgs = []
        for call in tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            if name == "tool_calculate":
                output = tools_module.tool_calculate(args.get("expression", ""))
            elif name == "tool_web_search":
                output = tools_module.tool_web_search(args.get("query", ""), int(args.get("max_results", 5)))
            else:
                output = f"Unknown tool: {name}"
            tool_results_msgs.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": name,
                "content": output
            })

        if tool_results_msgs:
            final_msgs = messages + [choice.message] + tool_results_msgs
            final = continue_with_tool_results(final_msgs, model=model, temperature=temperature)
            st.success(final.choices[0].message.content)
        else:
            st.success(choice.message.content)
