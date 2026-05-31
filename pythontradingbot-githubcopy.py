import accountid
import pandas
import time
from datetime import datetime, timedelta, timezone

# Status confirmation making sure connection to the Alpaca API is established
status_code= accountid.response.status_code

if status_code== 200:
    print('Connected to Alpaca API successfully')
    account_info= accountid.response.json()
else:
    print('Connection failed')


 # Fetches price data of the candle depending on whether the timeframe parameter is 1,5,10,15,or 30 mins. It then assigns the empty parameter dataframe with the live data from Alpaca API.

def get_recent_price_data(symbol="AAPL", timeframe="15Min", candle_count=100):
        end_time = datetime.now(timezone.utc)

        if timeframe == "15Min":
            minutes_per_candle = 15
        elif timeframe == "1Min":
            minutes_per_candle = 1
        elif timeframe == "5Min":
            minutes_per_candle = 5
        elif timeframe == "30Min":
            minutes_per_candle = 30
        else:
            minutes_per_candle = 15

        start_time = end_time - timedelta(minutes=minutes_per_candle * candle_count)

        params = {
            "symbols": symbol,
            "timeframe": timeframe,
            "start": start_time.isoformat().replace("+00:00", "Z"),
            "end": end_time.isoformat().replace("+00:00", "Z"),
            "limit": candle_count,
            "feed": "iex",
        }

        response = accountid.requests.get(
            "https://data.alpaca.markets/v2/stocks/bars",
            headers=accountid.HEADERS,
            params=params
        )

        print(response.status_code)

        data = response.json()
        bars = data.get("bars", {}).get(symbol, [])

        if not bars:
            raise ValueError(f"No bars found for {symbol}.")

        price_df = pandas.DataFrame(bars)

        return price_df

df = get_recent_price_data(
    symbol="SPY",
    timeframe="15Min",
    candle_count=100
)

display(df.tail())

# Styling and formatting the columns of the pandas table as well as renaming the columns
def format_price_table(df):
    formatted_df = df.copy()

    formatted_df = formatted_df.rename(columns={
        "t": "Time",
        "o": "Open",
        "h": "High",
        "l": "Low",
        "c": "Close",
        "v": "Volume",
        "n": "Trade Count",
        "vw": "VWAP"
    })

    formatted_df["Time"] = pandas.to_datetime(
        formatted_df["Time"],
        utc=True
    )
    formatted_df["Time"] = formatted_df["Time"].dt.tz_convert(
        "America/New_York"
    )

    formatted_df = formatted_df[
        [
            "Time",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Trade Count",
            "VWAP"
        ]
    ]

    return formatted_df

formatted_df = format_price_table(df)
display(formatted_df.head())

# Function to calculate indicators

def calculate_indicators(df):
    indicators_df = df.copy()

    # Make sure close prices are numeric
    indicators_df["c"] = pandas.to_numeric(indicators_df["c"], errors="coerce")
    indicators_df["v"] = pandas.to_numeric(indicators_df["v"], errors="coerce")

    # Simple Moving Averages
    indicators_df["SMA_20"] = indicators_df["c"].rolling(window=20).mean()
    indicators_df["SMA_50"] = indicators_df["c"].rolling(window=50).mean()

    # Exponential Moving Averages
    indicators_df["EMA_12"] = indicators_df["c"].ewm(span=12, adjust=False).mean()
    indicators_df["EMA_26"] = indicators_df["c"].ewm(span=26, adjust=False).mean()

    # MACD
    indicators_df["MACD"] = indicators_df["EMA_12"] - indicators_df["EMA_26"]
    indicators_df["MACD_Signal"] = indicators_df["MACD"].ewm(span=9, adjust=False).mean()
    indicators_df["MACD_Histogram"] = indicators_df["MACD"] - indicators_df["MACD_Signal"]

    # RSI
    delta = indicators_df["c"].diff()

    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gain = gains.rolling(window=14).mean()
    avg_loss = losses.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    indicators_df["RSI_14"] = 100 - (100 / (1 + rs))

    # Volume moving average
    indicators_df["Volume_SMA_20"] = indicators_df["v"].rolling(window=20).mean()

    #Average True Range
    high_low = indicators_df["h"] - indicators_df["l"]
    high_previous_close = (indicators_df["h"] - indicators_df["c"].shift(1)).abs()
    low_previous_close = (indicators_df["l"] - indicators_df["c"].shift(1)).abs()

    true_range = pandas.concat(
        [high_low, high_previous_close, low_previous_close],
        axis=1
    ).max(axis=1)

    indicators_df["ATR_14"] = true_range.rolling(window=14).mean()
    return indicators_df

