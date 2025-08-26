from duckduckgo_search import DDGS

def tool_calculate(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/(). ")
        if not set(expression) <= allowed:
            return "Error: only digits and + - * / ( ) allowed."
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def tool_web_search(query: str, max_results: int = 5) -> str:
    # Returns simple bullets with title + url; keeps it short for the model
    max_results = max(1, min(max_results, 10))
    out_lines = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = r.get("title", "").strip()
            href = r.get("href", "").strip()
            snippet = r.get("body", "").strip()
            out_lines.append(f"- {title} — {snippet[:140]}… ({href})")
    return "\n".join(out_lines) if out_lines else "No results."
