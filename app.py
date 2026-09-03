"""
BudgetBuddy - Personal Finance Manager
======================================

A Flask web application for tracking income and expenses, setting monthly
budgets, and visualizing spending habits through interactive charts.

Design note on tooling: Per CS50x final project requirements, I disclose that
AI-based coding assistants (large language model tools) were used as helpers to
aid in the design, implementation, and testing of this project. The overall
architecture, core functionality, and the essence of the work are my own; the
assistants were used to amplify productivity, generate boilerplate, and help
debug issues. No school problem solutions were obtained from such tools.
"""

import os
import csv
import io
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Response
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from helpers import login_required, usd, apologize, CURRENCIES

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if not os.path.exists("budgetbuddy.db"):
    import sqlite3
    conn = sqlite3.connect("budgetbuddy.db")
    conn.close()

db = SQL("sqlite:///budgetbuddy.db")


def init_db():
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL,
            currency TEXT DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            icon TEXT DEFAULT '📦',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            description TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            UNIQUE(user_id, category_id, month, year)
        )
    """)


init_db()


DEFAULT_CATEGORIES = [
    ("Salary", "income", "💰"),
    ("Freelance", "income", "💻"),
    ("Investments", "income", "📈"),
    ("Gifts", "income", "🎁"),
    ("Other Income", "income", "💵"),
    ("Food & Dining", "expense", "🍔"),
    ("Transportation", "expense", "🚗"),
    ("Housing", "expense", "🏠"),
    ("Utilities", "expense", "💡"),
    ("Entertainment", "expense", "🎬"),
    ("Shopping", "expense", "🛍️"),
    ("Health", "expense", "🏥"),
    ("Education", "expense", "📚"),
    ("Subscriptions", "expense", "📱"),
    ("Other Expense", "expense", "📦"),
]


def create_default_categories(user_id):
    for name, cat_type, icon in DEFAULT_CATEGORIES:
        db.execute(
            "INSERT INTO categories (user_id, name, type, icon) VALUES (?, ?, ?, ?)",
            user_id, name, cat_type, icon
        )


@app.before_request
def before_request():
    if "user_id" in session:
        session.permanent = True


@app.route("/")
@login_required
def index():
    return redirect("/dashboard")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apologize("must provide username", 400)
        if not password:
            return apologize("must provide password", 400)
        if password != confirmation:
            return apologize("passwords do not match", 400)
        if len(password) < 6:
            return apologize("password must be at least 6 characters", 400)

        existing = db.execute("SELECT id FROM users WHERE username = ?", username)
        if existing:
            return apologize("username already taken", 400)

        user_id = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username, generate_password_hash(password)
        )
        create_default_categories(user_id)

        session["user_id"] = user_id
        session["username"] = username
        session["currency"] = "USD"
        flash("Welcome to BudgetBuddy!")
        return redirect("/dashboard")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password")

        if not username:
            return apologize("must provide username", 400)
        if not password:
            return apologize("must provide password", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apologize("invalid username and/or password", 400)

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["currency"] = rows[0]["currency"] or "USD"
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    today = date.today()
    month = today.month
    year = today.year

    transactions = db.execute("""
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?
        ORDER BY t.date DESC, t.created_at DESC
    """, user_id, f"{month:02d}", str(year))

    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expenses

    all_time = db.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses
        FROM transactions WHERE user_id = ?
    """, user_id)

    overall_balance = all_time[0]["total_income"] - all_time[0]["total_expenses"]

    category_spending = db.execute("""
        SELECT c.name, c.icon, COALESCE(SUM(t.amount), 0) as total
        FROM categories c
        LEFT JOIN transactions t ON t.category_id = c.id
            AND t.type = 'expense'
            AND strftime('%m', t.date) = ?
            AND strftime('%Y', t.date) = ?
            AND t.user_id = ?
        WHERE c.user_id = ? AND c.type = 'expense'
        GROUP BY c.id
        HAVING total > 0
        ORDER BY total DESC
    """, f"{month:02d}", str(year), user_id, user_id)

    daily_spending = db.execute("""
        SELECT date, SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
            AND strftime('%Y', date) = ?
            AND strftime('%m', date) = ?
        GROUP BY date
        ORDER BY date
    """, user_id, str(year), f"{month:02d}")

    recent = transactions[:5]

    return render_template("dashboard.html",
        transactions=recent,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        overall_balance=overall_balance,
        category_spending=category_spending,
        daily_spending=daily_spending,
        month=today.strftime("%B %Y"),
        usd=usd
    )


