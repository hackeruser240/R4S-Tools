# File: functions_folder/ranking_forecast_model.py

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

def load_sample_data(keyword="Sample Keyword"):
    """
    Returns sample keyword ranking data for a given keyword.
    """
    dates = pd.date_range(start="2025-08-01", periods=60)
    data = pd.DataFrame({
        "keyword": keyword,
        "date": dates,
        "rank": np.clip(20 - 0.1 * np.arange(60) + np.random.normal(0, 1, 60), 1, 50),
        "search_volume": np.random.randint(1000, 3000, size=60),
        "clicks": np.random.randint(100, 500, size=60)
    })
    return data

def ranking_forecast_model(data: pd.DataFrame, forecast_horizon: int = 30):
    """
    Forecasts future keyword rankings using Prophet and XGBoost.
    Returns forecasted ranks and model diagnostics.
    """
    if "keyword" not in data.columns:
        raise ValueError("Input data must contain a 'keyword' column.")

    keyword = data["keyword"].iloc[0]
    df = data.copy()
    df['ds'] = pd.to_datetime(df['date'])
    df['y'] = df['rank']

    # Prophet model
    prophet_model = Prophet()
    prophet_model.fit(df[['ds', 'y']])
    future = prophet_model.make_future_dataframe(periods=forecast_horizon)
    prophet_forecast = prophet_model.predict(future)
    prophet_preds = prophet_forecast[['ds', 'yhat']].tail(forecast_horizon)

    # XGBoost model
    df['dayofyear'] = df['ds'].dt.dayofyear
    X_train = df[['dayofyear', 'search_volume', 'clicks']]
    y_train = df['rank']

    xgb_model = XGBRegressor()
    xgb_model.fit(X_train, y_train)

    future_days = future.tail(forecast_horizon)
    future_features = pd.DataFrame({
        'dayofyear': future_days['ds'].dt.dayofyear,
        'search_volume': np.random.randint(1000, 3000, size=forecast_horizon),
        'clicks': np.random.randint(100, 500, size=forecast_horizon)
    })

    xgb_preds = xgb_model.predict(future_features)

    # Ensemble prediction
    final_preds = 0.5 * prophet_preds['yhat'].values + 0.5 * xgb_preds
    forecast = pd.DataFrame({
        "date": future_days['ds'].values,
        "predicted_rank": final_preds
    })

    # Diagnostics
    prophet_rmse = np.sqrt(mean_squared_error(y_train, prophet_model.predict(df[['ds']])['yhat']))
    xgb_rmse = np.sqrt(mean_squared_error(y_train, xgb_model.predict(X_train)))

    return {
        "keyword": keyword,
        "forecast": forecast.to_dict(orient="records"),
        "model_metadata": {
            "prophet_rmse": round(prophet_rmse, 2),
            "xgboost_rmse": round(xgb_rmse, 2),
            "ensemble_strategy": "weighted_average"
        }
    }

def visualize_forecast_results(forecast_data: dict) -> str:
    """
    Generates an interactive Plotly HTML chart for keyword ranking forecast.
    Returns HTML string to embed in Flask template.
    """
    keyword = forecast_data.get("keyword", "Unknown Keyword")
    forecast = forecast_data.get("forecast", [])

    dates = [row["date"] for row in forecast]
    ranks = [row["predicted_rank"] for row in forecast]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=ranks,
        mode='lines+markers',
        name='Predicted Rank',
        line=dict(color='royalblue', width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=f"📈 Forecasted Ranking for '{keyword}'",
        xaxis_title="Date",
        yaxis_title="Predicted Rank (lower is better)",
        yaxis_autorange="reversed",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Return as HTML div string
    return pio.to_html(fig, full_html=False)

def generate_forecast_summary(forecast_data: dict) -> str:
    """
    Generates a natural-language summary of the forecast trend.
    """
    keyword = forecast_data.get("keyword", "Unknown Keyword")
    forecast = forecast_data.get("forecast", [])

    if not forecast:
        return "No forecast data available."

    ranks = [row["predicted_rank"] for row in forecast]
    dates = [row["date"] for row in forecast]

    start_rank = ranks[0]
    end_rank = ranks[-1]
    best_rank = min(ranks)
    best_date = pd.to_datetime(dates[ranks.index(best_rank)]).strftime("%d-%b-%Y")

    trend = "improving" if end_rank < start_rank else "declining" if end_rank > start_rank else "stable"
    change = round(abs(end_rank - start_rank), 2)

    summary = (
        f"📊 The keyword *'{keyword}'* is forecasted to be {trend} over the next {len(ranks)} days. "
        f"It starts at rank {round(start_rank, 2)} and ends at rank {round(end_rank, 2)}, "
        f"with a total change of {change} points. "
        f"The best predicted rank is {round(best_rank, 2)} on {best_date}."
    )

    return summary

if __name__ == "__main__":
    keyword = "seo optimization"
    sample_data = load_sample_data(keyword=keyword)
    result = ranking_forecast_model(sample_data, forecast_horizon=30)
    summary_text = generate_forecast_summary(result)

    print(f"\n🔍 Forecast for keyword: {result['keyword']}\n")
    print("📈 Forecast Output (first 5 days):")
    for row in result["forecast"][:5]:
        print(row)

    print("\n📊 Model Metadata:")
    print(result["model_metadata"])

    # Visualization
    html_chart = visualize_forecast_results(result)

    # Save chart + summary to file
    output_path = f"static/forecast_chart_{keyword.replace(' ', '_')}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Forecast for {keyword}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f9f9f9; padding: 20px; border-left: 4px solid #007BFF; margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <h1>📈 Forecast for Keyword: {keyword}</h1>
            <div class="summary">
                <h4>🧠 Summary</h4>
                <p>{summary_text}</p>
            </div>
            {html_chart}
        </body>
        </html>
        """)

    print(f"\n📊 Interactive chart + summary saved to: {output_path}")
    print("💡 Open this file in your browser to view the forecast and summary.")