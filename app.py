# -*- coding: utf-8 -*-
import os
import sqlite3
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

DB_PATH = "sales.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, description, amount, created_at FROM sales ORDER BY created_at DESC")
    rows = cur.fetchall()
    total = sum(row["amount"] for row in rows)
    conn.close()

    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Sales Tracker</title>
        <style>
            body {{font-family: Arial, sans-serif; margin:0; padding:0; background:#f4f4f4;}}
            .container {{max-width: 800px; margin: auto; padding: 20px; background:#fff; box-shadow:0 0 10px rgba(0,0,0,0.1);}}
            h1 {{text-align:center;}}
            form {{display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px;}}
            input[type=text], input[type=number] {{flex:1; padding:8px; border:1px solid #ccc; border-radius:4px;}}
            button {{padding:10px 20px; background:#28a745; color:#fff; border:none; border-radius:4px; cursor:pointer;}}
            button:hover {{background:#218838;}}
            table {{width:100%; border-collapse:collapse; margin-top:20px;}}
            th, td {{padding:12px; border:1px solid #ddd; text-align:left;}}
            th {{background:#f8f8f8;}}
            @media (max-width:600px) {{
                form {{flex-direction:column;}}
                input[type=text], input[type=number] {{width:100%;}}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Daily Sales Tracker</h1>
            <form action="/add-sale" method="post">
                <input type="text" name="description" placeholder="Description" required>
                <input type="number" step="0.01" name="amount" placeholder="Amount" required>
                <button type="submit">Add Sale</button>
            </form>
            <h2>Sales List</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
    """
    for row in rows:
        html += f"""
                    <tr>
                        <td>{row["id"]}</td>
                        <td>{row["description"]}</td>
                        <td>${row["amount"]:.2f}</td>
                        <td>{row["created_at"]}</td>
                    </tr>
        """
    html += f"""
                </tbody>
            </table>
            <h3>Total: ${total:.2f}</h3>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/add-sale")
def add_sale(description: str = Form(...), amount: float = Form(...)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sales (description, amount) VALUES (?, ?)",
        (description, amount)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import os, uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))))