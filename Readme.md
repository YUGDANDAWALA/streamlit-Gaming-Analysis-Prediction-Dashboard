# 🎮 Esports & Gaming Analytics Dashboard (Streamlit)

A comprehensive, data-driven analytics platform for exploring the world of Esports and Casual Gaming. This project unifies competitive and mainstream gaming data, providing interactive visualizations and AI-powered behavioral insights through a modern Streamlit dashboard.

---

## 📚 Project Overview

This dashboard is designed to:
- Integrate and analyze data from both Esports (competitive gaming) and Casual Gaming domains.
- Provide a unified, interactive interface for exploring trends, performance, and engagement across the gaming industry.
- Leverage machine learning to deliver personalized behavioral insights for gamers.

The project combines web-scraped Esports data, curated CSV datasets for casual/industry trends, and a machine learning model for engagement prediction, all orchestrated within a modular, Python-based architecture.

---

## 🏗️ Architecture & Workflow

### 1. **Data Acquisition & Ingestion**
- **Web Scraping**: `data_scraper.py` scrapes live Esports data (countries, players, tournaments, teams) from esportsearnings.com, cleaning and inserting it into a local MySQL database (`esports_data`).
- **CSV Import**: The same script also imports structured datasets for:
  - `VideoGames.csv`: Historical and best-selling video games (platform, genre, sales, etc.)
  - `Steam.csv`: Steam platform game stats (copies sold, playtime, reviews, etc.)
  - `Gaming_trends.csv`: Industry-wide trends (revenue, player base, metacritic scores, etc.)
  - `main_predict.csv`: User gaming profiles for ML engagement prediction.

### 2. **Database Design**
- All data is stored in a MySQL database (`esports_data`), with tables for each domain:
  - `countries`, `players`, `tournaments`, `teams` (Esports)
  - `VideoGames`, `SteamData`, `GamingTrends` (Casual/Industry)
- The schema is designed for efficient analytics and visualization, with numeric, categorical, and time-series fields.

### 3. **Backend & Data Access**
- **SQLAlchemy** is used for robust, Pythonic database access.
- **Streamlit Caching** ensures efficient, real-time data queries for the dashboard.
- Each dashboard section has a dedicated data-fetching function, returning preprocessed Pandas DataFrames for visualization.

### 4. **Dashboard & Visualization**
- **Streamlit App (`app.py`)**: The main entry point, orchestrating navigation, data access, and rendering.
- **Navigation**: Sidebar-driven, with four main categories:
  - **General**: Overview and Unified Data Analysis (Esports + Casual)
  - **Esports**: Countries, Players, Teams, Tournaments
  - **Casual Gamers**: VideoGames, SteamData, GamingTrends
  - **Behavioral Insights**: ML-powered engagement prediction
- **Visualizations**: Built with Plotly, including bar, line, scatter, 3D scatter, pie, and heatmap charts. Each section provides both high-level and granular views of the data.
- **Custom CSS**: Embedded for a modern, visually appealing, and responsive UI.

### 5. **Machine Learning & Behavioral Insights**
- **ML Model**: An XGBoost classifier is trained on `main_predict.csv` to predict user gaming engagement (High/Medium/Low) based on demographic and behavioral features.
- **User Interaction**: Users input their gaming profile via a form; the model predicts engagement and provides personalized feedback and suggestions.
- **ML Pipeline**: Includes label encoding, train/test split, model training, and real-time prediction within the dashboard.

---

## 🗂️ File-by-File Breakdown

- **`app.py`**: Main Streamlit dashboard. Handles navigation, data fetching, all visualizations, and the ML engagement prediction interface.
- **`data_scraper.py`**: Scrapes Esports data, imports CSVs, and inserts all data into the MySQL database. Contains table creation logic and data cleaning routines.
- **`setup_database.py`**: Orchestrates initial setup: checks MySQL connection, runs the scraper, and ensures all tables are created and populated.
- **`VideoGames.csv`**: Dataset of video game sales, platforms, genres, and publishers for casual gaming analytics.
- **`Steam.csv`**: Steam platform dataset with game sales, playtime, reviews, and developer/publisher info.
- **`Gaming_trends.csv`**: Industry trends dataset, including revenue, player base, metacritic scores, and trending status.
- **`main_predict.csv`**: User gaming profiles for training and running the ML engagement prediction model.
- **`requirements.txt`**: Lists all Python dependencies (Streamlit, Plotly, Pandas, SQLAlchemy, XGBoost, etc.).

---

## 🗄️ Database Schema (Key Tables)

- **countries**: name, total_earnings, num_players, top_game, game_earnings, game_percent
- **players**: player_id, player_name, total_earnings, main_game, earnings_percent
- **tournaments**: tournament_name, prize_pool, game
- **teams**: team_name, revenue, tournaments_played
- **VideoGames**: Rank, Name, Platform, Year, Genre, Publisher, NA_Sales, EU_Sales, JP_Sales, Other_Sales, Global_Sales
- **SteamData**: name, releaseDate, copiesSold, price, revenue, avgPlaytime, reviewScore, publisherClass, publishers, developers, steamId
- **GamingTrends**: Game Title, Genre, Platform, Release Year, Developer, Revenue, Players, Peak Concurrent Players, Metacritic Score, Esports Popularity, Trending Status

---

## 📊 Dashboard Sections (Detailed)

### **General**
- **Overview**: Project introduction, key metrics, and visual summary of the gaming landscape.
- **Unified Data Analysis**: Comparative analytics between Esports and Casual gaming, including correlation matrices, trend lines, and key insights.

### **Esports**
- **Countries**: Top-earning nations, player bases, and favorite games. Visualizations include bar, pie, line, scatter, and 3D plots.
- **Players**: Highest-earning players, their main games, and earnings share. Includes ranking, distribution, and bubble plots.
- **Teams**: Leading organizations, revenues, and tournament activity. Visualized with bar, pie, line, scatter, and 3D charts.
- **Tournaments**: Major events, prize pools, and featured games. Includes grouped analytics and time-series trends.

### **Casual Gamers**
- **VideoGames**: Best-selling titles, platforms, genres, and review scores. Includes bar, pie, scatter, and heatmap visualizations.
- **SteamData**: Steam's top games by sales, playtime, and reviews. Visualized with bar, pie, scatter, and heatmap charts.
- **GamingTrends**: Industry-wide revenue, player base, trending genres, and metacritic scores. Includes bar, pie, scatter, and heatmap analytics.

### **Behavioral Insights**
- **ML Engagement Prediction**: Users enter their gaming profile; the dashboard predicts engagement level (High/Medium/Low) using an XGBoost model. Results include personalized feedback and suggestions, with visual and interactive elements.

---

## 🤖 Machine Learning Pipeline (Behavioral Insights)
- **Input Features**: Age, Gender, Location, Game Genre, Play Time, In-Game Purchases, Game Difficulty, Sessions Per Week, Avg Session Duration, Player Level, Achievements Unlocked.
- **Model**: XGBoost Classifier, trained on labeled engagement data.
- **Output**: Predicted engagement class, with contextual feedback and suggestions for the user.
- **Integration**: Real-time prediction and feedback within the Streamlit dashboard.

---

## 🎯 Project Goals & Impact
- Bridge the gap between Esports analytics and mainstream gaming trends.
- Provide a holistic, data-driven view of the gaming industry for analysts, gamers, and industry professionals.
- Empower users with AI-driven insights into their own gaming behavior and engagement.

---

**This project is a showcase of unified gaming analytics, blending competitive and casual data with modern visualization and AI.**
