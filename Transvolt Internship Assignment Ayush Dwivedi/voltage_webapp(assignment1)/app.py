from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
app = Flask(__name__)
@app.route("/")
def index():
    df = pd.read_csv("Sample_Data.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format="%d-%m-%Y %H:%M")
    df['5_MA'] = df['Values'].rolling(window=5).mean()
    df['1000_MA'] = df['Values'].rolling(window=1000).mean()
    df['5000_MA'] = df['Values'].rolling(window=5000).mean()
    df['Voltage_Diff'] = df['Values'].diff()
    df['Slope_Change'] = df['Voltage_Diff'].diff()

    # Plotting 1000 and 5000-point Moving Averages charAt
    plt.figure(figsize=(15, 6))
    plt.plot(df['Timestamp'], df['Values'], label='Original Value', linewidth=0.8)
    plt.plot(df['Timestamp'], df['1000_MA'], label='1000-Point Moving Average', color='red')
    plt.plot(df['Timestamp'], df['5000_MA'], label='5000-Point Moving Average', color='green')
    plt.title("Voltage with 1000 and 5000-Point Moving Averages")
    plt.xlabel("Timestamp")
    plt.ylabel("Values")
    plt.xticks(rotation=90, fontsize=8)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("static/charts/long_ma.png")
    plt.close()

    # Plotting 5-point Moving Average chart
    os.makedirs("static/charts", exist_ok=True)
    plt.figure(figsize=(12, 5))
    plt.plot(df['Timestamp'], df['Values'], label='Original', linewidth=0.5)
    plt.plot(df['Timestamp'], df['5_MA'], label='5-MA', color='red')
    plt.title("Voltage with 5-point Moving Average")
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/charts/voltage_ma.png")
    plt.close()

    # Peaks and Lows
    peaks, _ = find_peaks(df['Values'])
    troughs, _ = find_peaks(-df['Values'])
    extrema_df = pd.concat([
        df.iloc[peaks][['Timestamp', 'Values']].assign(Type='Peak'),
        df.iloc[troughs][['Timestamp', 'Values']].assign(Type='Lows')
    ]).sort_values('Timestamp')

    # Voltage < 20
    low_voltage_df = df[df['Values'] < 20][['Timestamp', 'Values']]

    # Accelerated downward slope
    accel_df = df[(df['Voltage_Diff'] < 0) & (df['Slope_Change'] < 0)][['Timestamp', 'Values', 'Voltage_Diff', 'Slope_Change']]

    return render_template("index.html",
                           extrema=extrema_df.head(10).to_html(index=False),
                           lows=low_voltage_df.head(10).to_html(index=False),
                           accels=accel_df.head(10).to_html(index=False),
                           chart_url="/static/charts/voltage_ma.png",
                           long_chart_url="/static/charts/long_ma.png")

if __name__ == "__main__":
    app.run(debug=True)
