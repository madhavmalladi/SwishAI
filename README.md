# 🏀 NBA Player Guessing Game

A web-based NBA trivia game where users guess a randomly selected NBA player based on statistical hints. The game combines a Flask backend with a React frontend, featuring AI-assisted hints and visual charts for player performance.

---

## 🚀 Features

- 🎯 Guess the mystery NBA player based on 6 key statistical categories.
- 📈 Visualize player stats with interactive charts powered by Chart.js.
- 🔍 Search bar to guess and match players by name.
- 🤖 AI-powered chatbot for hints and assistance during gameplay.
- 🔁 New player generator using `nba_api` and Basketball Reference data.

---

## 🧠 How It Works

- The backend randomly selects a player who played in or after 1980 using the `nba_api`.
- The frontend displays 6 categories of per-game stats:
  - Points Per Game (PPG)
  - Assists Per Game (APG)
  - Rebounds Per Game (RPG)
  - Steals Per Game (SPG)
  - Blocks Per Game (BPG)
  - Three Pointers Made (3PM)
- The user submits guesses via a search bar; correct guesses end the game.
- An AI chatbot can be toggled to receive hints based on the player’s era, accolades, or position.

---

## 🛠️ Tech Stack

- **Frontend:** React + TypeScript + Chart.js
- **Backend:** Flask (Python)
- **AI Assistant**; OpenAI API
- **Database**: Supabase
- **Data Sources:**
  - `nba_api` (official NBA stats)
  - Basketball Reference (for image + awards)

