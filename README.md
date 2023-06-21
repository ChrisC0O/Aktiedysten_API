# Aktiedysten_API
This code is used to access the website: www.aktiedysten.dk.
You can buy, sell and more using simple commands.


## How to use:

  - Start by going to the Aktiedysten.dk and make an account.
  - Download the API.py.
  - Make a new .py file and import the Aktiedysten_API.
  - Insert your login info.

## Code exsample:
```py
from API import Aktiedysten_API

account = Aktiedysten_API("Username", "Password", "Game")
```
## All functions
```py
account.Buy()
account.Sell()
account.Liquidate_Game()
account.Sell_All()
```
## Buying 10 BTC using the code:
```py
account = Aktiedysten_API("Username", "Password", "Game")
account.Buy("CRYPTO", "BTC", 10, "STOCK")
```
returns:
```py
{'Confirmed': True, 'Game': 'GAME', 'Stock': 'BTC', 'Exchange': 'CRYPTO', 'OrderInStock': '10', 'OrderInCurrency': '2013118.9090987504', 'OrderType': 'Buy'}
```
## Simble tradebot exsample:

```py
from time import sleep

account = Aktiedysten_API("Username", "Password", "Game")

while True:
  account.Buy("CRYPTO", "BTC", 10, "STOCK")
  sleep(1)
```
# Script buys 1 BTC every second
