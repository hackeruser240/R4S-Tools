# File: functions_folder/trend_visualizer.py

import pandas as pd
import plotly.express as px
import numpy as np


def plot_trends(df):
    """
    Plots keyword performance trends over time using Plotly.
    Args:
        df (pd.DataFrame): Must contain 'keyword', 'date', 'value' columns
    Returns:
        str: HTML div containing the Plotly chart
    """
    df['date'] = pd.to_datetime(df['date'])
    fig = px.line(df, x='date', y='value', color='keyword', markers=True,
                  title='Keyword Performance Over Time')
    fig.update_layout(template='plotly_white')
    return fig.to_html(full_html=False)

def create_sample_data():
    keywords = [
        "MOF membrane",
        "crystallization",
        "substrate engineering",
        "gas separation",
        "vapor-phase synthesis",
        "bioinformatics pipeline",
        "template-driven catalysis",
        "mixed-linker MOF",
        "adsorption kinetics",
        "nanoporous materials"
    ]

    dates = pd.date_range(start="2024-10-01", end="2025-09-01", freq="MS")  # Monthly start dates

    # Generate synthetic data
    data = []
    rng = np.random.default_rng(seed=42)

    for keyword in keywords:
        base = rng.integers(100, 300)
        seasonal = np.sin(np.linspace(0, 2 * np.pi, len(dates))) * rng.integers(20, 60)
        noise = rng.normal(0, 25, len(dates))
        values = np.clip(base + seasonal + noise, 50, None).astype(int)

        for date, value in zip(dates, values):
            data.append({
                "keyword": keyword,
                "date": date.strftime("%Y-%m-%d"),
                "value": value
            })

    sample_data = pd.DataFrame(data)

    return sample_data

# 🔧 Local test block
if __name__ == '__main__':
    '''
        sample_data = pd.DataFrame([
            {"keyword": "MOF membrane", "date": "2025-01-01", "value": 120},
            {"keyword": "MOF membrane", "date": "2025-02-01", "value": 150},
            {"keyword": "crystallization", "date": "2025-01-01", "value": 80},
            {"keyword": "crystallization", "date": "2025-02-01", "value": 95},
        ])
    '''

    sample_data=create_sample_data()
    html_chart = plot_trends(sample_data)
    with open("static/trend_chart.html", "w", encoding="utf-8") as f:
        f.write(html_chart)
    print("✅ Chart saved to trend_chart.html")