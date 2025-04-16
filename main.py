from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from openai import OpenAI  # Updated import
import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request validation
class QueryRequest(BaseModel):
    prompt: str
    connection: dict

def create_dynamic_engine(conn: dict):
    try:
        db_url = (
            f"mysql+pymysql://{conn['user']}:{conn['password']}"
            f"@{conn['host']}:{conn['port']}/{conn['database']}"
        )
        return create_engine(db_url, pool_pre_ping=True)
    except Exception as e:
        raise ValueError(f"Invalid connection: {e}")

@app.post("/query")
async def query_db(request: QueryRequest):
    if not request.prompt or not request.connection:
        raise HTTPException(status_code=400, detail="Prompt or DB connection details missing")

    try:
        engine = create_dynamic_engine(request.connection)

        # Ask OpenAI to extract table names (updated syntax)
        table_names_resp = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract table names used in the prompt. Comma-separated, no explanation."},
                {"role": "user", "content": request.prompt}
            ]
        )
        tables = [t.strip() for t in table_names_resp.choices[0].message.content.split(",")]

        # Get schema from MySQL
        schema_parts = []
        with engine.begin() as conn:
            for table in tables:
                try:
                    rows = conn.execute(text(f"DESCRIBE {table}")).fetchall()
                    columns = [f"{row[0]} {row[1]}" for row in rows]
                    schema_parts.append(f"{table}({', '.join(columns)})")
                except SQLAlchemyError as e:
                    raise HTTPException(status_code=400, detail=f"Schema error for '{table}': {e}")

        schema = "\n".join(schema_parts)

        # Ask OpenAI to generate SQL using schema (updated syntax)
        system_prompt = f"""You are a MySQL expert.
Use the schema below to write a valid SQL query for the user's prompt.

{schema}

Return only the SQL query, nothing else.
"""

        sql_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.prompt}
            ]
        )

        sql = sql_response.choices[0].message.content.strip()

        # Execute the SQL query
        with engine.begin() as conn:
            result = conn.execute(text(sql))
            if sql.lower().startswith("select"):
                rows = [dict(row._mapping) for row in result]
                return {"sql": sql, "data": rows}
            return {"sql": sql, "message": f"{result.rowcount} rows affected."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
