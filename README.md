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