@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            category_id = request.form.get("category_id")
            amount = request.form.get("amount")
            tx_type = request.form.get("type")
            description = (request.form.get("description") or "").strip()
            tx_date = request.form.get("date")

            if not category_id:
                return apologize("must select a category", 400)
            try:
                amount_value = float(amount)
            except (TypeError, ValueError):
                return apologize("must provide a valid amount", 400)
            if amount_value <= 0:
                return apologize("must provide a valid amount", 400)
            if not tx_type or tx_type not in ("income", "expense"):
                return apologize("must select income or expense", 400)
            if not tx_date:
                tx_date = date.today().isoformat()

            # Verify category belongs to user and matches transaction type
            cat = db.execute(
                "SELECT id FROM categories WHERE id = ? AND user_id = ? AND type = ?",
                category_id, user_id, tx_type
            )
            if not cat:
                return apologize("invalid category selected", 400)

            db.execute(
                "INSERT INTO transactions (user_id, category_id, amount, type, description, date) VALUES (?, ?, ?, ?, ?, ?)",
                user_id, category_id, amount_value, tx_type, description, tx_date
            )
            flash("Transaction added successfully!")
            return redirect("/transactions")

        elif action == "delete":
            tx_id = request.form.get("transaction_id")
            db.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", tx_id, user_id)
            flash("Transaction deleted!")
            return redirect("/transactions")

    categories = db.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY type, name", user_id)

    all_transactions = db.execute("""
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC, t.created_at DESC
    """, user_id)

    return render_template("transactions.html",
        categories=categories,
        transactions=all_transactions,
        usd=usd,
        today=date.today().isoformat()
    )


@app.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    user_id = session["user_id"]
    today = date.today()
    month = today.month
    year = today.year

    if request.method == "POST":
        action = request.form.get("action", "save")

        if action == "delete":
            budget_id = request.form.get("budget_id")
            db.execute("DELETE FROM budgets WHERE id = ? AND user_id = ?", budget_id, user_id)
            flash("Budget deleted!")
            return redirect("/budgets")

        category_id = request.form.get("category_id")
        amount = request.form.get("amount")

        if not category_id:
            return apologize("must select a category", 400)
        try:
            amount_value = float(amount)
        except (TypeError, ValueError):
            return apologize("must provide a valid amount", 400)
        if amount_value <= 0:
            return apologize("must provide a valid amount", 400)

        # Verify category belongs to user and is of type expense
        cat = db.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ? AND type = 'expense'",
            category_id, user_id
        )
        if not cat:
            return apologize("invalid expense category for budget", 400)

        existing = db.execute(
            "SELECT id FROM budgets WHERE user_id = ? AND category_id = ? AND month = ? AND year = ?",
            user_id, category_id, month, year
        )

        if existing:
            db.execute(
                "UPDATE budgets SET amount = ? WHERE id = ?",
                amount_value, existing[0]["id"]
            )
        else:
            db.execute(
                "INSERT INTO budgets (user_id, category_id, amount, month, year) VALUES (?, ?, ?, ?, ?)",
                user_id, category_id, amount_value, month, year
            )

        flash("Budget saved successfully!")
        return redirect("/budgets")

    categories = db.execute(
        "SELECT * FROM categories WHERE user_id = ? AND type = 'expense' ORDER BY name", user_id
    )

    budgets_data = db.execute("""
        SELECT b.*, c.name as category_name, c.icon as category_icon,
            COALESCE(
                (SELECT SUM(t.amount) FROM transactions t
                 WHERE t.category_id = b.category_id AND t.user_id = ?
                 AND t.type = 'expense'
                 AND strftime('%m', t.date) = ? AND strftime('%Y', t.date) = ?),
                0
            ) as spent
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
        ORDER BY c.name
    """, user_id, f"{month:02d}", str(year), user_id, month, year)

    return render_template("budgets.html",
        categories=categories,
        budgets=budgets_data,
        usd=usd,
        month=today.strftime("%B %Y")
    )


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            tx_id = request.form.get("transaction_id")
            db.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", tx_id, user_id)
            flash("Transaction deleted!")
            return redirect(request.referrer or "/history")

    filter_type = request.args.get("type", "")
    filter_category = request.args.get("category", "")
    filter_month = request.args.get("month", "")
    filter_year = request.args.get("year", "")

    query = """
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.type as category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    """
    params = [user_id]

    if filter_type in ("income", "expense"):
        query += " AND t.type = ?"
        params.append(filter_type)

    if filter_category:
        query += " AND t.category_id = ?"
        params.append(filter_category)

    if filter_month:
        query += " AND strftime('%m', t.date) = ?"
        params.append(filter_month.zfill(2))

    if filter_year:
        query += " AND strftime('%Y', t.date) = ?"
        params.append(filter_year)

    query += " ORDER BY t.date DESC, t.created_at DESC"

    all_transactions = db.execute(query, *params)
    categories = db.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY type, name", user_id)

    years = db.execute(
        "SELECT DISTINCT strftime('%Y', date) as year FROM transactions WHERE user_id = ? ORDER BY year DESC",
        user_id
    )

    return render_template("history.html",
        transactions=all_transactions,
        categories=categories,
        years=years,
        usd=usd,
        filters={"type": filter_type, "category": filter_category, "month": filter_month, "year": filter_year}
    )


