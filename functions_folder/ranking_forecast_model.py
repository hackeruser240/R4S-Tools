# File: functions_folder/ranking_forecast_model.py

import pandas as pd
import numpy as np
from prophet import Prophet
from xgboost import XGBRegressor
import plotly.express as px
import os
import random

def generate_keywords(n=10):
    base_terms = [
        "MOF", "membrane", "crystallization", "substrate", "adsorption",
        "synthesis", "catalysis", "nanoporous", "linker", "separation",
        "template", "vapor-phase", "bioinformatics", "pipeline", "reactor",
        "porosity", "selectivity", "diffusion", "framework", "kinetics"
    ]

    keywords = []
    for _ in range(n):
        term1 = random.choice(base_terms)
        term2 = random.choice(base_terms)
        keyword = f"{term1}_{term2}"
        keywords.append(keyword)

    return keywords

def create_sample_data(keywords=None):
    if keywords is None:
        keywords = generate_keywords()

    dates = pd.date_range(start="2025-01-01", periods=12, freq="MS")
    data = []
    rng = np.random.default_rng(seed=90)

    for kw in keywords:
        base = rng.integers(5, 20)
        
        slope = rng.uniform(-10, 10)
        trend = base + slope * np.linspace(0, 1, len(dates))
        
        noise_level = rng.uniform(1, 10)
        noise = rng.normal(0, noise_level, len(dates))
        
        ranks = np.clip(trend + noise, 1, None).astype(int)
        for d, r in zip(dates, ranks):
            data.append({"keyword": kw, "ds": d, "y": r})

    return pd.DataFrame(data)

def forecast_with_prophet(df, keyword):
    df_kw = df[df['keyword'] == keyword][['ds', 'y']]
    if df_kw.dropna().shape[0] < 2:
        raise ValueError(f"Not enough data for keyword: {keyword}")
    model = Prophet()
    model.fit(df_kw)
    future = model.make_future_dataframe(periods=6, freq='MS')
    forecast = model.predict(future)
    forecast['keyword'] = keyword
    return forecast[['ds', 'yhat', 'keyword']]

def forecast_with_xgboost(df, keyword):
    df_kw = df[df['keyword'] == keyword].copy()
    if df_kw.shape[0] < 2:
        raise ValueError(f"Not enough data for keyword: {keyword}")
    df_kw['month'] = df_kw['ds'].dt.month
    df_kw['year'] = df_kw['ds'].dt.year
    X = df_kw[['month', 'year']]
    y = df_kw['y']
    model = XGBRegressor()
    model.fit(X, y)

    future_dates = pd.date_range(start=df_kw['ds'].max() + pd.DateOffset(months=1), periods=6, freq='MS')
    future_df = pd.DataFrame({
        'month': future_dates.month,
        'year': future_dates.year
    })
    preds = model.predict(future_df)
    return pd.DataFrame({
        'ds': future_dates,
        'yhat': preds,
        'keyword': keyword
    })

def plot_forecast(df_forecast):
    fig = px.line(df_forecast, x='ds', y='yhat', color='keyword', markers=True,
                  title='Forecasted Keyword Rankings')
    fig.update_layout(template='plotly_white')
    fig.update_yaxes(autorange='reversed')  # Lower rank = better
    return fig.to_html(full_html=False)

def generate_all_forecasts(df):
    """
    Generates forecasts for all keywords in the dataset using Prophet and XGBoost.
    Returns a dictionary of keyword → HTML chart.
    """
    charts = {}
    for kw in df['keyword'].unique():
        print("Keywords detected:", df['keyword'].unique())
        try:
            forecast_df = pd.concat([
                forecast_with_prophet(df, kw),
                forecast_with_xgboost(df, kw)
            ])
            chart_html = plot_forecast(forecast_df)
            charts[kw] = chart_html
        except Exception as e:
            print(f"⚠️ Skipping {kw}: {e}")
    return charts

# 🔧 Local test block
if __name__ == '__main__':
    df = create_sample_data()
    charts = generate_all_forecasts(df)
    os.makedirs("static", exist_ok=True)

    for kw, html in charts.items():
        filename = f"static/{kw}_forecast_chart.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Chart saved: {filename}")