# 💼 PortfolioSim

A modern, high-performance Investment Portfolio Simulator built with **Streamlit**, **Plotly**, and **MySQL**. It implements a simplified **Markowitz Modern Portfolio Theory** engine to generate risk-optimized investment recommendations.

![Aesthetic](https://img.shields.io/badge/Aesthetics-Premium-00ffa3?style=for-the-badge)
![Tech](https://img.shields.io/badge/Stack-Streamlit%20|%20MySQL-blue?style=for-the-badge)

## 🌟 Key Features

- **User Authentication**: Secure login and registration using `bcrypt` hashing.
- **Investor Profiles**: Create and manage multiple investment profiles based on age, income, and risk tolerance.
- **Smart Recommendation Engine**: Automatically selects and weights assets (Equity, Bonds, Property) based on your risk capacity (1–10) and goals.
- **Interactive Visualizations**: Real-time allocation pie charts and Risk vs. Return scatter plots using Plotly.
- **Portfolio Simulation**: Test your saved portfolios against simulated market sentiment to see potential gains/losses.
- **Premium UI**: Dark-mode glassmorphism design with custom CSS and Google Fonts (Syne & Space Mono).

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- MySQL Server

### 1. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file or set environment variables:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=PortfolioSim1
```
*Note: If not set, it defaults to the values in `config.py`.*

### 3. Run the App
```bash
streamlit run app.py
```
*The application will automatically initialize the database and tables on the first run.*

## 🛠️ Tech Stack
- **Frontend**: Streamlit (Python-based SPA)
- **Visuals**: Plotly Graph Objects
- **Data**: Pandas
- **Database**: MySQL (Connector/Python)
- **Security**: Bcrypt

## 📊 How the Engine Works
The simulator uses a simplified **Mean-Variance Optimization** (Markowitz) approach:
1. **Asset Selection**: Filters assets based on risk capacity and goal keywords.
2. **Weighting**: Uses Inverse-Volatility weighting for conservative profiles and Expected-Return weighting for aggressive ones.
3. **Metrics**: Calculates Portfolio Expected Return, Variance, and Sharpe Ratio.

---
Developed with ❤️ for the DIS Mini Project.
