# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 00:16:30 2025

@author: jjjimenez
"""

# -*- coding: utf-8 -*-
"""
Backtest Estrategia Value + Momentum para tickers financieros del S&P 500
Incluye curva de capital promedio
Autor: J3Viton (optimizado)
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
# Lista de tickers financieros del S&P 500
tickers_financials = ["JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "BK", "USB", "PNC"]

# Parámetros
START_DATE = "2015-01-01"
END_DATE = "2025-01-01"
SCORE_THRESHOLD = 1.0
ATR_MULT = 2

# 1️⃣ Función para obtener ratios y calcular Composite Value
def obtener_composite_value_tickers(tickers):
    data = []
    for t in tickers:
        try:
            info = yf.Ticker(t).get_info()
            data.append({
                "Ticker": t,
                "P/E": info.get("trailingPE", np.nan),
                "P/B": info.get("priceToBook", np.nan),
                "Sector": info.get("sector", "Unknown")
            })
        except Exception as e:
            print(f"Error con {t}: {e}")
    df = pd.DataFrame(data)
    df = df[(df["P/E"] > 5) & (df["P/E"] < 20) & (df["P/B"] > 0.4) & (df["P/B"] < 2)]
    if df.empty:
        return None
    z_scores = df[["P/E", "P/B"]].apply(lambda x: -(x - np.nanmean(x)) / np.nanstd(x))
    df["Composite Value"] = z_scores.mean(axis=1)
    df["Composite_z"] = (df["Composite Value"] - df["Composite Value"].mean()) / df["Composite Value"].std()
    return df[["Ticker", "Composite_z"]]

# 2️⃣ Función para calcular Momentum por regresión
def calcular_momentum_regresion_tickers(tickers, window_sma=20, window_reg=60):
    resultados = []
    for t in tickers:
        try:
            data = yf.download(t, period=f"{window_reg*2}d", interval="1d", progress=False)
            if data.empty:
                continue
            data["SMA"] = data["Close"].rolling(window_sma).mean()
            y = np.log(data["SMA"].dropna().values[-window_reg:])
            x = np.arange(len(y)).reshape(-1, 1)
            if len(y) < window_reg / 2:
                continue
            model = LinearRegression().fit(x, y)
            beta = model.coef_[0]
            resultados.append({"Ticker": t, "Momentum_beta": beta})
        except Exception as e:
            print(f"Error con {t}: {e}")
    df_mom = pd.DataFrame(resultados)
    if df_mom.empty:
        return None
    df_mom["Momentum_z"] = (df_mom["Momentum_beta"] - df_mom["Momentum_beta"].mean()) / df_mom["Momentum_beta"].std()
    return df_mom

# 3️⃣ Fusionar Value + Momentum y calcular Score_total
df_val = obtener_composite_value_tickers(tickers_financials)
df_mom = calcular_momentum_regresion_tickers(tickers_financials)
df_final = pd.merge(df_val, df_mom, on="Ticker", how="inner")
df_final["Score_total"] = 0.5 * df_final["Composite_z"] + 0.5 * df_final["Momentum_z"]
df_final.sort_values("Score_total", ascending=False, inplace=True)
df_final.reset_index(drop=True, inplace=True)

# Mostrar ranking
print("\n🏁 Ranking por Score_total:\n")
print(df_final[["Ticker", "Composite_z", "Momentum_z", "Score_total"]].to_string(index=False))

# 4️⃣ Gráfico de ranking
plt.figure(figsize=(10,6))
plt.barh(df_final["Ticker"], df_final["Score_total"], color="dodgerblue")
plt.axvline(x=1, color="red", linestyle="--", label="Umbral Score=1")
plt.xlabel("Score Total (Value + Momentum)")
plt.title("Ranking de acciones por Score_total")
plt.gca().invert_yaxis()
plt.grid(axis="x", linestyle="--", alpha=0.4)
plt.show()

# 5️⃣ Backtest con curva de capital promedio
def backtest(tickers):
    results = []
    equity_curves = []
    for t in tickers:
        try:
            data = yf.download(t, start=START_DATE, end=END_DATE, progress=False)
            if data.empty:
                continue
            data["returns"] = data["Close"].pct_change()
            score = df_final.loc[df_final["Ticker"] == t, "Score_total"].values[0]
            data["position"] = 1 if score > SCORE_THRESHOLD else 0
            data["strategy"] = data["position"] * data["returns"]
            cumulative = (1 + data["strategy"].fillna(0)).cumprod()
            equity_curves.append(cumulative)
            cagr = ((cumulative.iloc[-1]) ** (252 / len(data)) - 1)
            sharpe = np.sqrt(252) * data["strategy"].mean() / data["strategy"].std()
            drawdown = (cumulative / cumulative.cummax() - 1).min()
            results.append({"Ticker": t, "CAGR": cagr, "Sharpe": sharpe, "Max_Drawdown": drawdown})
        except Exception as e:
            print(f"Error en {t}: {e}")
    df_results = pd.DataFrame(results)
    # Curva de capital promedio
    if equity_curves:
        equity_avg = pd.concat(equity_curves, axis=1).mean(axis=1)
        plt.figure(figsize=(10,5))
        plt.plot(equity_avg.index, equity_avg.values, label="Estrategia Promedio", color="green")
        plt.title("Curva de Capital Promedio - Estrategia Value + Momentum")
        plt.xlabel("Fecha")
        plt.ylabel("Capital acumulado")
        plt.grid(True)
        plt.legend()
        plt.show()
    return df_results

df_backtest = backtest(df_final["Ticker"].tolist())
print("\n📈 Resultados del Backtest:\n")
print(df_backtest.round(3).to_string(index=False))