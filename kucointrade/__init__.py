from quart import Quart
from quart import request
import pandas as pd
import ccxt.async_support as ccxt
from quart import jsonify


app = Quart(__name__)

# API doesn't return endDate so we have to infer endDate through timestamp
end_date_delta = {
            '1m': 60,
            '3m': 3*60,
            '5m': 5*60,
            '15m': 15*60,
            '30m': 30*60,
            '1h': 60**2,
            '2h': 2*60**2,
            '4h': 4*60**2,
            '6h': 4*60**2,
            '8h': 8*60**2,
            '12h': 12*60**2,
            '1d': 24*60**2,
            '1w': 7*24*60**2,
        }


@app.post("/candles")
async def candles():
    """
        Get data from Kucoin API
        Expected json keys: 
            -start
            -end
            -interval
            -symbol
    """

    exchange = ccxt.kucoin()
    assert exchange.has['fetchOHLCV'] # Check if we can fetch data for kucoin exchange

    keys = ['start', 'end', 'interval', 'symbol']
    request_data = await request.get_json() # Get JSON data
    
    if any(map(lambda x: x not in request_data.keys(), keys)):
        # Check if any missing params
        exchange.close()
        raise ValueError('Missing parameters for API call')


    # Fetch requested data (pass start/end to "params" instead to "since" and "limit" to bypass unecessary second -> milisecond convertions)
    api_data = await exchange.fetch_ohlcv(request_data['symbol'],
                                          request_data['interval'],
                                          params={
                                            'startAt': request_data['start'], 
                                            'endAt': request_data['end']
                                            }
                                        )
    if len(api_data) == 0: return jsonify([{}])
    
    delta = end_date_delta[request_data['interval']]
    api_data = [{'start': int(i[0]/1000), 
                 'close_time': int(i[0]/1000) + delta,
                 'open': int(i[1]),
                 'high': int(i[2]),
                 'low': int(i[3]),
                 'close': int(i[4]),
                 'symbol': request_data['symbol']} for i in api_data]
    
    await exchange.close()
    return jsonify(api_data) # JSON array, should change format in the future


@app.post("/simulate_trading")
async def simulate_trading():
    """
        Get data from Kucoin API and calculate % return
        Expected json keys: 
            -start
            -end
            -interval
            -symbol
    """
    
    exchange = ccxt.kucoin()
    assert exchange.has['fetchOHLCV'] # Check if we can fetch data for kucoin exchange
    
    keys = ['start', 'end', 'interval', 'symbol']
    request_data = await request.get_json() # Get JSON data
    
    if any(map(lambda x: x not in request_data.keys(), keys)):
        # Check if any missing params
        raise ValueError('Missing parameters for API call')


    # Fetch requested data (pass start/end to "params" instead to "since" and "limit" to bypass unecessary second -> milisecond convertions)
    api_data = await exchange.fetch_ohlcv(request_data['symbol'],
                                          request_data['interval'],
                                          params={
                                            'startAt': request_data['start'], 
                                            'endAt': request_data['end']
                                            }
                                        )
    # Set to pandas DataFrame so we can use vector operations (faster for larger datasets)
    df = pd.DataFrame([{'start': int(i[0]/1000), 
                 'open': i[1],
                 'high': i[2],
                 'low': i[3],
                 'close': i[4],
                 'symbol': request_data['symbol']} for i in api_data])
    
    df['buy'] = df.open <= df.close
    if df.buy.mean() == 0:
        # No buy opportunities
        exchange.close()
        return jsonify({'percentage return': 0})
    last_close = df.close.iloc[-1] # Save last_close if we still have open position at the end
    df = df.iloc[df[df.buy].index[0]:] # Delete all rows before 1st buy opportunity
    df = df[df['buy'] != df['buy'].shift()].reset_index(drop=True) # Keep 1st row of duplicates (so we only get rows where we actually buy and sell)

    # If we still have open position we close at the end with the last close price
    profit = df.close.diff()[~df.buy].sum() if df.buy.iloc[-1] == False else df.close.diff()[~df.buy].sum() + last_close - df.close.iloc[1]
    
    pct_return = round((profit / df.close.iloc[0]) * 100, 3)
    await exchange.close()
    return jsonify({'percentage return': pct_return})

def run() -> None:
    app.run(port = 3000)
