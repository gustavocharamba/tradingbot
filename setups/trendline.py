import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

# Define the functions as provided

def __trendline__(history):
    def check_trend_line(support: bool, pivot: int, slope: float, y: np.array):
        intercept = -slope * pivot + y.iloc[pivot]
        line_vals = slope * np.arange(len(y)) + intercept
        diffs = line_vals - y
        if support and diffs.max() > 1e-5:
            return -1.0
        elif not support and diffs.min() < -1e-5:
            return -1.0
        err = (diffs ** 2.0).sum()
        return err

    def optimize_slope(support: bool, pivot: int, init_slope: float, y: np.array):
        slope_unit = (y.max() - y.min()) / len(y)
        opt_step = 1.0
        min_step = 0.0001
        curr_step = opt_step
        best_slope = init_slope
        best_err = check_trend_line(support, pivot, init_slope, y)
        assert (best_err >= 0.0)
        get_derivative = True
        derivative = None
        while curr_step > min_step:
            if get_derivative:
                slope_change = best_slope + slope_unit * min_step
                test_err = check_trend_line(support, pivot, slope_change, y)
                derivative = test_err - best_err
                if test_err < 0.0:
                    slope_change = best_slope - slope_unit * min_step
                    test_err = check_trend_line(support, pivot, slope_change, y)
                    derivative = best_err - test_err
                if test_err < 0.0:
                    raise Exception("Derivative failed. Check your history.")
                get_derivative = False
            if derivative > 0.0:
                test_slope = best_slope - slope_unit * curr_step
            else:
                test_slope = best_slope + slope_unit * curr_step
            test_err = check_trend_line(support, pivot, test_slope, y)
            if test_err < 0 or test_err >= best_err:
                curr_step *= 0.5
            else:
                best_err = test_err
                best_slope = test_slope
                get_derivative = True
        return best_slope, -best_slope * pivot + y.iloc[pivot]

    def fit_trendlines_single(data: np.array):
        x = np.arange(len(data))
        coefs = np.polyfit(x, data, 1)
        line_points = coefs[0] * x + coefs[1]
        upper_pivot = (data - line_points).argmax()
        lower_pivot = (data - line_points).argmin()
        support_coefs = optimize_slope(True, lower_pivot, coefs[0], data)
        resist_coefs = optimize_slope(False, upper_pivot, coefs[0], data)
        return support_coefs, resist_coefs

    def fit_trendlines_high_low(high: np.array, low: np.array, close: np.array):
        x = np.arange(len(close))
        coefs = np.polyfit(x, close, 1)
        line_points = coefs[0] * x + coefs[1]
        upper_pivot = (high - line_points).argmax()
        lower_pivot = (low - line_points).argmin()
        support_coefs = optimize_slope(True, lower_pivot, coefs[0], low)
        resist_coefs = optimize_slope(False, upper_pivot, coefs[0], high)
        return support_coefs, resist_coefs

    def get_line_points(candles, line_points):
        idx = candles.index
        line_i = len(candles) - len(line_points)
        assert(line_i >= 0)
        points = []
        for i in range(line_i, len(candles)):
            points.append((idx[i], line_points[i - line_i]))
        return points

    # Take natural log of history to resolve price scaling issues
    history = np.log(history)
    lookback = 30

    support_slope = [np.nan] * len(history)
    resist_slope = [np.nan] * len(history)
    for i in range(lookback - 1, len(history)):
        candles = history.iloc[i - lookback + 1: i + 1]
        support_coefs, resist_coefs = fit_trendlines_high_low(candles['high'], candles['low'], candles['close'])
        support_slope[i] = support_coefs[0]
        resist_slope[i] = resist_coefs[0]

    history['support_slope'] = support_slope
    history['resist_slope'] = resist_slope

    plt.style.use('dark_background')
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    history['close'].plot(ax=ax1)
    history['support_slope'].plot(ax=ax2, label='Support Slope', color='green')
    history['resist_slope'].plot(ax=ax2, label='Resistance Slope', color='red')
    plt.title("Trend Line Slopes BTC-USDT Daily")
    plt.legend()
    plt.show()

    candles = history.iloc[-30:] # Last 30 candles in history
    support_coefs_c, resist_coefs_c = fit_trendlines_single(candles['close'])
    support_coefs, resist_coefs = fit_trendlines_high_low(candles['high'], candles['low'], candles['close'])

    support_line_c = support_coefs_c[0] * np.arange(len(candles)) + support_coefs_c[1]
    resist_line_c = resist_coefs_c[0] * np.arange(len(candles)) + resist_coefs_c[1]

    support_line = support_coefs[0] * np.arange(len(candles)) + support_coefs[1]
    resist_line = resist_coefs[0] * np.arange(len(candles)) + resist_coefs[1]

    plt.style.use('dark_background')
    ax = plt.gca()

    s_seq = get_line_points(candles, support_line)
    r_seq = get_line_points(candles, resist_line)
    s_seq2 = get_line_points(candles, support_line_c)
    r_seq2 = get_line_points(candles, resist_line_c)

    mpf.plot(candles, alines=dict(alines=[s_seq, r_seq, s_seq2, r_seq2], colors=['w', 'w', 'b', 'b']), type='candle', style='charles', ax=ax)
    plt.show()
