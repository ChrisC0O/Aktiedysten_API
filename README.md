# Aktiedysten_API
This code is used to access the website: www.aktiedysten.dk.
You can buy, sell and more using simple commands.

## News:
> Code has been made more pythonic.
> This might cause scripts to crash, therefore check if your script needs refactoring.

> Added a create_new_game() feature!



## How to use:

  - Start by going to the Aktiedysten.dk
  - Make an account.
  - Download the API.py.
  - Import the script.
  - Insert your login info.

## Code exsample:
```py
from API import AktiedystenAPI

account = AktiedystenAPI("Username", "Password", "Game")
```
## All functions
```py
account.buy()
account.sell()
account.liquidate_game()
account.sell_all()
account.create_new_game()
account.get_game_json()
account.get_currency_in_bank()
account.get_initial_amount()
account.get_user_history()
```
## Buying 10 BTC using the code:
```py
account = AktiedystenAPI("Username", "Password", "Game")
account.buy("CRYPTO", "BTC", 10, "STOCK")
```
Returns Json:
```py
{'Confirmed': True, 'Game': 'GAME', 'Stock': 'BTC', 'Exchange': 'CRYPTO', 'OrderInStock': '10', 'OrderInCurrency': '2013118.9090987504', 'OrderType': 'Buy'}
```
## Simble tradebot exsample:

```py
from time import sleep

account = AktiedystenAPI("Username", "Password", "Game")

while True:
  account.buy("CRYPTO", "BTC", 1, "STOCK")
  sleep(1)
```
Script buys 1 BTC every second
