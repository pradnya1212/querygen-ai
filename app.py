from flask import Flask, request, jsonify, render_template
import psycopg2
from google import genai

app = Flask(__name__)

# 🔑 Gemini API
client = genai.Client(api_key="AIzaSyBV6BlguVL4Uzmd3W55O6FgE3FYncdVuGA")

# 🗄️ DB
conn = psycopg2.connect(
    host="localhost",
    database="project_db",
    user="postgres",
    password="root"
)

#  AI RESPONSE (WITH FALLBACK SQL)
import time

def generate_ai_response(prompt):
    try:
        time.sleep(2)  # prevent rate limit

        res = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if res and res.text:
            return res.text.strip()

        return "AI returned empty response"

    except Exception as e:
        print("AI ERROR:", e)

        # 🔥 FALLBACK RESPONSE
        return "⚠️ AI busy. Showing smart result instead."

#  SMART AI AGENT
def smart_ai_agent(query):
    query_lower = query.lower()

    # 🔥 HARDCODE BACKUP (VERY IMPORTANT)
    if "show all employees" in query_lower:
        sql = "SELECT e.id, e.name, d.dept_name, e.salary FROM employees e JOIN departments d ON e.dept_id = d.dept_id;"
        msg = "Here are all employees 👇"

    elif "employees in it" in query_lower:
        sql = "SELECT e.id, e.name, d.dept_name, e.salary FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.dept_name='IT';"
        msg = "Here are employees from IT department 👇"

    elif "highest salary" in query_lower:
        sql = "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
        msg = "Here is the highest paid employee 👇"

    elif "salary above" in query_lower:
        sql = "SELECT * FROM employees WHERE salary > 60000;"
        msg = "Employees with salary above 60000 👇"

    else:
        # 🔥 AI fallback
        ai_response = generate_ai_response(query)

        if not ai_response:
            return {
                "type": "text",
                "message": "⚠️ AI not responding. Try database queries."
            }

        return {
            "type": "text",
            "message": ai_response
        }

    # 🔥 RUN SQL
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()

        return {
            "type": "sql",
            "query": sql,
            "data": data,
            "message": msg
        }

    except Exception as e:
        print("SQL ERROR:", e)
        return {
            "type": "text",
            "message": "❌ Database error"
        }
    # 🔥 RUN SQL SAFELY
    if sql:
        try:
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
        except Exception as e:
            print("SQL ERROR:", e)
            sql = None  # prevent crash

    return {
        "type": "smart",
        "query": sql,
        "data": data,
        "message": answer
    }

# 🌐 ROUTES
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask')
def ask():
    q = request.args.get('q')
    return jsonify(smart_ai_agent(q))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)