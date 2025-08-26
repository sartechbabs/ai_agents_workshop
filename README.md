# AI Agent Workshop (Codespaces + Streamlit)

Build a minimal tool-using AI agent in **1.5 hours**, no local installs.

## ✨ Quick start (Codespaces)

1. **Use this template** → create your repo → click **Code ▸ Codespaces ▸ Create codespace on version_basic**.
2. Wait for the container to build (auto-installs requirements).
3. Add your key: in terminal `echo "LLM_API_KEY=YOUR_KEY" >> .env`
   - Optional: also set `LLM_BASE_URL` and `LLM_MODEL` (OpenAI-compatible).
4. Run the app:
   ```bash
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
