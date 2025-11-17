import sqlite3
import pandas as pd
import os
from pathlib import Path
import uuid

from dotenv import load_dotenv

load_dotenv()

llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
UPLOAD_DIR = Path("data/user_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path("data/user_data.db")

def init_db():
    if not DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.close()

def save_uploaded_csv(file) -> str:
    """Save uploaded CSV and return file path."""
    file_id = str(uuid.uuid4())[:8]
    file_path = UPLOAD_DIR / f"{file_id}_{file.name}"
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    print(f"[DB] Saved upload: {file_path}")
    return str(file_path)

def get_create_table_sql(csv_path: str) -> str:
    """Send first 10 rows to LLM → get CREATE TABLE SQL."""
    df = pd.read_csv(csv_path)
    sample = df.head(10).to_csv(index=False)

    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model=llm_model, temperature=0)

    prompt = f"""
You are a SQL expert. Given this CSV sample, return a **valid SQLite CREATE TABLE** statement.
- Use appropriate column types: TEXT, INTEGER, REAL, DATE.
- Table name: `user_data`
- Do NOT include data, only schema.
- Do NOT add PRIMARY KEY unless obvious.

CSV sample (first 10 rows):

{sample}

Return ONLY the clean SQL !
"""
    response = llm.invoke(prompt)
    
    print('LLM RESPONSE ', response)

    sql = response.content.strip()
    if sql.lower().startswith("```"):
        sql = sql.split("```", 2)[1].strip()
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()
    print(f"[LLM] Generated CREATE TABLE:\n{sql}")
    return sql

def create_and_load_table(csv_path: str):
    """Create table from LLM SQL and insert all data."""
    df = pd.read_csv(csv_path)

    create_sql = get_create_table_sql(csv_path)

    dangerous = ["DROP TABLE", "DROP DATABASE", "DELETE", "UPDATE", "INSERT", "ALTER"]
    if any(k in create_sql.upper() for k in dangerous):
        raise ValueError("LLM returned unsafe SQL")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DROP TABLE IF EXISTS user_data")
        conn.execute(create_sql)
        df.to_sql("user_data", conn, index=False, if_exists="append")
        conn.commit()
        print(f"[DB] Table `user_data` created and loaded with {len(df)} rows")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user_data")
        rows = cur.fetchone()[0]
        cur.execute("PRAGMA table_info(user_data)")
        cols = [row[1] for row in cur.fetchall()]
        revenue = 0
        top_product = "N/A"
        for col in cols:
            try:
                cur.execute(f"SELECT SUM({col}) FROM user_data")
                revenue = cur.fetchone()[0] or 0
                if revenue:
                    break
            except:
                pass
        return {"rows": rows, "revenue": revenue, "top_product": top_product}
    except:
        return {"rows": 0, "revenue": 0, "top_product": "N/A"}
    finally:
        conn.close()

def safe_execute(sql: str) -> str:
    dangerous = ["DELETE", "DROP", "UPDATE", "INSERT", "CREATE", "ALTER"]
    if any(k in sql.upper() for k in dangerous):
        return "BLOCKED: Dangerous operation."
    try:
        print(f"[DB] Executing SQL:\n{sql}")
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        print(df)
        conn.close()
        return df.head(10).to_markdown(index=False, tablefmt="pipe")
    except Exception as e:
        return f"SQL ERROR: {e}"