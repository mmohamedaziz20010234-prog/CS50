# BudgetBuddy
#### Video Demo:  <https://youtu.be/x7_XVDa6z0k>
#### Description:

BudgetBuddy is a full-stack personal finance web application built as the capstone final project for Harvard University's CS50x (Introduction to Computer Science). It empowers individuals to take complete control of their financial life by tracking income and expenses, establishing monthly category budgets, analyzing spending distributions through dynamic charts, and exporting records for offline review.

### Team Members & Collaboration
This project was collaboratively designed and developed by a two-person team in accordance with CS50x guidelines:

1. **Mohamed Abdelmaksoud Ismail Abdelmaksoud Aziz**
   - **GitHub Username:** [mmohamedaziz20010234-prog](https://github.com/mmohamedaziz20010234-prog)
   - **edX Username:** `mmohamedaziz20010234`
   - **Location:** Damanhur, Egypt
   - **Role & Contributions:** Backend routing and Flask architecture (`app.py`), SQLite relational database schema design, cryptographic password security and session management (`helpers.py`), data validation, and dynamic CSV streaming export.

2. **Mohammed Khamis Abdel Mawgoud Osman**
   - **GitHub Username:** [mohamedkhamisdev](https://github.com/mohamedkhamisdev)
   - **edX Username:** `mohammed_khamis_osman`
   - **Location:** Damanhur, Egypt
   - **Role & Contributions:** Front-end template architecture with Jinja2 (`templates/`), mobile-responsive UI design with Bootstrap 5 dark theme, client-side dynamic JavaScript interactions (`static/js/script.js`), and Chart.js analytical visualizations.

### Problem Statement & Motivation
Managing personal finances with spreadsheets or manual notebooks is often tedious, prone to human error, and difficult to visualize over time. Conversely, many modern commercial budgeting applications suffer from bloat, subscription paywalls, intrusive advertisements, or privacy concerns related to storing sensitive financial transactions on third-party cloud infrastructure. BudgetBuddy addresses these challenges directly by providing a clean, responsive, fast, and self-hosted personal finance manager that runs securely on the user's own machine with zero third-party data tracking.

---

### Key Features & Capabilities

1. **Secure User Authentication & Session Management**
   - User registration and login protected with cryptographic password hashing using Werkzeug (`generate_password_hash` and `check_password_hash`).
   - Server-side session storage using `Flask-Session` on the server filesystem, ensuring sensitive session data is not stored insecurely in client-side cookies.
   - Route-level access control with a custom `@login_required` decorator.
   - In-app password change functionality directly from account settings.

2. **Intuitive Financial Dashboard**
   - At-a-glance metrics calculating Monthly Income, Monthly Expenses, Monthly Net Balance, and All-Time Overall Balance.
   - Interactive Doughnut Chart rendered with Chart.js, visualizing spending proportion across expense categories for the active month.
   - Interactive Line Chart illustrating daily spending fluctuations across the month.
   - Quick preview of the 5 most recent transactions.

3. **Transaction Logging & Management**
   - Fast entry form allowing users to record income or expense transactions with category selection, date picker, amount, and custom notes.
   - Client-side dynamic category filtering: selecting "Income" or "Expense" automatically updates the category dropdown to show only relevant categories without requiring a full page refresh.
   - Complete transaction listing with reverse chronological ordering and instant one-click deletion with confirmation safeguards.

4. **Monthly Category Budgets & Early Warning Alerts**
   - Set spending limits for any expense category for the current calendar month.
   - Real-time progress bars comparing actual category spending against the allocated limit.
   - Visual color feedback: green progress for normal spending, yellow warning when spending exceeds 80% of budget, and bright red alert when the budget limit is breached.
   - Easy budget updating and deletion controls.

5. **Advanced Transaction History & Filtering**
   - Comprehensive historical view supporting multi-parameter filtering by Transaction Type (All / Income / Expense), Category, Month (January through December), and Year.
   - Instant calculation of the Filtered Net balance for any active query.
   - Instant one-click filter reset button.
   - Direct transaction deletion from the history table.

6. **Customizable Categories**
   - Automatic seeding of 15 sensible default categories upon user registration (e.g., Salary, Freelance, Investments, Food & Dining, Transportation, Housing, Utilities, Entertainment, Health, Education).
   - Ability to add new custom categories with custom emoji icons and designated types.
   - Protected deletion: categories with existing recorded transactions cannot be accidentally deleted, preserving database referential integrity.

7. **Multi-Currency Display Settings**
   - Global display currency preference supporting 12 major international currencies (USD $, EUR €, GBP £, EGP E£, SAR ر.س, AED د.إ, INR ₹, JPY ¥, CNY ¥, TRY ₺, AUD A$, CAD C$).
   - Formats numbers consistently across the dashboard, tables, and budget widgets according to the selected currency.

8. **Data Export & Backup**
   - One-click CSV export via the `/export` route, allowing users to download their entire financial record into Microsoft Excel, Google Sheets, or Apple Numbers for archival and deeper analysis.

---

### Project File Structure & Architecture

The application is modularized across the following files and directories:

- **`app.py`**: The core application controller. Contains the Flask app initialization, database connection management, database schema definitions (`init_db`), default category seeding (`create_default_categories`), and all route handlers:
  - `/register`, `/login`, `/logout`: Authentication lifecycle.
  - `/dashboard`: Monthly metrics, Chart.js dataset generation, recent transactions.
  - `/transactions`: Adding and deleting transactions with backend validation.
  - `/budgets`: Creating, modifying, tracking, and deleting monthly category spending limits.
  - `/history`: Multi-parameter filtered queries, year extraction, filtered net sums.
  - `/categories`: Creating and safely deleting custom categories.
  - `/settings`: Updating user currency preferences and changing account passwords.
  - `/export`: Generating and streaming CSV attachments dynamically via Python's `csv` and `io.StringIO` modules.

- **`helpers.py`**: Utility helper functions and definitions:
  - `login_required`: Decorator that wraps route handlers to enforce authentication.
  - `usd`: Formats floating-point numbers with commas, two decimals, and the user's chosen currency symbol.
  - `apologize`: Renders a user-friendly error template (`apology.html`) displaying HTTP status codes and custom explanatory messages.
  - `CURRENCIES` & `CURRENCY_SYMBOLS`: Dictionaries mapping currency ISO codes to symbols and country names.

- **`templates/`**: Jinja2 HTML templates structuring the presentation layer:
  - **`layout.html`**: Master base template containing the `<head>` metadata, Bootstrap 5 CDN links, Bootstrap Icons, custom dark theme stylesheet, responsive navigation bar with active user badge, flash message alerts, footer, and script bundles.
  - **`dashboard.html`**: The main user dashboard displaying summary cards, Chart.js canvas elements, and recent activity.
  - **`transactions.html`**: Form for adding new transactions with responsive grid layout and table of all logged transactions.
  - **`budgets.html`**: Budget creation form and interactive progress bar cards.
  - **`history.html`**: Filter bar with dropdowns for type, category, month, and year, along with the filtered results table.
  - **`categories.html`**: Category management layout split into Expense and Income category lists with transaction counters.
  - **`settings.html`**: Side-by-side configuration cards for currency selection and password modification.
  - **`login.html`** & **`register.html`**: Clean authentication cards with validation hints.
  - **`apology.html`**: Playful yet informative error page for handling invalid inputs or unauthorized actions.

- **`static/`**: Static front-end assets:
  - **`css/style.css`**: Custom CSS rules enhancing Bootstrap 5 dark mode, defining smooth card elevations, rounded badge borders, custom progress bar heights, and responsive mobile padding.
  - **`js/script.js`**: Client-side JavaScript handling dynamic DOM manipulation for category filtering on transaction type change and initialization of the Chart.js doughnut and line charts with custom palettes and tooltips.

- **`requirements.txt`**: Specifies Python package dependencies: `flask`, `cs50`, `flask-session`, and `werkzeug`.

- **`.gitignore`**: Excludes local database files (`budgetbuddy.db`), session caches (`flask_session/`), and Python bytecode caches (`__pycache__/`) from version control.

---

### Database Schema

The application uses SQLite with four normalized relational tables:

1. **`users`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `username`: TEXT UNIQUE NOT NULL
   - `hash`: TEXT NOT NULL (salted hash generated via Werkzeug)
   - `currency`: TEXT DEFAULT 'USD'
   - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

2. **`categories`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `user_id`: INTEGER NOT NULL (Foreign Key -> `users.id`)
   - `name`: TEXT NOT NULL
   - `type`: TEXT NOT NULL CHECK(type IN ('income', 'expense'))
   - `icon`: TEXT DEFAULT '📦'

3. **`transactions`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `user_id`: INTEGER NOT NULL (Foreign Key -> `users.id`)
   - `category_id`: INTEGER NOT NULL (Foreign Key -> `categories.id`)
   - `amount`: REAL NOT NULL
   - `type`: TEXT NOT NULL CHECK(type IN ('income', 'expense'))
   - `description`: TEXT
   - `date`: DATE NOT NULL
   - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

4. **`budgets`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `user_id`: INTEGER NOT NULL (Foreign Key -> `users.id`)
   - `category_id`: INTEGER NOT NULL (Foreign Key -> `categories.id`)
   - `amount`: REAL NOT NULL
   - `month`: INTEGER NOT NULL
   - `year`: INTEGER NOT NULL
   - `UNIQUE(user_id, category_id, month, year)`

---

### Design Decisions & Trade-Offs

1. **Database Engine (SQLite vs. PostgreSQL/MySQL)**:
   SQLite was chosen because BudgetBuddy is designed as a portable, self-contained personal application. SQLite stores the entire database in a single local file (`budgetbuddy.db`) without requiring external daemon processes or complex configuration. This aligns perfectly with the privacy goal of keeping financial records strictly on the user's machine.

2. **Front-End Architecture & Charting (Chart.js via CDN vs. React/Vue)**:
   Rather than introducing a heavy Node.js build pipeline or complex Single Page Application (SPA) state management, server-rendered Jinja2 templates were paired with lightweight client-side JavaScript and Chart.js from a CDN. This keeps the application simple to run, fast to load, and easy to maintain while delivering modern interactivity.

3. **Server-Side Session Storage vs. Client Cookies**:
   To prevent tampering and session data leakage, `Flask-Session` configured with filesystem storage was used instead of signed client-side cookies, mirroring best practices taught in CS50's Finance problem set.

4. **Dynamic Client-Side Category Filtering**:
   When logging transactions, users need categories matching their chosen type (income or expense). Filtering options client-side via JavaScript provides instant responsiveness without incurring extra server round-trips.

---

### Academic Honesty & AI Assistance Disclosure

In accordance with the CS50x Academic Honesty Policy for the Final Project:
AI coding tools (large language model assistants) were utilized as helpers during the development of this project to assist with boilerplate code generation, syntax validation, documentation phrasing, and debugging. The conceptual design, system architecture, database schema, and core logic represent my own work.

---

### How to Run Locally

1. **Clone the repository or navigate to the project directory**:
   ```bash
   cd "Final.edx - Copy"
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask development server**:
   ```bash
   flask run
   ```
   *Alternatively:*
   ```bash
   python app.py
   ```

4. **Open your browser and visit**:
   ```
   http://127.0.0.1:5000/
   ```
