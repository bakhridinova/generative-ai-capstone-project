# agent.py  ← FINAL, NO MORE TABULATE ERRORS EVER
import os
import openai
import json
import sqlite3
import pandas as pd
import base64
from io import BytesIO
import plotly.express as px
from db import safe_execute, DB_PATH
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import base64
from io import BytesIO

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

def get_table_context() -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(user_data)")
        cols = [f"{row[1]} ({row[2]})" for row in cur.fetchall()]
        schema = ", ".join(cols)
        sample = pd.read_sql_query("SELECT * FROM user_data LIMIT 5", conn)
        conn.close()
        return f"Table: user_data\nColumns: {schema}\n\nSample rows:\n{sample.to_string(index=False)}"
    except Exception as e:
        return "No data loaded yet."

TABLE_CONTEXT = get_table_context()

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Run a safe SELECT query on user_data and return results as markdown table.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_chart",
            "description": "Generate a bar chart from a markdown table.",
            "parameters": {
                "type": "object",
                "properties": {"markdown_table": {"type": "string"}},
                "required": ["markdown_table"]
            }
        }
    }
]

def get_answer(user_question: str) -> str:
    print(f"\n[AGENT] Question: {user_question}")
    print(TABLE_CONTEXT)

    messages = [
            {
                "role": "system",
                "content": f"""You are an expert data analyst.
    Use the EXACT column names from the schema below.
    NEVER guess column names.
    NEVER write INSERT, UPDATE, DELETE, DROP, or CREATE.
    Only use SELECT queries.

    {TABLE_CONTEXT}

    Answer in clear, natural English. If showing data, summarize it nicely.
    Use the tools when needed."""
            },
            {"role": "user", "content": user_question}
        ]

    for _ in range(4):
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            # temperature=0
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            answer = msg.content or "No answer."
            print(f"[AGENT] Final answer:\n{answer}")
            return answer

        for tool in msg.tool_calls:
            name = tool.function.name
            args = json.loads(tool.function.arguments)

            print(f"[TOOL] Calling {name} with args: {args}")

            if name == "run_sql":
                result = safe_execute(args["query"])
                print(f"[TOOL] {name} result:\n{result}")
            elif name == "make_chart":
                try:
                    from io import StringIO
                    table_str = args["markdown_table"].strip()

                    df = pd.read_csv(StringIO(table_str), sep="|", skiprows=1, engine="python")
                    df = df.dropna(axis=1, how='all')
                    df = df.iloc[:-1]
                    df.columns = [c.strip() for c in df.columns]

                    num_col = df.select_dtypes(include="number").columns[0]
                    cat_col = df.columns[0] if df.columns[0] != num_col else df.columns[1]

                    import matplotlib.pyplot as plt
                    plt.figure(figsize=(11, 6))
                    bars = plt.bar(df[cat_col].astype(str), df[num_col], color="#1f77b4")
                    plt.title(f"{num_col} by {cat_col}", fontsize=16, pad=20)
                    plt.xlabel(cat_col, fontsize=12)
                    plt.ylabel(num_col, fontsize=12)
                    plt.xticks(rotation=45, ha="right")
                    plt.grid(axis='y', alpha=0.3)
                    plt.tight_layout()

                    buf = BytesIO()
                    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
                    plt.close()
                    img_b64 = base64.b64encode(buf.getvalue()).decode()

                    result = f"data:image/png;base64,{img_b64}"

                    print("[TOOL] make_chart → pure base64 image returned")
                    return result
                except Exception as e:
                    result = f"Chart error: {e}"
            else:
                result = "Unknown tool."


            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "name": name,
                "content": result
            })

    return "I couldn't answer in 4 steps. Try a simpler question."