from kucointrade import app
import pytest


async def test_candles_example() -> None:
    test_client = app.test_client()
    response = await test_client.post("/candles", json={"start": 1655722800, "end": 1655895600, "interval": "1h", "symbol": "BTC/USDT"})
    data = await response.get_json()
    assert data[-1] == {"close":20421,"close_time":1655895600,"high":20554,"low":20360,"open":20428,"start":1655892000,"symbol":"BTC/USDT"}

async def test_candles_empty_data() -> None:
    test_client = app.test_client()
    response = await test_client.post("/candles", json={"start": 1655722800, "end": 1655722800, "interval": "1h", "symbol": "BTC/USDT"})
    data = await response.get_json()
    assert data == [{}]

async def test_candles_ValueError() -> None:
    test_client = app.test_client()
    with pytest.raises(ValueError):
        response = await test_client.post("/candles", json={"start": 1655722800, "interval": "1h", "symbol": "BTC/USDT"})
    
async def test_trading_value() -> None:
    test_client = app.test_client()
    response = await test_client.post("/simulate_trading", json={"start": 1655722800, "end": 1655895600, "interval": "1h", "symbol": "BTC/USDT"})
    data = await response.get_json()
    assert data == {"percentage return":3.692}