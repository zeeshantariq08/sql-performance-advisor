# 🚀 SQL Query Optimizer & Performance Advisor

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-ready-green.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

A **developer-focused SQL performance analyzer** that helps you:

- Detect common query issues  
- Score query efficiency using PostgreSQL `EXPLAIN ANALYZE`  
- Get optimization suggestions  
- (Optionally) receive AI-powered explanations  

Built for backend developers, database engineers, and anyone who wants faster SQL.

---

## ✨ Features

- Static SQL analysis (no database connection needed)  
- Performance scoring based on real `EXPLAIN ANALYZE` output  
- Detects common anti-patterns:
  - `SELECT *` usage  
  - Missing `WHERE` clause  
  - Potentially expensive / risky `JOIN`s  
  - Missing or inadequate indexes  
  - Non-SARGable expressions (`DATE()`, `YEAR()`, `UPPER(column)`, etc.)  
- Generates rewritten / optimized SQL versions  
- Clear before/after query diff view  
- Overall performance score (0–100)  
- Optional AI explanations (Google Gemini)  
- CLI interface + REST API (FastAPI)  
- Windows / Linux / macOS compatible  

---

## 📊 Example Output

```text
📊 Overall Query Score: 62 / 100

⚠ NON_SARGABLE_CONDITION
  Severity: MEDIUM
  Why:      Non-SARGable condition on orders.created_at
  Fix:      created_at BETWEEN '2025-12-18 00:00:00' AND '2025-12-18 23:59:59'

⚠ INDEX_SUGGESTION
  Severity: LOW
  Why:      Consider adding an index on orders.created_at
  Fix:      CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### Scoring Guide

Starts with 100 points. Points are deducted according to severity of detected problems and `EXPLAIN ANALYZE` metrics.

| Issue Detected          | Penalty |
| ----------------------- | ------- |
| Sequential Scan         | -25     |
| Slow Execution (>500ms) | -20     |
| Bad row estimates       | -20     |
| Nested Loop joins       | -15     |
| Full table scan risk    | -15     |

**Interpretation:**  
- 🟢 85–100 → Excellent  
- 🟡 60–84  → Needs improvement  
- 🔴 < 60  → High optimization priority  

---

## 🛠 Installation

```bash
# 1. Clone repository
git clone https://github.com/your-username/sql-query-optimizer.git
cd sql-query-optimizer

# 2. Create & activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ CLI Usage

```bash
python main.py
```

The tool will guide you through:

- Entering your SQL query  
- (Optional) Pasting `EXPLAIN ANALYZE` result  
- Enabling/disabling AI explanations  

### 🔍 Query Diff Example

```diff
- WHERE DATE(created_at) = '2025-12-18'
+ WHERE created_at BETWEEN '2025-12-18 00:00:00'
+ AND '2025-12-18 23:59:59'
```

---

## 🌐 REST API (FastAPI)

Start the server:

```bash
uvicorn app.api:app --reload
```

Interactive documentation:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

Example request:

```json
POST /analyze
{
  "query": "SELECT * FROM orders WHERE DATE(created_at) = '2025-12-18'",
  "ai": false
}
```

---

## 🤖 AI Explanations (Optional)

Powered by **Google Gemini**.  

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

> AI explanations are disabled by default — you can safely ignore this feature.

---

## 📄 License

MIT License © 2025  

---

## ⭐ Support the Project

If this tool helps you write faster queries, please consider giving the repository a star!  
It really makes a difference. ⭐  
