import os, json, importlib
import streamlit as st
from agent import SYSTEM, build_tools, call_model, continue_with_tool_results

tools_module = importlib.import_module("tools")

MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

st.set_page_config(
    page_title="AI Agent Workshop",
    page_icon="🧭",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🧭 AI Agent Workshop</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Interactive AI Agent with Advanced Tools and Capabilities</p>", unsafe_allow_html=True)

# Add a info box with tips
st.info("💡 **Tips:** You can ask the agent to perform calculations, search the web, or help you with learning plans. Try different prompts to explore its capabilities!")

with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/docs/main/public/images/brand/streamlit-mark-color.png", width=100)
    st.subheader("⚙️ Agent Settings")
    
    with st.expander("Model Configuration", expanded=True):
        model = st.text_input("🤖 Model", MODEL)
        temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.2, 0.1,
                              help="Higher values make the output more random, lower values more deterministic")
    
    with st.expander("Environment Setup", expanded=False):
        st.markdown("**Required Environment Variables:**")
        st.code("LLM_API_KEY", language="bash")
        st.markdown("**Optional Variables:**")
        st.code("LLM_BASE_URL\nLLM_MODEL", language="bash")
    
    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    st.metric("Queries Made", st.session_state.query_count)

# Create two columns for the main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🤔 What would you like the agent to do?")
    prompt = st.text_area(
        "Enter your prompt",
        "Plan 3 steps to learn GenAI safely and compute 2*(10+5). Also search 'responsible AI checklist'.",
        height=100
    )

    # Example prompts in an expander
    with st.expander("✨ Example Prompts"):
        st.markdown("""
        - Calculate the compound interest on $1000 for 5 years at 5% interest rate
        - Search for best practices in responsible AI development
        - Create a learning plan for machine learning beginners
        """)

with col2:
    st.markdown("### ⚡ Actions")
    run_button = st.button("🚀 Run Agent", use_container_width=True)
    
    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.query_count = 0
        st.experimental_rerun()

if run_button:
    # Increment query counter
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    st.session_state.query_count += 1
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

        # Create a container for the response
        response_container = st.container()
        
        with response_container:
            st.markdown("### 🤖 Agent Response")
            
            # Show thinking process
            with st.expander("🔍 Agent Thought Process", expanded=False):
                st.write("Tool calls made:", len(tool_calls))
                for call in tool_calls:
                    st.code(f"Tool: {call.function.name}\nArgs: {call.function.arguments}", language="json")
            
            # Show final response
            if tool_results_msgs:
                final_msgs = messages + [choice.message] + tool_results_msgs
                final = continue_with_tool_results(final_msgs, model=model, temperature=temperature)
                st.markdown("#### Response:")
                st.markdown(final.choices[0].message.content)
            else:
                st.markdown("#### Response:")
                st.markdown(choice.message.content)
            
            # Add timestamp
            st.caption(f"Response generated at {st.session_state.get('last_run_time', '')}")
