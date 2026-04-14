# Online Voting System 🗳️

A secure, responsive, and robust Online Voting System developed as a complete Full Stack Web Application. Built on top of Python (Flask) and MySQL, this project strictly adheres to UML system design principles (Use Case, Class, Sequence, and Activity diagrams) to provide a flawless voting experience.

## Features & Architecture

### User Roles
1. **👤 Voter**: 
   - Registers for an account and logs in securely.
   - Can view the list of participating candidates.
   - Restricted to casting **exactly one vote**.
   - Can view live election results across the platform.
2. **🛠️ Administrator**:
   - Gets access to a protected admin dashboard.
   - Add, manage, and delete standing candidates.
   - Monitor total system-wide voting statistics.

### Technical Stack
* **Backend**: Python (Flask)
* **Database**: MySQL (PyMySQL connector)
* **Frontend**: HTML5, CSS3 (Glassmorphism design, responsive layouts), Vanilla JavaScript
* **Security**: Password hashing via `werkzeug.security`, protected Flask Sessions, Database-level vote duplication prevention.

---

## Process & Implementation Details

The system flow functions as follows:
1. **System Initialization**: When the app starts, it checks for the target `online_voting` database. If uninitialized, it automatically sets up the schemas (`users`, `candidates`, `votes`) via the `db.py` driver and injects a default admin account.
2. **Authentication Flow**: New users hit the `Register` endpoint. Passwords are mathematically hashed. Login requests start a server-side session that persists their `user_id` and `role`.
3. **Voting Process**: Voters are met with a candidate UI on their dashboard. Clicking "Vote" fires a POST request. The system concurrently checks their `has_voted` status. To guarantee integrity, the state is immediately swapped, and the vote is appended to the `votes` table linking their `user_id` to the `candidate_id`. 
4. **Result Generation**: By utilizing dynamic SQL aggregation (`COUNT(*) GROUP BY candidate_id`), the backend evaluates votes locally on the DB side and ships purely calculated percentages and standings to the frontend Results dashboard. 

---

## Excution & Setup Instructions

Follow these steps to launch the application on your local machine.

### 1. Prerequisites
- **Python 3.8+** installed on your machine.
- A local instance of **MySQL Server** running. 

### 2. Database Configuration
Open the `.env` file located in the root of the project. Ensure the database credentials match your local MySQL configuration:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=      # Put your MySQL password here if you have one
DB_NAME=online_voting
```

### 3. Install Dependencies
Open your terminal (Command Prompt/PowerShell) in the project directory (`d:\onlineVotingSystem`) and run:
```bash
# Optional but recommended: Create a virtual environment
python -m venv venv
# Activate it (Windows):
.\venv\Scripts\activate

# Install the required Flask and MySQL packages
pip install -r requirements.txt
```

### 4. Run the Application!
Start the Flask server. On boot, the server will automatically seed the database and tables for you if they don't yet exist.
```bash
python app.py
```
After you see `* Running on http://127.0.0.1:5000`, open your web browser and navigate to exactly that URL.

### 5. Testing the Roles
The application automatically creates an Admin account for you on its first execution. Log in with the following to access the Admin Dashboard and populate the system with a few candidates:
* **Email**: `admin@voting.com`
* **Password**: `admin123`

After adding some candidates, click `Logout` and visit the `Register` page to create a normal Voter account and test the full voting flow!

---

## Deployment (GitHub & Vercel)

You can deploy this Flask app for free using **GitHub** and **Vercel** combined with a cloud database. 

### 1. Push to GitHub
1. Create a new empty repository on your GitHub account.
2. In your local terminal, initialize Git, commit your files, and push the code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

### 2. Configure Cloud Database
Because Vercel environments are serverless, it cannot host your local MySQL database. You will need to create a free cloud MySQL database (using a provider like **Aiven**, **TiDB**, or **Railway**).
- Retrieve your remote database credentials (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`) from the provider.

### 3. Vercel Configuration (`vercel.json`)
You need a `vercel.json` file in your project directory to tell Vercel how to run your Python Flask app. Create a file named `vercel.json` at the root of the project with the following content:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### 4. Deploy to Vercel
1. Go to [Vercel.com](https://vercel.com/) and register/log in with your GitHub account.
2. Click **Add New** -> **Project** and import the GitHub repository you just created.
3. Before deploying, expand the **Environment Variables** section and add all your cloud database credentials:
   - `DB_HOST` = `<your cloud db host>`
   - `DB_USER` = `<your cloud db user>`
   - `DB_PASSWORD` = `<your cloud db password>`
   - `DB_NAME` = `<your cloud db name>`
4. Click **Deploy**. Vercel will install your dependencies from `requirements.txt` and launch your serverless Flask app!
