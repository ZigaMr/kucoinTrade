# kucoinTrade

Python API trade simulator 

To run with poetry:

    Make sure you have poetry installed (version 1.1.1)
    Make sure you have python 3.8.0 set as global/local version (can use pyenv)
    Clone everything and run "poetry install" to create new repository from existing pyproject.toml file (make sure to enable env creation "poetry config virtualenvs.create true")
    Move to repo directory and type "poetry run start" to start the quart API
    Now you can access the data from the JSON REST interface (curl -X POST http://localhost:3000/simulate_trading -H 'Content-Type: application/json' -d '{"start": 1655722800, "end": 1655995600, "interval": "1h", "symbol": "BTC/USDT"}')

Tests:
    
    Repo contains some tests already in the tests folder which you start with running "pytest" command after activating poetry environment ("poetry shell")

To run as Docker image:

    Clone everything and make sure you have Docker installed
    sudo docker build --no-cache --network="host" -t .

