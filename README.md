# SRS Project

Welcome to the **SRS Project**!

This project is a personal tool I am developing to help me **memorize German (Deutsch) vocabulary** more efficiently.  
Each day, I encounter many new words, and without proper tracking, I find myself quickly forgetting them.  
To solve this, I decided to build an app based on the **Spaced Repetition System (SRS)** — a proven method for long-term memory retention.

---

## How It Works

- When `main.py` is executed:
  - The app **checks if there are any missing tables** in the database schema and creates them if necessary.
  - It then **runs a FastAPI server** using **Uvicorn**, exposing API endpoints for interacting with the app.

- Some API endpoints require **authentication**:
  - **OAuth** is used for token-based authentication.
  - **SHA-256** encryption is applied for password security to ensure data protection.

---

## Technologies Used
- **Python**
- **FastAPI**
- **Uvicorn**
- **OAuth** for authentication
- **SHA-256** for password hashing
- **sqlalchemy** for database interaction
- **postgres** for vocabulary storage

---
## current Phase
- Working on wordmanagment API endpoint 


## Future Plans
- Add a simple frontend for easier vocabulary management
- Implement spaced repetition logic based on performance using simple SM-2 Algorithm

---

Feel free to explore, contribute, or suggest improvements! 🚀

