#!/usr/bin/env python3
"""
Database Setup Script for Esports Analytics Dashboard
This script helps you set up the database and populate it with data.
"""

import subprocess
import sys
import os

def check_mysql_connection():
    """Check if MySQL is running and accessible"""
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        connection.close()
        print("✅ MySQL connection successful")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("💡 Make sure XAMPP/MySQL is running")
        return False

def run_data_scraper():
    """Run the data scraper to populate the database"""
    try:
        print("🚀 Running data scraper...")
        result = subprocess.run([sys.executable, "data_scraper.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Data scraper completed successfully!")
            print(result.stdout)
        else:
            print("❌ Data scraper failed:")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ Error running data scraper: {e}")
        return False

def main():
    print("🎮 Esports Analytics Dashboard - Database Setup")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists("data_scraper.py"):
        print("❌ data_scraper.py not found in current directory")
        return
    
    # Check MySQL connection
    if not check_mysql_connection():
        print("\n🔧 Please start your MySQL server (XAMPP) and try again")
        return
    
    # Run data scraper
    print("\n📊 Setting up database and populating with data...")
    if run_data_scraper():
        print("\n🎉 Setup completed successfully!")
        print("🚀 You can now run the dashboard with: streamlit run app.py")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 