def fix_indicator_data(indicator_df):
    fixed_df = indicator_df.copy()

    numeric_columns = [
        "o",
        "h",
        "l",
        "c",
        "v",
        "n",
        "vw",
        "SMA_20",
        "SMA_50",
        "EMA_12",
        "EMA_26",
        "MACD",
        "MACD_Signal",
        "MACD_Histogram",
        "RSI_14",
        "Volume_SMA_20",
        "ATR_14"
    ]

    for column in numeric_columns:
        if column in fixed_df.columns:
            fixed_df[column] = pandas.to_numeric(fixed_df[column], errors="coerce")

    columns_to_fill_with_mean = [
        "RSI_14",
        "ATR_14",
        "SMA_20",
        "SMA_50",
        "Volume_SMA_20"
    ]

    for column in columns_to_fill_with_mean:
        if column in fixed_df.columns:
            if fixed_df[column].isna().all():
                fixed_df[column] = fixed_df[column].fillna(0.0)
            else:
                fixed_df[column] = fixed_df[column].fillna(fixed_df[column].mean())

    outlier_columns = [
        "v",
        "n"
    ]

    for column in outlier_columns:
        if column in fixed_df.columns:
            q1 = fixed_df[column].quantile(0.25)
            q3 = fixed_df[column].quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            fixed_df[column] = fixed_df[column].clip(
                lower=lower_bound,
                upper=upper_bound
            )

    return fixed_df

indicator_df = calculate_indicators(df)
indicator_df = fix_indicator_data(indicator_df)
df_fixed = indicator_df

df_fixed.tail()

#Formatting of the indicator table. Includes: time,open,high,low,close,volume,trade count,vwap,sma 20,sma 50,ema 12,ema 26,macd,macd signal,macd histogram,rsi 14,volume sma 20,atr 14

def format_indicator_table(indicator_df):
    pretty_indicator_df = indicator_df.rename(columns={
        "t": "Time",
        "o": "Open",
        "h": "High",
        "l": "Low",
        "c": "Close",
        "v": "Volume",
        "n": "Trade Count",
        "vw": "VWAP",
        "SMA_20": "SMA 20",
        "SMA_50": "SMA 50",
        "EMA_12": "EMA 12",
        "EMA_26": "EMA 26",
        "MACD_Signal": "MACD Signal",
        "MACD_Histogram": "MACD Histogram",
        "RSI_14": "RSI 14",
        "Volume_SMA_20": "Volume SMA 20",
        "ATR_14": "ATR 14"
    })

    pretty_indicator_df["Time"] = pandas.to_datetime(
        pretty_indicator_df["Time"],
        utc=True
    )
    pretty_indicator_df["Time"] = pretty_indicator_df["Time"].dt.tz_convert(
        "America/New_York"
    )
    pretty_indicator_df["Time"] = pretty_indicator_df["Time"].dt.strftime(
        "%Y-%m-%d %I:%M %p"
    )

    pretty_indicator_df = pretty_indicator_df[
        [
            "Time",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Trade Count",
            "VWAP",
            "SMA 20",
            "SMA 50",
            "EMA 12",
            "EMA 26",
            "MACD",
            "MACD Signal",
            "MACD Histogram",
            "RSI 14",
            "Volume SMA 20",
            "ATR 14"
        ]
    ]

    return pretty_indicator_df

pretty_indicator_df = format_indicator_table(indicator_df)
display(pretty_indicator_df)

#%%
# Trading logic: This compares whether the higher or lower EMA crosses which will signal a bullish or bearish market, hence telling us when to sell or buy

def ema_crossover(df):
    if len(df) < 2:
        return "HOLD"

    latest_two_rows = df.dropna(subset=["EMA_12", "EMA_26"]).tail(2)

    if len(latest_two_rows) < 2:
        return "HOLD"

    previous_candle = latest_two_rows.iloc[0]
    current_candle = latest_two_rows.iloc[1]

    previous_ema_12 = previous_candle["EMA_12"]
    previous_ema_26 = previous_candle["EMA_26"]

    current_ema_12 = current_candle["EMA_12"]
    current_ema_26 = current_candle["EMA_26"]

    bullish_crossover = previous_ema_12 <= previous_ema_26 and current_ema_12 > current_ema_26
    bearish_crossover = previous_ema_12 >= previous_ema_26 and current_ema_12 < current_ema_26

    if bullish_crossover:
        return "BUY:EMA 12 crosses ABOVE EMA 26"

    if bearish_crossover:
        return "SELL:EMA 12 crosses BELOW EMA 26"

    return "HOLD"

