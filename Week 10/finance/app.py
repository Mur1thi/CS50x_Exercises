import os
import locale

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]

    # Select all transactions for user
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)

    holdings = []
    grand_total = 0

    # Loop through transactions
    for transaction in transactions:
        # Lookup current share price
        quote = lookup(transaction["symbol"])

        # Calculate total value for this transaction
        value = quote["price"] * transaction["shares"]

        # Sum to grand total
        grand_total += value

        # Populate holdings
        holdings.append({
            "name": quote["name"],
            "shares": transaction["shares"],
            "price": usd(quote["price"]),
            "value": usd(value)
        })

    # Get current cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    # Add to grand total
    grand_total += cash

    return render_template("index.html", holdings=holdings,
                           cash=usd(cash),
                           grand_total=usd(grand_total))



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        # Lookup current cash balance
        row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = row[0]["cash"]

        # Pass to template
        return render_template("buy.html", cash=round(cash, 2))

    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol")

        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("shares must be positive int")

        if shares <= 0:
            return apology("shares must be positive int")

        row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = row[0]["cash"]

        stock_price = quote["price"]
        total_cost = stock_price * shares

        if cash < total_cost:
            return apology("not enough cash")

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                   session["user_id"], quote["symbol"], shares, quote["price"])

        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   cash - total_cost, session["user_id"])



        return redirect("/")

    else:
        return apology("Unable to buy stock, please try again")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
        """Get stock quote."""
        if request.method == "GET":
            return render_template("quote.html")
        if request.method == "POST":
            symbol = request.form.get("symbol")
            if not symbol:
                return apology("must provide symbol", 400)
            quote = lookup(symbol)
            if not quote:
                return apology("invalid symbol", 400)
            return render_template("quoted.html", quote=quote)
            return apology("Retry quote", 400)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET": return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username: return apology("must provide username", 400)

        # Ensure password was submitted
        if not password: return apology("must provide password", 400)

        # Ensure confirmation was submitted
        if not confirmation: return apology("must confirm password", 400)

        # Ensure passwords match
        if password != confirmation: return apology("passwords do not match", 400)
        hash = generate_password_hash(password)
        try: db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except: return apology("username already exists", 400)
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        return redirect("/")
    return apology("Registration failed", 400)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        # Ensure symbol was submitted
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must select a stock")

        # Ensure shares was submitted
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("must provide valid shares")

        # Lookup stock price
        quote = lookup(symbol)
        if not quote:
            return apology("symbol not found")

        # Calculate total proceeds
        price = quote["price"]
        total_proceeds = shares * price

        # Insert transaction
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                   session["user_id"], symbol, -shares, price)

        # Update cash balance
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_proceeds, session["user_id"])

        return redirect("/")

    else:
        # Display user's owned stocks
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
                             session["user_id"])

        return render_template("sell.html", symbols=symbols)