@app.route("/export")
@login_required
def export():
    user_id = session["user_id"]

    transactions = db.execute("""
        SELECT t.date, c.name as category, c.type, t.amount, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
    """, user_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Category", "Type", "Amount", "Description"])

    for t in transactions:
        writer.writerow([t["date"], t["category"], t["type"], f"{t['amount']:.2f}", t["description"] or ""])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=budgetbuddy_export.csv"}
    )


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            name = (request.form.get("name") or "").strip()
            cat_type = request.form.get("type")
            icon = (request.form.get("icon") or "📦").strip()

            if not name or not cat_type:
                return apologize("must provide name and type", 400)
            if cat_type not in ("income", "expense"):
                return apologize("invalid type", 400)

            db.execute(
                "INSERT INTO categories (user_id, name, type, icon) VALUES (?, ?, ?, ?)",
                user_id, name, cat_type, icon
            )
            flash("Category added successfully!")
            return redirect("/categories")

        elif action == "delete":
            cat_id = request.form.get("category_id")
            tx_count = db.execute(
                "SELECT COUNT(*) as count FROM transactions WHERE category_id = ? AND user_id = ?",
                cat_id, user_id
            )
            if tx_count and tx_count[0]["count"] > 0:
                flash("Cannot delete category with existing transactions!")
            else:
                db.execute("DELETE FROM budgets WHERE category_id = ? AND user_id = ?", cat_id, user_id)
                db.execute("DELETE FROM categories WHERE id = ? AND user_id = ?", cat_id, user_id)
                flash("Category deleted successfully!")
            return redirect("/categories")

    all_categories = db.execute(
        "SELECT c.*, (SELECT COUNT(*) FROM transactions WHERE category_id = c.id AND user_id = ?) as tx_count FROM categories c WHERE c.user_id = ? ORDER BY c.type, c.name",
        user_id, user_id
    )

    return render_template("categories.html", categories=all_categories)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action", "currency")

        if action == "password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirmation = request.form.get("confirmation")

            if not current_password or not new_password or not confirmation:
                return apologize("must fill all password fields", 400)

            rows = db.execute("SELECT hash FROM users WHERE id = ?", user_id)
            if not rows or not check_password_hash(rows[0]["hash"], current_password):
                return apologize("current password is incorrect", 400)

            if new_password != confirmation:
                return apologize("new passwords do not match", 400)

            if len(new_password) < 6:
                return apologize("new password must be at least 6 characters", 400)

            db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_password), user_id)
            flash("Password updated successfully!")
            return redirect("/settings")

        else:
            currency = request.form.get("currency", "")

            if currency not in [c[0] for c in CURRENCIES]:
                return apologize("must select a valid currency", 400)

            db.execute("UPDATE users SET currency = ? WHERE id = ?", currency, user_id)
            session["currency"] = currency
            flash("Display currency updated!")
            return redirect("/settings")

    row = db.execute("SELECT currency FROM users WHERE id = ?", user_id)
    current_currency = (row[0]["currency"] if row else None) or session.get("currency", "USD")

    return render_template("settings.html",
        currencies=CURRENCIES,
        current_currency=current_currency
    )


if __name__ == "__main__":
    app.run(debug=True)