#GLOBAL VARIABLE
trade_signal = ema_crossover(indicator_df)

print(f"EMA crossover signal: {trade_signal}")


# Creates the orders

def create_market_order(symbol, qty, side):
    order_data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "day"
    }

    order_response = accountid.requests.post(
        "https://paper-api.alpaca.markets/v2/orders",
        headers=accountid.HEADERS,
        json=order_data
    )

    print(order_response.status_code)

    try:
        print(order_response.json())
    except Exception:
        print(order_response.text)

    return order_response

# Stop-Loss Mechanism

def calculate_trade_levels(indicator_df, tp_ratio=2):
    latest_candle = indicator_df.dropna(subset=["ATR_14"]).iloc[-1]

    entry_price = latest_candle["c"]

    stop_loss = entry_price - latest_candle["ATR_14"]

    stop_distance = entry_price - stop_loss

    take_profit = entry_price + (stop_distance * tp_ratio)

    trade_levels = {
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "stop_distance": stop_distance,
        "take_profit": take_profit,
        "tp_ratio": tp_ratio
    }

    return trade_levels

# Automation of the bot. The function is fed the trading signals which then will trigger the feeding of the trade levels (stop-loss). This will then execute the buy and sell orders. The automation process will check for current time vs last time to keep the process running.

def run_bot(
    symbol="AAPL",
    timeframe="15Min",
    candle_count=100,
    qty=1,
    place_order=False,
    tp_ratio=2,
    automate=False,
    max_runs=None,
    sleep_seconds=60,
    display_rows=20
):
    global df
    global formatted_df
    global indicator_df
    global pretty_indicator_df
    global trade_signal
    global order_response
    global trade_levels

    def execute_bot_once(run_number=None):
        global df
        global formatted_df
        global indicator_df
        global pretty_indicator_df
        global trade_signal
        global order_response
        global trade_levels

        if run_number is not None:
            print(f"Starting trading bot run #{run_number}...")
        else:
            print("Starting trading bot...")

        df = get_recent_price_data(
            symbol=symbol,
            timeframe=timeframe,
            candle_count=candle_count
        )

        if df is None or df.empty:
            raise ValueError(f"No price data found for {symbol}.")

        formatted_df = format_price_table(df)

        indicator_df = calculate_indicators(df)

        trade_signal = ema_crossover(indicator_df)

        pretty_indicator_df = format_indicator_table(indicator_df)

        order_response = None
        trade_levels = None

        print(f"Symbol: {symbol}")
        print(f"Timeframe: {timeframe}")
        print(f"Latest close: {df.iloc[-1]['c']}")
        print(f"EMA crossover signal: {trade_signal}")

        if trade_signal.startswith("BUY"):
            print("Buy signal detected")

            trade_levels = calculate_trade_levels(
                indicator_df,
                tp_ratio=tp_ratio
            )

            print(f"Entry price: {trade_levels['entry_price']:.2f}")
            print(f"Stop loss: {trade_levels['stop_loss']:.2f}")
            print(f"Stop distance: {trade_levels['stop_distance']:.2f}")
            print(f"Take profit: {trade_levels['take_profit']:.2f}")

            if place_order:
                order_response = create_market_order(symbol, qty, "buy")
            else:
                print("Order not placed because place_order=False")

        elif trade_signal.startswith("SELL"):
            print("Sell signal detected")

            if place_order:
                order_response = create_market_order(symbol, qty, "sell")
            else:
                print("Order not placed because place_order=False")

        else:
            print("No trade placed")

        display(pretty_indicator_df.tail(display_rows))

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "price_df": df,
            "formatted_df": formatted_df,
            "indicator_df": indicator_df,
            "pretty_indicator_df": pretty_indicator_df,
            "trade_signal": trade_signal,
            "trade_levels": trade_levels,
            "order_response": order_response
        }

    if not automate:
        return execute_bot_once()

    print("Bot automation started...")

    run_count = 0

    while True:
        run_count += 1

        try:
            bot_result = execute_bot_once(run_number=run_count)
        except Exception as error:
            print(f"Bot run failed: {error}")
            bot_result = None

        if max_runs is not None and run_count >= max_runs:
            print("Bot automation stopped.")
            return bot_result

        print(f"Waiting {sleep_seconds} seconds until next run...")
        time.sleep(sleep_seconds)

bot_result = run_bot(
            symbol="SPY",
            timeframe="15Min",
            candle_count=100,
            qty=1,
            place_order=True,
            tp_ratio=2,
            automate=True,
            max_runs=5,
            sleep_seconds=5
        )