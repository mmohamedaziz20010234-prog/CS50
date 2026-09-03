"""
Helper utilities for BudgetBuddy.

Tooling note: This file was authored with the assistance of AI coding tools,
used to support the CS50x final project. The functions here (login_required,
usd, apologize) implement standard Flask patterns taught in the course.
"""

from flask import redirect, render_template, session
from functools import wraps


CURRENCIES = [
    ("USD", "$", "US Dollar"),
    ("EUR", "€", "Euro"),
    ("GBP", "£", "British Pound"),
    ("EGP", "E£", "Egyptian Pound"),
    ("SAR", "ر.س", "Saudi Riyal"),
    ("AED", "د.إ", "UAE Dirham"),
    ("INR", "₹", "Indian Rupee"),
    ("JPY", "¥", "Japanese Yen"),
    ("CNY", "¥", "Chinese Yuan"),
    ("TRY", "₺", "Turkish Lira"),
    ("AUD", "A$", "Australian Dollar"),
    ("CAD", "C$", "Canadian Dollar"),
]

CURRENCY_SYMBOLS = {code: symbol for code, symbol, _ in CURRENCIES}


def currency_symbol(code):
    return CURRENCY_SYMBOLS.get(code, "$")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def usd(value):
    """Format a number as currency using the user's display currency."""
    symbol = currency_symbol(session.get("currency", "USD"))
    return f"{symbol}{value:,.2f}"


def apologize(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code
