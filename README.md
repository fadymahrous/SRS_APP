# SRS Project

Welcome to the **SRS Project**!

This is a personal tool I'm developing to help me **memorize German (Deutsch) vocabulary** more efficiently.  
Each day, I encounter many new words, and without proper tracking, I find myself quickly forgetting them.  
To address this, I decided to build an app based on the **Spaced Repetition System (SRS)** — a proven technique for long-term memory retention.

---

## How It Works

- When `main.py` is executed:
  - The app checks for any missing tables in the database schema and creates them if needed.
  - It then launches a FastAPI server using Uvicorn, exposing various API endpoints.

- Some API endpoints require authentication:
  - OAuth2 is used for token-based authentication.
  - SHA-256 hashing ensures password security.

---

## Technologies Used

- Python
- FastAPI
- Uvicorn
- OAuth2 for authentication
- SHA-256 for password hashing
- SQLAlchemy for database interaction
- PostgreSQL for vocabulary storage

---

## API Endpoints Overview

Below is a summary of available API endpoints. Most require authentication.

### `GET /users/`
**Description:** Retrieve user details.  
**Access:** Public  
**Use Case:** Fetch information about registered users.

---

### `POST /users/create`
**Description:** Create a new user.  
**Access:** Public  
**Use Case:** Register a new user in the system.

---

### `DELETE /users/userdelete`
**Description:** Delete the currently logged-in user.  
**Access:** Authenticated users only  
**Use Case:** Allows a user to delete their own account.

---

### `POST /auth/token`
**Description:** Log in to receive an access token.  
**Access:** Public  
**Use Case:** Authenticate a user and generate a JWT token for protected endpoints.

---

### `GET /auth/me/`
**Description:** Get details of the currently logged-in user.  
**Access:** Authenticated users only  
**Note:** Mainly used for testing or demonstration purposes.

---

### `POST /word/addword`
**Description:** Add a word to the user's personal word pool.  
**Access:** Authenticated users only  
**Use Case:** Users can add vocabulary they want to track and practice.

---

### `GET /word/todaywordslist`
**Description:** List all words due for practice today.  
**Access:** Authenticated users only  
**Use Case:** Display vocabulary items scheduled for review.

---

### `GET /word/parcticenextword`
**Description:** Fetch the next word for practice.  
**Access:** Authenticated users only  
**Use Case:** Retrieve one word at a time for spaced repetition training.

**Note:** There’s a typo in the endpoint (`parcticenextword`). Consider renaming it to `/word/practicenextword`.

---

### `POST /word/rateword`
**Description:** Submit a recall rating for a practiced word.  
**Access:** Authenticated users only  
**Use Case:** The SM-2 algorithm uses the rating to determine the next review date.

---

**Note:** Most endpoints require a valid JWT token. Be sure to authenticate using `/auth/token` before accessing protected routes.

---

## Current Phase

- Working on adding logic for users to choose how many words they want to practice per day.

---

## Future Plans

- Integrate dict.cc data to provide examples for each word, making them easier to remember.
- Enrich each vocabulary word with cards that help users visually link and remember the word

---

Feel free to explore, contribute, or suggest improvements.
