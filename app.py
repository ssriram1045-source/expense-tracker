import sqlite3
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            spent_on TEXT DEFAULT (date('now'))
        )
    """)
    conn.commit()
    conn.close()

PAGE = """
<h1>Expense Tracker</h1>

<h3>Add Expense</h3>
<form method="POST" action="/add">
  <input name="title" placeholder="What did you spend on?" required>
  <select name="category">
    <option>Food</option>
    <option>Travel</option>
    <option>Shopping</option>
    <option>Bills</option>
    <option>Other</option>
  </select>
  <input name="amount" type="number" step="0.01" placeholder="Amount" required>
  <button type="submit">Add</button>
</form>

<h3>Spending by Category</h3>
<table border="1" cellpadding="8">
  <tr><th>Category</th><th>Total</th></tr>
  {% for t in totals %}
  <tr>
    <td>{{ t['category'] }}</td>
    <td>{{ t['total'] }}</td>
  </tr>
  {% else %}
  <tr><td colspan="2">No data yet</td></tr>
  {% endfor %}
</table>
<p><b>Grand Total: {{ grand_total }}</b></p>

<h3>All Expenses</h3>
<table border="1" cellpadding="8">
  <tr><th>ID</th><th>Title</th><th>Category</th><th>Amount</th><th>Date</th><th>Action</th></tr>
  {% for e in expenses %}
  <tr>
    <td>{{ e['id'] }}</td>
    <td>{{ e['title'] }}</td>
    <td>{{ e['category'] }}</td>
    <td>{{ e['amount'] }}</td>
    <td>{{ e['spent_on'] }}</td>
    <td>
      <form method="POST" action="/delete/{{ e['id'] }}" style="display:inline">
        <button type="submit">Delete</button>
      </form>
    </td>
  </tr>
  {% else %}
  <tr><td colspan="6">No expenses yet</td></tr>
  {% endfor %}
</table>
"""

@app.route("/")
def home():
    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    totals = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "GROUP BY category ORDER BY total DESC"
    ).fetchall()
    grand_total = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses"
    ).fetchone()[0]
    conn.close()
    return render_template_string(
        PAGE, expenses=expenses, totals=totals, grand_total=grand_total
    )

@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (title, category, amount) VALUES (?, ?, ?)",
        (request.form["title"], request.form["category"], request.form["amount"]),
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)