# 🎮 Esports Analytics Dashboard - Streamlit Version

A comprehensive Streamlit application for analyzing esports data with interactive Python-based visualizations.

## 🚀 Features

- **Interactive Charts**: Bar charts, line charts, scatter plots, 3D visualizations, and heatmaps
- **Real-time Data**: Live data from MySQL database
- **Multiple Views**: Countries, Players, Tournaments, Teams, and Advanced Analytics
- **Python-based**: No JavaScript required - all visualizations built with Plotly
- **Responsive Design**: Beautiful UI with custom CSS styling

## 📊 Dashboard Sections

1. **Overview**: Welcome page with key metrics and statistics
2. **Countries**: Analysis of countries by earnings and player count
3. **Players**: Top players analysis with earnings and game distribution
4. **Tournaments**: Tournament statistics and prize pool analysis
5. **Teams**: Team revenue and tournament participation analysis
6. **Data Analysis**: Advanced analytics including correlations and distributions

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+** installed on your system
2. **MySQL Server** (XAMPP recommended for easy setup)
3. **Esports Database** with the required tables

### Setup Steps

1. **Create project folder on D drive:**
   ```
   D:\Streamlit_Esports_Dashboard\
   ```

2. **Copy these files to your project folder:**
   - `streamlit_main.py` → `app.py`
   - `data_scraper_new.py` → `data_scraper.py`
   - `requirements_streamlit.txt` → `requirements.txt`
   - `README_Streamlit.md` → `README.md`

3. **Open VS Code and open the project folder:**
   - File → Open Folder → Select `D:\Streamlit_Esports_Dashboard`

4. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

5. **Activate virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

6. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

7. **Set up MySQL Database:**
   - Start your MySQL server (XAMPP or standalone)
   - Run the setup script to populate the database:
   ```bash
   python setup_database.py
   ```
   - Or manually run the data scraper:
   ```bash
   python data_scraper.py
   ```

## 🚀 Running the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

3. **Explore the dashboard** using the sidebar navigation

## 📈 Visualizations Included

### Bar Charts
- Top countries by earnings
- Top players by earnings
- Top tournaments by prize pool
- Top teams by revenue

### Line Charts
- Player earnings rankings
- Tournament prize pool trends

### Scatter Plots
- Countries: Earnings vs Players
- Players: Earnings vs Ranking
- Tournaments: Prize Pool vs Teams
- Teams: Revenue vs Tournaments

### 3D Scatter Plots
- Interactive 3D visualizations for all data types

### Pie Charts
- Earnings distribution by game
- Country earnings distribution

### Heatmaps
- Correlation matrix of all metrics

## 🔧 Customization

### Adding New Visualizations

To add new charts, create new functions in the visualization section:

```python
def create_new_chart(df, x_col, y_col, title):
    fig = px.new_chart_type(
        df,
        x=x_col,
        y=y_col,
        title=title,
        template="plotly_white"
    )
    return fig
```

### Modifying Database Queries

Edit the fetch functions to modify data retrieval:

```python
@st.cache_data(ttl=3600)
def fetch_custom_data():
    conn = get_db_connection()
    query = "YOUR_CUSTOM_QUERY"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
```

### Styling

Modify the CSS in the `st.markdown` section to customize the appearance:

```python
st.markdown("""
<style>
    .custom-class {
        /* Your custom styles */
    }
</style>
""", unsafe_allow_html=True)
```

## 📊 Database Schema

The application expects the following MySQL tables:

### Countries Table
```sql
CREATE TABLE countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    total_earnings BIGINT,
    num_players INT,
    top_game VARCHAR(100),
    game_earnings BIGINT,
    game_percent FLOAT
);
```

### Players Table
```sql
CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id VARCHAR(100),
    player_name VARCHAR(100),
    total_earnings BIGINT,
    main_game VARCHAR(100),
    earnings_percent FLOAT
);
```

### Tournaments Table
```sql
CREATE TABLE tournaments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_name VARCHAR(200),
    prize_pool BIGINT,
    game VARCHAR(100),
    participate_team INT,
    no_of_player INT
);
```

### Teams Table
```sql
CREATE TABLE teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(255),
    revenue INT,
    tournaments_played INT
);
```

## 🎯 Key Advantages Over Django Version

1. **Python-First**: All visualizations created with Python code
2. **Interactive**: Real-time interactivity without JavaScript
3. **Easy Deployment**: Simple to deploy on Streamlit Cloud
4. **Rapid Development**: Quick iteration and testing
5. **Built-in Caching**: Automatic data caching for performance
6. **Responsive Design**: Works on all device sizes

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Deploy with one click

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 🔍 Troubleshooting

### Database Connection Issues
- Ensure MySQL server is running
- Check database credentials
- Verify database and tables exist

### Missing Data Issues
If you see "No data available" or missing tables:
1. Run the setup script: `python setup_database.py`
2. Check the database status in the Overview section of the dashboard
3. Ensure your internet connection is working (data is scraped from esportsearnings.com)

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Port Issues
- Change port if 8501 is occupied: `streamlit run app.py --server.port 8502`

### Common Error Messages
- **"Table doesn't exist"**: Run `python setup_database.py`
- **"No data available"**: The scraper may have failed. Check internet connection and run setup again
- **"Database connection failed"**: Make sure XAMPP/MySQL is running

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Enjoy exploring esports data with Python-powered visualizations! 🎮📊**