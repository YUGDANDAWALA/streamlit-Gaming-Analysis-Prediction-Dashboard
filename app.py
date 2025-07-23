import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from sqlalchemy import create_engine, text  # Add text import
import numpy as np
from typing import List, Optional, Literal
import requests
import pymysql  # NEW: pymysql import

from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


# Page configuration
st.set_page_config(
    page_title="Gaming Analytics Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #4b6cb7;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #4b6cb7;
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background-color: #f8fafc;
        border: 2px solid #4b6cb7;
        border-radius: 10px;
    }
    .stPlotlyChart {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database engine function (SQLAlchemy)
@st.cache_resource
def get_engine():
    engine = create_engine("mysql+pymysql://root:@localhost/esports_data")
    return engine

# Function to check if table exists and has data

def check_table_data(table_name):
    """Check if a table exists and has data"""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
            row = result.fetchone()
            if not row:
                st.warning(f"Table '{table_name}' does not exist in the database.")
                return False, 0
            # Check if table has data
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count_row = result.fetchone()
            if not count_row:
                st.warning(f"Table '{table_name}' exists but has no data.")
                return True, 0
            count = count_row[0]
            if count == 0:
                st.warning(f"Table '{table_name}' exists but has no data.")
                return True, 0
            return True, count
    except Exception as e:
        st.error(f"Error checking table '{table_name}': {e}")
        return False, 0

# Function to import CSV into database table

def import_csv_to_db(csv_path: str, table_name: str, engine, if_exists: Literal['fail', 'replace', 'append'] = 'append'):
    """
    Import a CSV file into a MySQL table using pandas and SQLAlchemy.
    - csv_path: path to the CSV file
    - table_name: name of the table in the database
    - engine: SQLAlchemy engine
    - if_exists: 'append' to add, 'replace' to overwrite
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    st.success(f"✅ Imported {csv_path} to {table_name} ({len(df)} rows)")

# Data fetching functions with caching
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_countries_data():
    engine = get_engine()
    try:
        query = "SELECT name, total_earnings, num_players, top_game, game_earnings, game_percent FROM countries LIMIT 50"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching countries data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_players_data():
    engine = get_engine()
    try:
        query = "SELECT player_id, player_name, total_earnings, main_game, earnings_percent FROM players LIMIT 50"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching players data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_tournaments_data():
    engine = get_engine()
    try:
        query = "SELECT tournament_name, game, prize_pool FROM tournaments LIMIT 50"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching tournaments data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_teams_data():
    engine = get_engine()
    try:
        query = "SELECT team_name, revenue, tournaments_played FROM teams LIMIT 50"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching teams data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_videogames_data():
    engine = get_engine()
    try:
        query = "SELECT * FROM VideoGames LIMIT 1000"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching VideoGames data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_steamdata_data():
    engine = get_engine()
    try:
        query = "SELECT * FROM SteamData LIMIT 1000"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching SteamData: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_gamingtrends_data():
    engine = get_engine()
    try:
        query = "SELECT * FROM gamingtrends LIMIT 1000"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching GamingTrends data: {e}")
        return pd.DataFrame()

# Visualization functions
def create_bar_chart(df, x_col, y_col, title, color_col=None, width=None):
    """Create a bar chart using Plotly"""
    if df.empty:
        st.warning("No data available for this visualization.")
        return None
    
    fig = px.bar(
        df.head(100),  # Limit to top 20 for better visualization
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_color="#4b6cb7",
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        height=500,
        width=width,
        showlegend=True if color_col else False
    )
    
    fig.update_xaxes(tickangle=-45)
    return fig

def create_line_chart(df, x_col, y_col, title):
    """Create a line chart using Plotly"""
    if df.empty:
        st.warning("No data available for this visualization.")
        return None
    
    fig = px.line(
        df.head(100),
        x=x_col,
        y=y_col,
        title=title,
        template="plotly_white",
        markers=True
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_color="#4b6cb7",
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        height=500
    )
    
    fig.update_xaxes(tickangle=-45)
    return fig

def create_scatter_plot(df, x_col, y_col, size_col, title):
    """Create a scatter plot using Plotly"""
    if df.empty:
        st.warning("No data available for this visualization.")
        return None
    
    fig = px.scatter(
        df.head(50),
        x=x_col,
        y=y_col,
        size=size_col,
        title=title,
        template="plotly_white",
        hover_data=[x_col, y_col, size_col]
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_color="#4b6cb7",
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        height=500
    )
    
    fig.update_xaxes(tickangle=-45)
    return fig

def create_3d_scatter(df, x_col, y_col, z_col, title):
    """Create a 3D scatter plot using Plotly"""
    if df.empty:
        st.warning("No data available for this visualization.")
        return None
    
    fig = px.scatter_3d(
        df.head(180),
        x=x_col,
        y=y_col,
        z=z_col,
        title=title,
        template="plotly_white",
        color=z_col,
        size=z_col
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_color="#4b6cb7",
        height=550
    )
    
    return fig

def create_pie_chart(df, names_col, values_col, title):
    """Create a pie chart using Plotly"""
    if df.empty:
        st.warning("No data available for this visualization.")
        return None
    
    fig = px.pie(
        df.head(50),
        names=names_col,
        values=values_col,
        title=title,
        template="plotly_white"
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_color="#4b6cb7",
        height=500
    )
    
    return fig

def create_heatmap(df, x_col, y_col, values_col, title):
    """Create a heatmap using Plotly"""
    if df.empty:
        st.warning("No data available for this visualization.")
        return None
    
    pivot_df = df.pivot_table(
        values=values_col,
        index=y_col,
        columns=x_col,
        aggfunc='mean'
    ).fillna(0)
    
    fig = px.imshow(
        pivot_df,
        title=title,
        template="plotly_white",
        aspect="auto",
        color_continuous_scale='Magma'  # Use a soft, blue-green palette
    )
    
    fig.update_layout(
        title_font_size=20,
        title_font_color="#4b6cb7",
        height=500
    )
    
    return fig

# --- Dashboard Section Functions ---
def overview_dashboard():
    # --- Title and Subtitle OUTSIDE the Hero Box (with purple and gaming logo) ---
    st.markdown('''
    <div style="text-align:center; margin-top:1.5em; margin-bottom:0.2em;">
        <span style="font-size:2.7em; font-weight:900; color:#8e44ad; letter-spacing:1.5px;"><span style='font-size:1.2em; vertical-align:middle; margin-right:0.2em;'>🎮</span>Gaming Analysis Dashboard</span><br>
        <span style="font-size:1.25em; color:#34a0a4; font-weight:600; display:inline-block; margin-top:0.3em;">Unlock the power of Esports &amp; Casual Gaming data. <span style='color:#ffe066;'>🚀</span></span>
    </div>
    ''', unsafe_allow_html=True)

    # --- Hero Box with Only Supporting Text ---
    st.markdown('''
    <div style="position:relative; background: linear-gradient(120deg, rgba(75,108,183,0.93) 0%, rgba(52,160,164,0.93) 100%), url('https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1200&q=80') center/cover no-repeat; border-radius: 22px; box-shadow: 0 6px 36px rgba(75,108,183,0.18); padding: 2.2em 2em 1.7em 2em; margin-bottom:2.5em; text-align:center; overflow:hidden;">
        <div style="margin-top:0.1em; font-size:1.13em; color:#f8fafc; font-weight:400;">From global esports arenas to your living room, see what shapes the world of gaming.<br>Dive into interactive charts, live data, and smart AI insights—all in one seamless dashboard.</div>
    </div>
    ''', unsafe_allow_html=True)

    # --- Visually Engaging Quick Stats Row (with emojis and color) ---
    st.markdown('''
    <div style="display:flex; gap:1.7em; justify-content:center; margin-bottom:2.5em;">
        <div class="metric-card" style="flex:1; text-align:center; box-shadow:0 4px 18px rgba(75,108,183,0.10); background:linear-gradient(135deg,#e0eafc 0%,#cfdef3 100%); border:2.5px solid #4b6cb7; border-radius:18px;">
            <div style="font-size:2.5em;">🌍</div>
            <div style="font-size:1.13em; color:#4b6cb7; font-weight:700;">Countries</div>
            <div style="font-size:2em; color:#34a0a4; font-weight:800;">50+</div>
            <div style="font-size:1em; color:#888;">Esports Nations</div>
        </div>
        <div class="metric-card" style="flex:1; text-align:center; box-shadow:0 4px 18px rgba(75,108,183,0.10); background:linear-gradient(135deg,#e0eafc 0%,#cfdef3 100%); border:2.5px solid #4b6cb7; border-radius:18px;">
            <div style="font-size:2.5em;">👥</div>
            <div style="font-size:1.13em; color:#4b6cb7; font-weight:700;">Players</div>
            <div style="font-size:2em; color:#34a0a4; font-weight:800;">10,000+</div>
            <div style="font-size:1em; color:#888;">Pro &amp; Casual Gamers</div>
        </div>
        <div class="metric-card" style="flex:1; text-align:center; box-shadow:0 4px 18px rgba(75,108,183,0.10); background:linear-gradient(135deg,#e0eafc 0%,#cfdef3 100%); border:2.5px solid #4b6cb7; border-radius:18px;">
            <div style="font-size:2.5em;">🏆</div>
            <div style="font-size:1.13em; color:#4b6cb7; font-weight:700;">Tournaments</div>
            <div style="font-size:2em; color:#34a0a4; font-weight:800;">500+</div>
            <div style="font-size:1em; color:#888;">Major Events</div>
        </div>
        <div class="metric-card" style="flex:1; text-align:center; box-shadow:0 4px 18px rgba(75,108,183,0.10); background:linear-gradient(135deg,#e0eafc 0%,#cfdef3 100%); border:2.5px solid #4b6cb7; border-radius:18px;">
            <div style="font-size:2.5em;">🕹️</div>
            <div style="font-size:1.13em; color:#4b6cb7; font-weight:700;">Games</div>
            <div style="font-size:2em; color:#34a0a4; font-weight:800;">1,000+</div>
            <div style="font-size:1em; color:#888;">Titles &amp; Trends</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # --- Why Use This Dashboard? ---
    st.markdown('''
    <div style="background: linear-gradient(90deg,#e0eafc 0%,#cfdef3 100%); border-radius: 16px; box-shadow: 0 2px 18px rgba(75,108,183,0.10); padding: 2em 1.5em 1.5em 1.5em; margin-bottom:2.2em;">
        <div style="font-size:1.35em; color:#4b6cb7; font-weight:800; margin-bottom:0.7em; text-align:center;">Why Use This Dashboard?</div>
        <div style="display:flex; flex-wrap:wrap; gap:1.5em; justify-content:center;">
            <div style="flex:1; min-width:210px; max-width:250px; background:#fff; border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.7em; color:#4b6cb7;">⚡</div>
                <b style="color:#222;">Instant Insights</b>
                <div style="color:#444; font-size:1.01em; margin-top:0.3em;">Get real-time, interactive analytics on every click—no waiting, no hassle.</div>
            </div>
            <div style="flex:1; min-width:210px; max-width:250px; background:#fff; border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.7em; color:#4b6cb7;">🎨</div>
                <b style="color:#222;">Stunning Visuals</b>
                <div style="color:#444; font-size:1.01em; margin-top:0.3em;">Enjoy beautiful charts, 3D plots, and heatmaps designed for clarity and impact.</div>
            </div>
            <div style="flex:1; min-width:210px; max-width:250px; background:#fff; border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.7em; color:#4b6cb7;">🤖</div>
                <b style="color:#222;">AI-Powered</b>
                <div style="color:#444; font-size:1.01em; margin-top:0.3em;">Predict your gaming engagement and get personalized suggestions with machine learning.</div>
            </div>
            <div style="flex:1; min-width:210px; max-width:250px; background:#fff; border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.7em; color:#4b6cb7;">🌐</div>
                <b style="color:#222;">All-in-One</b>
                <div style="color:#444; font-size:1.01em; margin-top:0.3em;">Esports, casual gaming, trends, and more—explore everything in one place.</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # --- Featured Insights (Sample/Fun Facts) ---
    st.markdown('''
    <div style="background: #fff; border-radius: 16px; box-shadow: 0 2px 18px rgba(75,108,183,0.10); padding: 2em 1.5em 1.5em 1.5em; margin-bottom:2.2em;">
        <div style="font-size:1.25em; color:#4b6cb7; font-weight:700; margin-bottom:0.7em; text-align:center;">Featured Insights</div>
        <div style="display:flex; flex-wrap:wrap; gap:1.5em; justify-content:center;">
            <div style="flex:1; min-width:200px; max-width:300px; background:linear-gradient(120deg,#e0eafc 0%,#cfdef3 100%); border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.5em; color:#34a0a4;">🏆</div>
                <b style="color:#222;">Biggest Esports Prize Pool</b>
                <div style="color:#444; font-size:1em; margin-top:0.3em;">The largest esports tournament prize pool exceeded <b>$40 million</b>!</div>
            </div>
            <div style="flex:1; min-width:200px; max-width:300px; background:linear-gradient(120deg,#e0eafc 0%,#cfdef3 100%); border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.5em; color:#34a0a4;">🕹️</div>
                <b style="color:#222;">Top-Selling Game</b>
                <div style="color:#444; font-size:1em; margin-top:0.3em;">Some video games have sold over <b>200 million</b> copies worldwide!</div>
            </div>
            <div style="flex:1; min-width:200px; max-width:300px; background:linear-gradient(120deg,#e0eafc 0%,#cfdef3 100%); border-radius:12px; padding:1.1em; box-shadow:0 2px 8px rgba(75,108,183,0.06);">
                <div style="font-size:1.5em; color:#34a0a4;">🌍</div>
                <b style="color:#222;">Global Reach</b>
                <div style="color:#444; font-size:1em; margin-top:0.3em;">Esports and gaming communities span <b>every continent</b>—join the movement!</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # --- Modern Call to Action ---
    st.markdown('''
    <div style="text-align:center; margin-top:2.7em;">
        <span style="font-size:1.35em; color:#4b6cb7; font-weight:800;">Ready to level up your gaming insights?</span><br>
        <span style="font-size:1.13em; color:#222;">Use the sidebar to start exploring. <b>Every click unlocks a new perspective!</b></span>
        <div style="margin-top:2em;">
            <a href="#" style="background:linear-gradient(90deg,#4b6cb7 0%,#34a0a4 100%); color:#fff; padding:1.1em 2.7em; border-radius:999px; font-weight:900; font-size:1.25em; text-decoration:none; box-shadow:0 4px 18px rgba(52,160,164,0.18); letter-spacing:0.7px; transition:box-shadow 0.2s;">Start Exploring 🚀</a>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def countries_dashboard():
    st.markdown("## 🌍 Countries Analysis")
    
    countries_df = fetch_countries_data()
    
    if not countries_df.empty:
        # First row: Bar and Pie graphs side by side (pie chart centered and improved)
        col1, col2 = st.columns([2,2])
        with col1:
            fig = create_bar_chart(
                countries_df,
                'name',
                'total_earnings',
                'Top Countries by Total Earnings'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Pie chart: Top 6 games by total percentage (more even slices, default spacing, previous look)
            grouped_game_percent = countries_df.groupby('top_game')['game_percent'].sum()
            sorted_game_percent = grouped_game_percent.sort_values(ascending=False)
            top_games = sorted_game_percent.head(6).reset_index()
            fig = create_pie_chart(
                top_games,
                'top_game',
                'game_percent',
                'Top 6 Games by Total Percentage'
            )
            if fig:
                fig.update_layout(
                    height=420,
                    title_font_size=22,
                    legend_font_size=13,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=20, r=20, t=60, b=60),
                    showlegend=True
                )
                fig.update_traces(textfont_size=13, pull=[0]*6, marker=dict(line=dict(color='#fff', width=1)))
                st.plotly_chart(fig, use_container_width=True)
        # Second row: Line chart below
        with st.container():
            fig = create_line_chart(
                countries_df,
                'name',
                'num_players',
                'Countries by Number of Players (Line Plot)'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        # 3D Scatter plot
        fig = create_3d_scatter(
            countries_df,
            'name',
            'total_earnings',
            'num_players',
            'Countries: Earnings vs Players (3D View)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Scatter plot
        fig = create_scatter_plot(
            countries_df,
            'name',
            'total_earnings',
            'num_players',
            'Countries: Earnings vs Players (Bubble Size = Number of Players)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Data table
        st.markdown("### 📋 Raw Data")
        st.dataframe(countries_df, use_container_width=True)
    else:
        st.warning("No countries data available.")

def players_dashboard():
    st.markdown("## 👥 Players Analysis")
    
    # Check if players table exists and has data
    exists, count = check_table_data('players')
    if not exists:
        st.error("Players table does not exist. Please run the data scraper first.")
        st.info("To fix this, run: `python data_scraper.py`")
        return
    elif count == 0:
        st.warning("Players table exists but has no data. Please run the data scraper first.")
        st.info("To fix this, run: `python data_scraper.py`")
        return
    
    players_df = fetch_players_data()
    
    if not players_df.empty:
        # Top players by earnings
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_bar_chart(
                players_df,
                'player_name',
                'total_earnings',
                'Top Players by Earnings'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pie chart: Top 8 games by number of players (count of players per main_game)
            top_games = (
                players_df['main_game'].value_counts().head(8).reset_index()
            )
            top_games.columns = ['main_game', 'player_count']
            fig = create_pie_chart(
                top_games,
                'main_game',
                'player_count',
                'Top 8 Games by Number of Players'
            )
            if fig:
                fig.update_layout(
                    height=420,
                    title_font_size=22,
                    legend_font_size=13,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=20, r=20, t=60, b=60),
                    showlegend=True
                )
                fig.update_traces(textfont_size=13, pull=[0]*8, marker=dict(line=dict(color='#fff', width=1)))
                st.plotly_chart(fig, use_container_width=True)
        
        # Line chart of player_id vs total_earnings
        # players_df_sorted = players_df.sort_values('total_earnings', ascending=False).reset_index()
        fig = create_line_chart(
            players_df,
            'player_id',
            'total_earnings',
            'Player Earnings by Player ID (Line Plot)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Add ranking column for 3D scatter plot
        players_df = players_df.sort_values('total_earnings', ascending=False).reset_index(drop=True)
        players_df['ranking'] = players_df.index + 1
        # 3D Scatter plot
        fig = create_3d_scatter(
            players_df,
            'player_name',
            'total_earnings',
            'ranking',  # Use computed ranking
            'Players: Earnings vs Ranking (3D View)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Bubble plot: player_name vs total_earnings, bubble size = total_earnings
        fig = create_scatter_plot(
            players_df,
            'player_name',
            'total_earnings',
            'total_earnings',
            'Players: Earnings vs Player Name (Bubble Size = Earnings)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown("### 📋 Raw Data")
        st.dataframe(players_df, use_container_width=True)
    else:
        st.warning("No players data available.")

def tournaments_dashboard():
    st.markdown("## 🏆 Tournaments Analysis")
    
    # Check if tournaments table exists and has data
    exists, count = check_table_data('tournaments')
    if not exists:
        st.error("Tournaments table does not exist. Please run the data scraper first.")
        st.info("To fix this, run: `python data_scraper.py`")
        return
    elif count == 0:
        st.warning("Tournaments table exists but has no data. Please run the data scraper first.")
        st.info("To fix this, run: `python data_scraper.py`")
        return
    
    tournaments_df = fetch_tournaments_data()
    
    if not tournaments_df.empty:
        # First row: Bar and Pie charts side by side
        col1, col2 = st.columns(2)
        with col1:
            fig = create_bar_chart(
                tournaments_df,
                'tournament_name',
                'prize_pool',
                'Top Tournaments by Prize Pool'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Pie chart: Top 6 games by total prize_pool
            grouped_prize_pool = tournaments_df.head(100).groupby('game')['prize_pool'].sum()
            sorted_prize_pool = grouped_prize_pool.sort_values(ascending=False)
            top_games = sorted_prize_pool.head(6).reset_index()
            fig = create_pie_chart(
                top_games,
                'game',
                'prize_pool',
                'Top 6 Games by Total Prize Pool'
            )
            if fig:
                fig.update_layout(
                    height=420,
                    title_font_size=22,
                    legend_font_size=13,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=20, r=20, t=60, b=60),
                    showlegend=True
                )
                fig.update_traces(textfont_size=13, pull=[0]*6, marker=dict(line=dict(color='#fff', width=1)))
                st.plotly_chart(fig, use_container_width=True)
        # Second row: Line chart below both
        with st.container():
            # Restore: show total prize pool per game (grouped by game), all available games
            game_prize_df = tournaments_df.groupby('game')['prize_pool'].sum().reset_index()
            fig = create_line_chart(
                game_prize_df,
                'game',
                'prize_pool',
                'Games vs Prize Pool (Line Plot)'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        # 3D Scatter plot below line chart
        fig = create_3d_scatter(
            tournaments_df,
            'tournament_name',
            'game',
            'prize_pool',
            'Tournaments: Tournament Name vs Game vs Prize Pool (3D View)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Bubble plot below 3D scatter plot
        fig = create_scatter_plot(
            tournaments_df,
            'tournament_name',
            'prize_pool',
            'prize_pool',
            'Tournaments: Tournament Name vs Prize Pool (Bubble Size = Prize Pool)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Data table (only show tournament_name, game, prize_pool)
        st.markdown("### 📋 Raw Data")
        st.dataframe(tournaments_df[['tournament_name', 'game', 'prize_pool']], use_container_width=True)
    else:
        st.warning("No tournaments data available.")

def teams_dashboard():
    st.markdown("## 🏢 Teams Analysis")
    
    # Check if teams table exists and has data
    exists, count = check_table_data('teams')
    if not exists:
        st.error("Teams table does not exist. Please run the data scraper first.")
        st.info("To fix this, run: `python data_scraper.py`")
        return
    elif count == 0:
        st.warning("Teams table exists but has no data. Please run the data scraper first.")
        st.info("To fix this, run: `python data_scraper.py`")
        return
    
    teams_df = fetch_teams_data()
    
    if not teams_df.empty:
        # First row: Bar and Pie charts side by side
        col1, col2 = st.columns(2)
        with col1:
            fig = create_bar_chart(
                teams_df,
                'team_name',
                'revenue',
                'Top Teams by Revenue'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Pie chart: Top 6 teams by tournaments_played
            top_teams = (
                teams_df.sort_values('tournaments_played', ascending=False)
                .head(6)
                .loc[:, ['team_name', 'tournaments_played']]
            )
            fig = create_pie_chart(
                top_teams,
                'team_name',
                'tournaments_played',
                'Top 6 Teams by Tournaments Played'
            )
            if fig:
                fig.update_layout(
                    height=420,
                    title_font_size=22,
                    legend_font_size=13,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5
                    ),
                    margin=dict(l=20, r=20, t=60, b=60),
                    showlegend=True
                )
                fig.update_traces(textfont_size=13, pull=[0]*6, marker=dict(line=dict(color='#fff', width=1)))
                st.plotly_chart(fig, use_container_width=True)
        # Second row: Line chart below both
        with st.container():
            fig = create_line_chart(
                teams_df,
                'team_name',
                'tournaments_played',
                'Teams by Tournaments Played (Line Plot)'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        # 3D Scatter plot
        fig = create_3d_scatter(
            teams_df,
            'team_name',
            'revenue',
            'tournaments_played',
            'Teams: Revenue vs Tournaments Played (3D View)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Bubble plot: team_name vs revenue, bubble size = tournaments_played
        fig = create_scatter_plot(
            teams_df,
            'team_name',
            'revenue',
            'tournaments_played',
            'Teams: Revenue vs Team Name (Bubble Size = Tournaments Played)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Data table
        st.markdown("### 📋 Raw Data")
        st.dataframe(teams_df, use_container_width=True)
    else:
        st.warning("No teams data available.")

def videogames_dashboard():
    st.markdown("## 🎮 Video Games Analysis")
    videogames_df = fetch_videogames_data()
    if not videogames_df.empty:
        # Sort by Global_Sales descending for better bar chart readability
        sorted_df = videogames_df.sort_values(['Global_Sales'], ascending=False).head(100)
        fig = create_bar_chart(
            sorted_df,
            'Name',
            'Global_Sales',
            'Top 100 Games by Global Sales',
            width=1400  # Increase width for better x-axis label spacing
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Pie chart: Top 6 platforms by number of games
        top_platforms = videogames_df['Platform'].value_counts().head(6).reset_index()
        top_platforms.columns = ['Platform', 'Game_Count']
        fig = create_pie_chart(
            top_platforms,
            'Platform',
            'Game_Count',
            'Top 6 Platforms by Number of Games'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Improved scatter plot: Rank vs Global_Sales (Top 200), colored by Global_Sales
        if 'EU_Sales' in videogames_df.columns and 'NA_Sales' in videogames_df.columns:
            scatter_fig = px.scatter(
                videogames_df,
                x='EU_Sales',
                y='NA_Sales',
                color='NA_Sales',
                color_continuous_scale='Plasma',
                title='EU_Sales vs NA-Sales',
                template='plotly_white'
            )
            scatter_fig.update_layout(
                height=500,
                title_font_size=20,
                title_font_color="#4b6cb7",
                xaxis_title='Rank (by Global Sales)',
                yaxis_title='Global Sales (Millions)',
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            st.plotly_chart(scatter_fig, use_container_width=True)
        
        # Restore heatmap: Platform vs Genre by average Global_Sales
        if all(col in videogames_df.columns for col in ['Platform', 'Genre', 'Global_Sales']):
            fig = create_heatmap(
                videogames_df,
                'Platform',
                'Genre',
                'Global_Sales',
                'Heatmap: Platform vs Genre by Avg Global Sales'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        # Restore raw data table (first 50 rows)
        st.markdown("### 📋 Raw Data")
        st.dataframe(videogames_df.head(50), use_container_width=True)
        # 2D scatter plot: Year vs Global_Sales (Top 200), colored by Global_Sales
def steamdata_dashboard():
    st.markdown("## 🚀 Steam Data Analysis")
    steam_df = fetch_steamdata_data()
    if not steam_df.empty:
        steam_df['copiesSold'] = pd.to_numeric(steam_df['copiesSold'].astype(str).str.replace(',', ''), errors='coerce')
        steam_df['reviewScore'] = pd.to_numeric(steam_df['reviewScore'], errors='coerce')
        steam_df['revenue'] = pd.to_numeric(steam_df['revenue'].astype(str).str.replace(',', ''), errors='coerce')
        steam_df['avgPlaytime'] = pd.to_numeric(steam_df['avgPlaytime'], errors='coerce')
        # Bar chart: Top 100 games (no sorting)
        fig = create_bar_chart(
            steam_df.head(100),
            'name',
            'copiesSold',
            'Top 100 Games by Copies Sold'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Pie chart: avgPlaytime distribution for first 6 games (first 100 rows)
        pie_df = steam_df.head(100).head(6)[['name', 'avgPlaytime']]
        fig = create_pie_chart(
            pie_df,
            'name',
            'avgPlaytime',
            'Average Playtime Distribution (Top 6 Games)'
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        # Restore original scatter plot: releaseDate vs copiesSold (2D, colored by copiesSold)
        if 'copiesSold' in steam_df.columns and 'revenue' in steam_df.columns:
            scatter_fig = px.scatter(
                steam_df,
                x='copiesSold',
                y='revenue',
                color='revenue',
                color_continuous_scale='Plasma',
                title='copiesSold vs Revenue (2D Scatter Plot, Colored by Copies Sold)',
                template='plotly_white'
            )
            scatter_fig.update_layout(
                height=500,
                title_font_size=20,
                title_font_color="#4b6cb7",
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            st.plotly_chart(scatter_fig, use_container_width=True)
        
        df_heat = steam_df.head(200).copy()
        df_heat['play_bin'] = pd.qcut(df_heat['avgPlaytime'], q=6, duplicates='drop')
        df_heat['score_bin'] = pd.qcut(df_heat['reviewScore'], q=6, duplicates='drop')
        pivot = df_heat.pivot_table(
            values='revenue',
            index='score_bin',
            columns='play_bin',
            aggfunc='mean'
        )
        hover_pivot = df_heat.pivot_table(
            values='copiesSold',
            index='score_bin',
            columns='play_bin',
            aggfunc='mean'
        )
        z = np.where(np.isnan(pivot.values), np.nan, pivot.values)
        hover_text = np.where(np.isnan(hover_pivot.values), '', hover_pivot.values)
        fig = go.Figure(
            data=go.Heatmap(
                z=z,
                x=[str(x) for x in pivot.columns],
                y=[str(y) for y in pivot.index],
                text=hover_text,
                hovertemplate='Avg Playtime: %{x}<br>Review Score: %{y}<br>Avg Revenue: %{z}<br>Avg Copies Sold: %{text}<extra></extra>',
                colorscale='Magma',
                colorbar=dict(title='Avg Revenue'),
                zmin=np.nanmin(pivot.values),
                zmax=np.nanmax(pivot.values)
            )
        )
        fig.update_layout(
            title="Heatmap: Avg Playtime vs Review Score by Avg Revenue (First 200)",
            xaxis_title="Avg Playtime (quantile bins)",
            yaxis_title="Review Score (quantile bins)",
            height=700,
            width=700,
            title_font_size=20,
            title_font_color="#4b6cb7"
        )
        st.plotly_chart(fig, use_container_width=True)
        # Raw data table (show only first 50 rows)
        st.markdown("### 📋 Raw Data")
        st.dataframe(steam_df.head(50), use_container_width=True)
    else:
        st.warning("No SteamData available.")

def gamingtrends_dashboard():
    st.markdown("## 📈 Gaming Trends Analysis")
    trends_df = fetch_gamingtrends_data()
    if not trends_df.empty:
        # Clean up columns
        # Rename columns for easier access
        trends_df = trends_df.rename(columns={
            'Revenue (Millions $)': 'Revenue',
            'Players (Millions)': 'Players',
            'Peak Concurrent Players': 'peak_concurrent_players',
            'Metacritic Score': 'metacritic_score'
        })
        trends_df['Revenue'] = pd.to_numeric(trends_df['Revenue'], errors='coerce')
        trends_df['peak_concurrent_players'] = pd.to_numeric(trends_df['peak_concurrent_players'], errors='coerce')
        trends_df['Players'] = pd.to_numeric(trends_df['Players'], errors='coerce')
        trends_df['metacritic_score'] = pd.to_numeric(trends_df['metacritic_score'], errors='coerce')
        # Bar chart: Game Title vs Revenue
        if 'Game Title' in trends_df.columns and 'Revenue' in trends_df.columns:
            fig = create_bar_chart(
                trends_df.head(100),
                'Game Title',
                'Revenue',
                'Game Title vs Revenue (First 100)'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        # Pie chart: top 6 Game Title by peak_concurrent_players
        if 'Game Title' in trends_df.columns and 'peak_concurrent_players' in trends_df.columns:
            grouped_peak_players = trends_df.head(100).groupby('Game Title')['peak_concurrent_players'].sum()
            sorted_peak_players = grouped_peak_players.sort_values(ascending=False)
            top_pie = sorted_peak_players.head(6).reset_index()
            fig = create_pie_chart(
                top_pie,
                'Game Title',
                'peak_concurrent_players',
                'Top 6 Games by Peak Concurrent Players'
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        # Scatter plot: Game Title vs Players (2D, colored by Players)
        if 'Game Title' in trends_df.columns and 'Players' in trends_df.columns:
            
            scatter_fig = px.scatter(
                trends_df,
                x='Game Title',
                y='Players',
                color='Players',
                color_continuous_scale='Plasma',
                title='Game Title vs Players (2D Scatter Plot, Colored by Players)',
                template='plotly_white'
            )
            scatter_fig.update_layout(
                height=500,
                title_font_size=20,
                title_font_color="#4b6cb7",
                xaxis_title_font_size=14,
                yaxis_title_font_size=14
            )
            st.plotly_chart(scatter_fig, use_container_width=True)
        # Heatmap: metacritic_score (binned) vs Genre by avg Revenue, hover shows avg Players
        if all(col in trends_df.columns for col in ['metacritic_score', 'Genre', 'Revenue', 'Players']):
            import numpy as np
            import plotly.graph_objects as go
            df_heat = trends_df.head(100).copy()
            df_heat['score_bin'] = pd.qcut(df_heat['metacritic_score'], q=6, duplicates='drop')
            pivot = df_heat.pivot_table(
                values='Revenue',
                index='Genre',
                columns='score_bin',
                aggfunc='mean'
            )
            hover_pivot = df_heat.pivot_table(
                values='Players',
                index='Genre',
                columns='score_bin',
                aggfunc='mean'
            )
            z = np.where(np.isnan(pivot.values), np.nan, pivot.values)
            hover_text = np.where(np.isnan(hover_pivot.values), '', hover_pivot.values)
            fig = go.Figure(
                data=go.Heatmap(
                    z=z,
                    x=[str(x) for x in pivot.columns],
                    y=[str(y) for y in pivot.index],
                    text=hover_text,
                    hovertemplate='Metacritic Score: %{x}<br>Genre: %{y}<br>Avg Revenue: %{z}<br>Avg Players: %{text}<extra></extra>',
                    colorscale='Viridis',
                    colorbar=dict(title='Avg Revenue'),
                    zmin=np.nanmin(pivot.values),
                    zmax=np.nanmax(pivot.values)
                )
            )
            fig.update_layout(
                title="Heatmap: Metacritic Score vs Genre by Avg Revenue (First 100)",
                xaxis_title="Metacritic Score (quantile bins)",
                yaxis_title="Genre",
                height=700,
                width=700,
                title_font_size=20,
                title_font_color="#4b6cb7"
            )
            st.plotly_chart(fig, use_container_width=True)
        # Data table (show only first 50 rows)
        st.markdown("### 📋 Raw Data")
        st.dataframe(trends_df.head(50), use_container_width=True)
    else:
        st.warning("No GamingTrends data available.")

def main_data_analysis_dashboard():
    st.markdown("""
    <h1 style='text-align:center; color:#4b6cb7; font-size:2.5rem; margin-bottom:0.5em;'>📊 Unified Data Analysis: Esports & Casual Gamers</h1>
    """, unsafe_allow_html=True)
    st.info("Explore the intersection of competitive Esports and the world of Casual Gaming with rich, interactive analytics and insights.")

    # --- Field Abbreviations/Explanations ---
    st.markdown("""
    <div style='background: linear-gradient(90deg, #e0eafc 0%, #cfdef3 100%); padding:1em; border-radius:10px; margin-bottom:1em;'>
    <b style='font-size:1.2em;'>What is <span style='color:#4b6cb7;'>Esports</span>?</b><br>
    <span style='color:#222;'>Esports refers to organized, competitive video gaming where professional players and teams compete in tournaments for prestige and substantial prize pools. It is a rapidly growing industry with global reach, passionate fanbases, and a strong digital presence.</span><br><br>
    <b style='font-size:1.2em;'>What are <span style='color:#4b6cb7;'>Casual Gamers</span>?</b><br>
    <span style='color:#222;'>Casual Gamers are individuals who play games for fun, relaxation, and entertainment, often across a wide variety of platforms and genres. Their choices and trends drive the mainstream gaming industry, influencing which games become global hits.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='display:flex; gap:2em;'>
      <div style='flex:1;'>
        <b>🎮 Esports Data Includes:</b>
        <ul>
          <li><b>Countries:</b> Top-earning nations, player bases, and favorite games.</li>
          <li><b>Players:</b> Highest-earning pros, their main games, and earnings share.</li>
          <li><b>Teams:</b> Leading organizations, revenues, and tournament activity.</li>
          <li><b>Tournaments:</b> Major events, prize pools, and featured games.</li>
        </ul>
      </div>
      <div style='flex:1;'>
        <b>🕹️ Casual Gamers Data Includes:</b>
        <ul>
          <li><b>Videogames:</b> Best-selling titles, platforms, and review scores.</li>
          <li><b>SteamData:</b> Steam's top games by sales, playtime, and reviews.</li>
          <li><b>GamingTrends:</b> Industry-wide revenue, player base, and trending genres.</li>
        </ul>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Data Fetching ---
    countries_df = fetch_countries_data()
    players_df = fetch_players_data()
    teams_df = fetch_teams_data()
    tournaments_df = fetch_tournaments_data()
    videogames_df = fetch_videogames_data()
    steam_df = fetch_steamdata_data()
    trends_df = fetch_gamingtrends_data()

    # --- Combined/Comparative Graphs ---
    st.markdown("""
    <h2 style='color:#4b6cb7; margin-top:2em;'>🌐 Esports vs. Casual Gamers: Key Comparisons</h2>
    """, unsafe_allow_html=True)
    # Stack the two graphs vertically for better visibility
    # Esports: Top 10 countries vs top 10 teams by earnings/revenue
    if not countries_df.empty and not teams_df.empty:
        combined = pd.DataFrame({
            'Country': countries_df.sort_values('total_earnings', ascending=False)['name'].head(10),
            'Country Earnings': countries_df.sort_values('total_earnings', ascending=False)['total_earnings'].head(10).values,
            'Team': teams_df.sort_values('revenue', ascending=False)['team_name'].head(10).values,
            'Team Revenue': teams_df.sort_values('revenue', ascending=False)['revenue'].head(10).values
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(x=combined['Country'], y=combined['Country Earnings'], name='Top Countries Earnings', marker_color='#4b6cb7'))
        fig.add_trace(go.Bar(x=combined['Team'], y=combined['Team Revenue'], name='Top Teams Revenue', marker_color='#34a0a4'))
        fig.update_layout(barmode='group', title='Top 10 Countries vs Top 10 Teams (Earnings/Revenue)',
                         xaxis_title='Country / Team', yaxis_title='Earnings / Revenue',
                         title_font_size=18, title_font_color="#4b6cb7", plot_bgcolor='#f8fafc', height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for combined Esports bar chart.")
    # Casual: Top 10 games by global sales vs top 10 Steam games by copies sold
    if not videogames_df.empty and not steam_df.empty:
        vg = videogames_df.sort_values('Global_Sales', ascending=False).head(10)
        stg = steam_df.sort_values('copiesSold', ascending=False).head(10).copy()
        # Convert Steam copiesSold to millions for fair comparison
        stg['copiesSold_millions'] = stg['copiesSold'] / 1_000_000
        fig = go.Figure()
        fig.add_trace(go.Bar(x=vg['Name'], y=vg['Global_Sales'], name='Top Games Global Sales (Millions)', marker_color='#4b6cb7'))
        fig.add_trace(go.Bar(x=stg['name'], y=stg['copiesSold_millions'], name='Top Steam Games Copies Sold (Millions)', marker_color='#34a0a4'))
        fig.update_layout(barmode='group', title='Top 10 Videogames vs Top 10 Steam Games (Millions)',
                         xaxis_title='Game', yaxis_title='Sales / Copies Sold (Millions)',
                         title_font_size=18, title_font_color="#4b6cb7", plot_bgcolor='#f8fafc', height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for combined Casual Gamers bar chart.")

    # --- Trend Line: Esports Prize Pools vs. Industry Revenue ---
    st.markdown("""
    <h2 style='color:#4b6cb7; margin-top:2em;'>📈 Esports Prize Pools vs. Gaming Industry Revenue</h2>
    <div style='color:#444; margin-bottom:1em;'>See how the growth of Esports prize pools compares to the overall gaming industry's revenue trends.</div>
    """, unsafe_allow_html=True)
    if not tournaments_df.empty and not trends_df.empty and 'Release Year' in trends_df.columns:
        # Extract and filter years
        prize_by_year = tournaments_df.copy()
        if 'year' not in prize_by_year.columns:
            prize_by_year['year'] = prize_by_year['tournament_name'].str.extract(r'(\d{4})').astype(float)
        prize_by_year = prize_by_year[(prize_by_year['year'] >= 1980) & (prize_by_year['year'] <= 2025)]
        prize_by_year = prize_by_year.groupby('year')['prize_pool'].sum().reset_index()
        revenue_by_year = trends_df.copy()
        revenue_by_year = revenue_by_year[(revenue_by_year['Release Year'] >= 1980) & (revenue_by_year['Release Year'] <= 2025)]
        revenue_by_year = revenue_by_year.groupby('Release Year')['Revenue (Millions $)'].sum().reset_index()
        # Align years
        common_years = set(prize_by_year['year']).intersection(set(revenue_by_year['Release Year']))
        prize_by_year = prize_by_year[prize_by_year['year'].isin(list(common_years))]
        revenue_by_year = revenue_by_year[revenue_by_year['Release Year'].isin(list(common_years))]
        # Plot with dual y-axis
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prize_by_year['year'], y=prize_by_year['prize_pool'], mode='lines+markers', name='Esports Prize Pool (Millions $)', line=dict(color='#4b6cb7', width=3), yaxis='y1'))
        fig.add_trace(go.Scatter(x=revenue_by_year['Release Year'], y=revenue_by_year['Revenue (Millions $)'], mode='lines+markers', name='Gaming Industry Revenue (Millions $)', line=dict(color='#34a0a4', width=3, dash='dash'), yaxis='y2'))
        fig.update_layout(
            title='Prize Pools vs. Industry Revenue Over Time',
            xaxis_title='Year',
            yaxis=dict(title='Esports Prize Pool (Millions $)', titlefont=dict(color='#4b6cb7'), tickfont=dict(color='#4b6cb7')),
            yaxis2=dict(title='Industry Revenue (Millions $)', titlefont=dict(color='#34a0a4'), tickfont=dict(color='#34a0a4'), overlaying='y', side='right'),
            legend=dict(x=0.01, y=0.99),
            title_font_size=18, title_font_color="#4b6cb7", plot_bgcolor='#f8fafc', height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for time trend analysis.")

    # --- Correlation Heatmap: Esports vs Casual Metrics ---
    st.markdown("""
    <h2 style='color:#4b6cb7; margin-top:2em;'>🔗 Correlation: Esports & Casual Metrics</h2>
    """, unsafe_allow_html=True)
    combined_data = pd.DataFrame()
    if not countries_df.empty:
        combined_data['Country_Earnings'] = countries_df['total_earnings'].head(20)
    if not players_df.empty:
        combined_data['Player_Earnings'] = players_df['total_earnings'].head(20)
    if not teams_df.empty:
        combined_data['Team_Revenue'] = teams_df['revenue'].head(20)
    if not tournaments_df.empty:
        combined_data['Tournament_Prize_Pool'] = tournaments_df['prize_pool'].head(20)
    if not videogames_df.empty:
        combined_data['Game_Global_Sales'] = videogames_df['Global_Sales'].head(20)
    if not steam_df.empty:
        combined_data['Steam_Copies_Sold'] = steam_df['copiesSold'].head(20)
    if not trends_df.empty and 'Revenue (Millions $)' in trends_df.columns:
        combined_data['Industry_Revenue'] = trends_df['Revenue (Millions $)'].head(20)
    if not combined_data.empty:
        corr_matrix = combined_data.corr()
        fig = px.imshow(
            corr_matrix,
            title="Correlation Matrix: Esports & Casual Gamers Metrics",
            template="plotly_white",
            color_continuous_scale="RdBu"
        )
        fig.update_layout(title_font_size=18, title_font_color="#4b6cb7", height=500, plot_bgcolor='#f8fafc')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for correlation analysis.")

    # --- Key Insights Section ---
    st.markdown("""
    <h2 style='color:#4b6cb7; margin-top:2em;'>💡 Key Insights & Takeaways</h2>
    <ul style='font-size:1.1em; color:#333;'>
      <li><b>Esports</b> is driven by a small number of high-earning countries, teams, and players, with prize pools growing rapidly in recent years.</li>
      <li><b>Casual Gaming</b> dominates in terms of player base and sales, with trends shifting quickly based on new releases and platform popularity.</li>
      <li>There is a strong correlation between the popularity of certain games in Esports and their commercial success among casual gamers.</li>
      <li>Industry revenue growth often parallels the rise in Esports prize pools, showing the interconnectedness of both fields.</li>
      <li>Understanding both Esports and Casual Gamers is crucial for anyone interested in the future of gaming, whether as a player, fan, or industry professional.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.success("This analysis section gives you a holistic, visually engaging view of both Esports and Casual Gamers. Use the sidebar to explore more details on each field!")

def behavioral_insights_gaming_engagement():
    # ML setup (must be before the form/UI)
    df = pd.read_csv('main_predict.csv')
    X = df.drop(['PlayerID', 'EngagementLevel'], axis=1)
    y = df['EngagementLevel']
    cat_cols = ['Gender', 'Location', 'GameGenre', 'GameDifficulty']
    num_cols = [col for col in X.columns if col not in cat_cols]
    encoders = {col: LabelEncoder().fit(X[col]) for col in cat_cols}
    for col in cat_cols:
        X[col] = encoders[col].transform(X[col])
    # Encode y
    y_encoder = LabelEncoder()
    y = y_encoder.fit_transform(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBClassifier(max_depth=6,learning_rate=0.1,booster='gbtree',colsample_bytree=0.8,tree_method='auto',
    objective='multi:softmax',n_jobs=1,n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Modern, minimal page-wide background and font
    st.markdown("""
    <style>
    html, body, .stApp {
        background: linear-gradient(120deg, #f8fafc 0%, #e0eafc 100%) !important;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
    }
    .info-card {
        background: rgba(255,255,255,0.92);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(75,108,183,0.10);
        border: 1.5px solid #e0eafc;
        padding: 2.2rem 2rem 1.5rem 2rem;
        max-width: 700px;
        margin: 2.2rem auto 2.2rem auto;
    }
    .info-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #3a4a6b;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .info-desc {
        text-align: center;
        color: #444;
        font-size: 1.13rem;
        margin-bottom: 1.2rem;
        font-weight: 400;
    }
    .tech-used {
        text-align: center;
        color: #4b6cb7;
        font-size: 1.05rem;
        margin-bottom: 0.2rem;
        font-weight: 500;
    }
    .glass-form {
        background: rgba(255,255,255,0.82);
        border-radius: 20px;
        box-shadow: 0 4px 24px rgba(75,108,183,0.10);
        border: 1.5px solid #e0eafc;
        backdrop-filter: blur(7px);
        -webkit-backdrop-filter: blur(7px);
        padding: 2.5rem 2rem 2rem 2rem;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 2.2rem;
    }
    .form-header {
        text-align:center;
        font-size:1.35rem;
        color:#4b6cb7;
        margin-bottom:1.5rem;
        font-weight:700;
        letter-spacing:0.5px;
    }
    .modern-accuracy {
        display:inline-block;
        background: linear-gradient(90deg, #4b6cb7 0%, #34a0a4 100%);
        color:#fff;
        padding:0.7em 2em;
        border-radius: 999px;
        font-weight:600;
        font-size:1.12em;
        margin-bottom:1.5em;
        box-shadow:0 2px 12px rgba(52,160,164,0.13);
        border: none;
        letter-spacing: 0.5px;
    }
    .modern-result-card {
        background: #4b6cb7;
        color: #fff;
        border-radius: 16px;
        padding: 1.5rem 1.2rem 1.2rem 1.2rem;
        font-size: 1.35rem;
        font-weight: 600;
        text-align: center;
        margin: 0 auto 1.2rem auto;
        box-shadow: 0 2px 12px rgba(52,160,164,0.10);
        letter-spacing: 0.5px;
        max-width: 500px;
    }
    .centered-img {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto 1.2rem auto;
        width: 100%;
    }
    .feedback-msg {
        font-size: 1.08rem;
        margin-bottom: 1.2rem;
        color: #333;
        text-align: center;
        font-weight: 400;
    }
    .suggestion-msg {
        font-size: 1.08rem;
        margin-bottom: 1.5rem;
        color: #4b6cb7;
        text-align: center;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    # Info card at the top
    st.markdown('''<div class="info-card">
        <div class="info-title">🧑‍💻 Behavioral Insights into Gaming Engagement</div>
        <div class="info-desc">Welcome! This page uses machine learning to predict your gaming engagement level based on your profile. Enter your details below and discover your engagement type, get a personalized suggestion, and see a fun visual result.<br><br><b>How it works:</b> We use an <b>XGBoost</b> model, a state-of-the-art machine learning algorithm, trained on real gaming data to classify your engagement as High, Medium, or Low.</div>
        <div class="tech-used">🔧 <b>Tech Used:</b> <b>Streamlit</b>, <b>XGBoost</b>, <b>Pandas</b>, <b>Python</b>, <b>Glassmorphism CSS</b></div>
    </div>''', unsafe_allow_html=True)

    # --- User Input Form ---
    with st.form("prediction_form"):
        st.markdown('<div class="form-header">📝 Enter your gaming profile details below</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("🔢 Age", min_value=10, max_value=100, value=25, key="age", help="Enter your age in years.")
            gender_options = list(encoders['Gender'].classes_) if encoders['Gender'].classes_ is not None else []
            gender = st.selectbox("🚻 Gender", gender_options, key="gender", help="Select your gender.")
            location_options = list(encoders['Location'].classes_) if encoders['Location'].classes_ is not None else []
            location = st.selectbox("🌍 Location", location_options, key="location", help="Select your region.")
            game_genre_options = list(encoders['GameGenre'].classes_) if encoders['GameGenre'].classes_ is not None else []
            game_genre = st.selectbox("🎮 Game Genre", game_genre_options, key="game_genre", help="Favorite type of game you play.")
            play_time = st.number_input("⏰ Play Time (Hours)", min_value=0.0, max_value=100.0, value=10.0, key="play_time", help="Average hours spent gaming per week.")
            in_game_purchases = st.selectbox("💸 In-Game Purchases", [0, 1], key="in_game_purchases", help="Have you made in-game purchases? 1=Yes, 0=No.")
        with col2:
            game_difficulty_options = list(encoders['GameDifficulty'].classes_) if encoders['GameDifficulty'].classes_ is not None else []
            game_difficulty = st.selectbox("🎯 Game Difficulty", game_difficulty_options, key="game_difficulty", help="Preferred game difficulty.")
            sessions_per_week = st.number_input("📅 Sessions Per Week", min_value=0, max_value=50, value=5, key="sessions_per_week", help="How many times do you play per week?")
            avg_session_duration = st.number_input("🕒 Avg Session Duration (Minutes)", min_value=1, max_value=500, value=60, key="avg_session_duration", help="Average duration of a gaming session.")
            player_level = st.number_input("🏅 Player Level", min_value=1, max_value=100, value=10, key="player_level", help="Your in-game level.")
            achievements_unlocked = st.number_input("🏆 Achievements Unlocked", min_value=0, max_value=100, value=10, key="achievements_unlocked", help="Number of achievements unlocked.")
        st.markdown('</div>', unsafe_allow_html=True)
        # Show model accuracy
        from sklearn.metrics import accuracy_score
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        st.markdown(f'<div class="modern-accuracy">Model Accuracy: {acc*100:.2f}%</div>', unsafe_allow_html=True)
        submit = st.form_submit_button("🎮 Predict Engagement Level")

    if submit:
        import time
        with st.spinner('Analyzing your gaming profile...'):
            time.sleep(1.1)
            input_dict = {
                'Age': age,
                'Gender': encoders['Gender'].transform([gender])[0],
                'Location': encoders['Location'].transform([location])[0],
                'GameGenre': encoders['GameGenre'].transform([game_genre])[0],
                'PlayTimeHours': play_time,
                'InGamePurchases': in_game_purchases,
                'GameDifficulty': encoders['GameDifficulty'].transform([game_difficulty])[0],
                'SessionsPerWeek': sessions_per_week,
                'AvgSessionDurationMinutes': avg_session_duration,
                'PlayerLevel': player_level,
                'AchievementsUnlocked': achievements_unlocked
            }
            input_df = pd.DataFrame([input_dict])
            pred = model.predict(input_df)[0]
            pred_label = y_encoder.inverse_transform([pred])[0]

        # Show result with image, emoji, feedback, and centered card
        badge = {'High': '🔥', 'Medium': '🎮', 'Low': '🌱'}
        feedback = {
            'High': "You're a highly engaged gamer! Keep enjoying and maybe try streaming or joining tournaments!",
            'Medium': "You're moderately engaged. Try exploring new genres or playing with friends for more fun!",
            'Low': "You have a casual approach to gaming. Play at your own pace and enjoy your free time!"
        }
        suggestions = {
            'High': "💡 <b>Suggestion:</b> Consider joining online tournaments or starting a gaming blog to share your passion!",
            'Medium': "💡 <b>Suggestion:</b> Try out new genres or multiplayer games to boost your engagement!",
            'Low': "💡 <b>Suggestion:</b> Explore casual games or play with friends for a more enjoyable experience!"
        }
        st.markdown(f'<div class="modern-result-card">{badge.get(pred_label, "")} Predicted Engagement Level: <span style="font-size:1.5em;">{pred_label}</span> </div>', unsafe_allow_html=True)
        # Centered image below the result card
        img_url = ""
        img_caption = ""
        if pred_label == 'High':
            st.balloons()
            img_url = "https://miro.medium.com/v2/resize:fit:1400/1*b4G-IzJAi_q2OUhyieSNNw.png"
            img_caption = "Highly Engaged Gamer!"
        elif pred_label == 'Medium':
            img_url = "https://img.freepik.com/premium-photo/bearded-man-…ller-showing-excited-expression_116547-125573.jpg"
            img_caption = "Moderately Engaged Gamer!"
        else:
            st.snow()
            img_url = "https://www.allprodad.com/wp-content/uploads/2021/06/07-01-21-kids-playing-video-games-scaled.jpg"
            img_caption = "Low Engagement Detected"
        st.markdown('<div class="centered-img">', unsafe_allow_html=True)
        # st.image(img_url,align="center", caption=img_caption, width=560)
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src="{img_url}" alt="image" style="height:450px; width:600px;">
                <p style='color: grey;'>{img_caption}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        # Show feedback and suggestion below the image
        st.markdown(f'<div class="feedback-msg">{feedback.get(pred_label, "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="suggestion-msg">{suggestions.get(pred_label, "")}</div>', unsafe_allow_html=True)

# --- Main Application with Two-Level Navigation ---
def main():
    main_section = st.sidebar.radio("Select User Type:", ["General", "Esports", "Casual Gamers", "Behavioral Insights into Gaming Engagement"])
    sub_section = None
    if main_section == "General":
        st.sidebar.title("Navigation")
        general_section = st.sidebar.selectbox("Choose a section:", ["Overview", "Data Analysis"])
        # Routing logic for General
        if general_section == "Overview":
            overview_dashboard()
        elif general_section == "Data Analysis":
            main_data_analysis_dashboard()  # This should be the function for Data Analysis section
    elif main_section == "Esports":
        st.sidebar.title("Navigation")
        sub_section = st.sidebar.selectbox("Select Esports Field:", ["Countries", "Players", "Teams", "Tournaments"])
        # Routing logic for Esports
        if sub_section == "Countries":
            countries_dashboard()
        elif sub_section == "Players":
            players_dashboard()
        elif sub_section == "Teams":
            teams_dashboard()
        elif sub_section == "Tournaments":
            tournaments_dashboard()
    elif main_section == "Casual Gamers":
        st.sidebar.title("Navigation")
        sub_section = st.sidebar.selectbox("Select Casual Gamers Field:", ["Videogames", "SteamData", "GamingTrends"])
        # Routing logic for Casual Gamers
        if sub_section == "Videogames":
            videogames_dashboard()
        elif sub_section == "SteamData":
            steamdata_dashboard()
        elif sub_section == "GamingTrends":
            gamingtrends_dashboard()
    elif main_section == "Behavioral Insights into Gaming Engagement":
        behavioral_insights_gaming_engagement()

if __name__ == "__main__":
    main() 