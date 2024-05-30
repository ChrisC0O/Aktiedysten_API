import urllib.parse
import requests
import time
import json


class AktiedystenAPI:

    def __init__(self, email, password, game):

        login_data = {
            "auth_email": email,
            "auth_password": password,
            "site": "AKTIEDYSTEN_DK",
            "dryrun": "0",
            "lang": "da"
        }

        # Prepping login info
        self.login_info = login_data
        self.game = game
        self.s = requests.Session()

        # Login to Aktiedysten.dk and Validates if login was successful
        if self.s.post("https://aktiedysten.dk/a/ua/login", self.login_info).status_code != 200:
            raise ValueError(
                f"Error password or username not correct.")

        # Finds game PortfolioId
        games_id_json = json.loads(self.s.get("https://aktiedysten.dk/a/my_games").text)

        for elements in games_id_json:
            game_id = elements["Id"]
            portfolio_id = elements['PortfolioId']

            game_name = json.loads(
                self.s.get(f"https://aktiedysten.dk/z/game_info?game_id={game_id}&portfolio_id={portfolio_id}").text)

            if game_name["State"] == 'started' and game_name["Name"] == self.game:
                self.game_id = game_id
                self.portfolio_id = portfolio_id
                self.game_being_played = game_name["Name"]
                self.bankrollcurrency = game_name['BankrollCurrency']

        try:
            type(self.game_id)

        except AttributeError:
            raise ValueError(
                f"Error the game [{game}] does not exist.")

    def amount_to_sum(self, BuyWithAmount, data, minus):

        """
        Used for converting "STOCK" to "CURRENCY"
        :param BuyWithAmount: Amount in "STOCK"
        :param data: Data about the "STOCK"
        :param minus: If True the brokerage_sum will be subtracted from the final price
        :return: The price if the amount of "STOCK" input
        """

        data = json.loads(data.text)

        price = float(data["StockRateInGameCurrency"])
        user_input = float(BuyWithAmount)
        brokeragePct = float(data["BrokeragePct"])

        if str(brokeragePct) == 0:
            whole_price = user_input * price

            return whole_price

        if minus == False:
            whole_price = user_input * price
            y = whole_price / 100
            brokerage_sum = y * brokeragePct
            final_price = brokerage_sum + whole_price

            return final_price

        if minus == True:
            whole_price = user_input * price
            y = whole_price / 100
            brokerage_sum = y * brokeragePct
            final_price = whole_price - brokerage_sum

            return final_price

    def sum_to_amount(self, BuyWithAmount, data):

        """
        Used for converting "CURRENCY" to "STOCK"
        :param BuyWithAmount: Amount in "CURRENCY"
        :param data: Data about the "STOCK"
        :return: The amount of "STOCK" converted from "CURRENCY"
        """

        data = json.loads(data.text)

        currency = float(data["StockRateInGameCurrency"])
        user_input = float(BuyWithAmount)

        new_amount = user_input / currency

        return new_amount

    def buy(self, exchange, ticker, buy_with_amount, method):

        """
        Buys a stock of your choosing.

        :param exchange: Exchange
        :param ticker: Ticker Symbol
        :param buy_with_amount: Amount to Buy
        :param method: Used to show if BuyWithAmount is "CURRENCY" or "STOCK"
        :return:
        """

        exchange = exchange.upper()
        ticker = ticker.upper()
        buy_with_amount = str(buy_with_amount)
        method = method.upper()

        if method != "CURRENCY" and method != "STOCK":
            raise ValueError(
                f"Error CURRENCY or STOCK not spelled right")

        stock_data = self.s.get(
            f"https://aktiedysten.dk/a/trade_portfolio_options?portfolio_id={self.portfolio_id}&exchange={exchange}&ticker={ticker}")

        if not stock_data.status_code == 200:
            raise ValueError(
                f"Error Ticker['{ticker}'] or Exchange['{exchange}'] does not exist.")

        if method == "CURRENCY":
            buy_with_amount_currency = buy_with_amount
            buy_with_amount_amount = str(self.sum_to_amount(buy_with_amount, stock_data))
            buy_with_amount = buy_with_amount_currency

        if method == "STOCK":
            buy_with_amount_currency = str(self.amount_to_sum(buy_with_amount, stock_data, False))
            buy_with_amount_amount = buy_with_amount
            buy_with_amount = buy_with_amount_currency

        if buy_with_amount == "0.0":
            return None

        rq = '{"PortfolioId":!"#,"Exchange":"€%&","Ticker":"/()","BuyWithAmount":=?!,"DoEnqueue":false}'
        rq = rq.replace('!"#', str(self.portfolio_id))
        rq = rq.replace("€%&", exchange)
        rq = rq.replace("/()", ticker)
        rq = rq.replace("=?!", buy_with_amount)

        buy_data = {
            "rq": rq}

        buy_order = self.s.post("https://aktiedysten.dk/a/trade", buy_data)

        if buy_order.status_code == 200:
            return_file = {
                "Confirmed": True,
                "Game": self.game_being_played,
                "Stock": ticker,
                "Exchange": exchange,
                "OrderInStock": buy_with_amount_amount,
                "OrderInCurrency": buy_with_amount_currency,
                "OrderType": "Buy"
            }

            return return_file

        if not buy_order.status_code == 200:
            return_file = {
                "Confirmed": False,
                "Game": self.game_being_played,
                "Stock": ticker,
                "Exchange": exchange,
                "OrderInStock": buy_with_amount_amount,
                "OrderInCurrency": buy_with_amount_currency,
                "OrderType": "Buy"
            }

            return return_file

    def sell(self, exchange, ticker, buy_with_amount, method):

        """
        Sells a stock of your choosing.
        :param exchange: Exchange
        :param ticker: Ticker Symbol
        :param buy_with_amount: Amount to Buy
        :param method: Used to show if BuyWithAmount is "CURRENCY" or "STOCK"
        :return:
        """

        exchange = exchange.upper()
        ticker = ticker.upper()
        buy_with_amount = str(buy_with_amount)
        method = method.upper()

        if method != "CURRENCY" and method != "STOCK":
            raise ValueError(
                f"Error CURRENCY or STOCK not spelled right")

        stock_data = self.s.get(
            f"https://aktiedysten.dk/a/trade_portfolio_options?portfolio_id={self.portfolio_id}&exchange={exchange}&ticker={ticker}")

        if not stock_data.status_code == 200:
            raise ValueError(
                f"Error Ticker['{ticker}'] or Exchange['{exchange}'] does not exist.")

        if method == "CURRENCY":
            buy_with_amount_currency = buy_with_amount
            buy_with_amount_amount = str(self.sum_to_amount(buy_with_amount, stock_data))
            buy_with_amount = buy_with_amount_amount

        if method == "STOCK":
            buy_with_amount_currency = str(self.amount_to_sum(buy_with_amount, stock_data, True))
            buy_with_amount_amount = buy_with_amount
            buy_with_amount = buy_with_amount_amount

        rq = '{"PortfolioId":!"#,"Exchange":"€%&","Ticker":"/()","SellQuantity":=?!,"DoEnqueue":false}'
        rq = rq.replace('!"#', str(self.portfolio_id))
        rq = rq.replace("€%&", exchange)
        rq = rq.replace("/()", ticker)
        rq = rq.replace("=?!", str(buy_with_amount))

        buy_data = {
            "rq": rq}

        sell_order = self.s.post("https://aktiedysten.dk/a/trade", buy_data)

        if sell_order.status_code == 200:
            return_file = {
                "Confirmed": True,
                "Game": self.game_being_played,
                "Stock": ticker,
                "Exchange": exchange,
                "OrderInStock": buy_with_amount_amount,
                "OrderInCurrency": buy_with_amount_currency,
                "OrderType": "Sale"
            }

            return return_file

        if not sell_order.status_code == 200:
            return_file = {
                "Confirmed": False,
                "Game": self.game_being_played,
                "Stock": ticker,
                "Exchange": exchange,
                "OrderInStock": buy_with_amount_amount,
                "OrderInCurrency": buy_with_amount_currency,
                "OrderType": "Sale"
            }

            return return_file

    def liquidate_game(self):

        """
        Liquidates your portfolio
        :return: Returns order information
        """

        account = self.s.get(
            f"https://aktiedysten.dk/a/my_portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text

        account = json.loads(account)
        assets = account["Assets"]

        order_data = []

        for i in assets:
            exchange = i["Exchange"]
            ticker = i["Ticker"]
            quantity = float((i["Quantity"]))

            if self.bankrollcurrency == ticker:
                continue

            data = self.sell(exchange, ticker, quantity, "STOCK")
            order_data.append(data)

        return order_data

    def sell_all(self, ticker):

        """
        Sells all stock of a given ticker
        :return: Returns order information
        """

        account = self.s.get(
            f"https://aktiedysten.dk/a/my_portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text

        account = json.loads(account)
        assets = account["Assets"]
        user_input_ticker = ticker.upper()

        for i in assets:
            exchange = i["Exchange"]
            ticker = i["Ticker"]
            quantity = float((i["Quantity"]))

            if user_input_ticker == ticker:
                order_data = self.sell(exchange, ticker, quantity, "STOCK")

        try:
            return order_data
        except UnboundLocalError:

            raise ValueError(
                f"The Stock [{user_input_ticker.upper()}] does not exist in portfolio")

    def get_game_json(self):

        data = self.s.get(f"https://aktiedysten.dk/a/my_portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        data = json.loads(data)

        return data

    def get_currency_in_bank(self):

        total_in_account = self.s.get(
            f"https://aktiedysten.dk/z/portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        total_in_account = json.loads(total_in_account)

        return total_in_account["Total"]

    def get_initial_amount(self):

        InitialAmount = self.s.get(
            f"https://aktiedysten.dk/z/portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        InitialAmount = json.loads(InitialAmount)

        return InitialAmount["Portfolio"]["Game"]["InitialAmount"]

    def get_user_history(self):

        history = self.s.get(f"https://aktiedysten.dk/z/portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        history = json.loads(history)
        return history

    def create_new_game(self,
                        name: str,
                        amount: int,
                        currency: str,
                        days_to_end: int,
                        brokerage_pct: float,
                        max_amount_per_stock=None,
                        volume_multiplier=None,
                        markets_to_exclude=None):

        """
        Creates a new game.
        :param name: Name of the game you want to create.
        :param currency: Game currency.
        :param days_to_end: In how many days should the game end.
        :param brokerage_pct: Games brokerage percentage.
        :param amount: Amount of money.
        :param max_amount_per_stock: Max amount you can buy stock from.
        :param volume_multiplier: Trade with real world volume.
        :param markets_to_exclude: By default games will be created with all markets. Set this to exclude markets.
        You can choose from: ["DK_STOCK", "US_STOCK", "DE_STOCK", "SE_STOCK", "FI_STOCK", "IS_STOCK", "COMMODITIES",
                            "FOREX", "CRYPTOCURRENCIES"]
        :return: Returns True if the game was created successfully, else return False.
        """

        def make_unix_end_day(days):
            return time.time() + (days * 86400)

        def url_encode(text):
            return urllib.parse.quote(text, encoding="utf-8")

        markets = ["DK_STOCK", "US_STOCK", "DE_STOCK", "SE_STOCK", "FI_STOCK", "IS_STOCK", "COMMODITIES", "FOREX",
                   "CRYPTOCURRENCIES"]

        name = url_encode(name)
        end_time = make_unix_end_day(days_to_end)
        currency = currency.upper()

        if max_amount_per_stock is None:
            max_amount_per_stock = 0

        if volume_multiplier is True:
            volume_multiplier = "&volume_multiplier=1"
        else:
            volume_multiplier = ""

        if markets_to_exclude is not None:
            for i in markets_to_exclude:
                markets.remove(i)

        marked_payload = ""
        for i in markets:
            marked_payload += f'%22{i}%22%2C'

        marked_payload = marked_payload[0:-3]
        marked_payload = f'%5B{marked_payload}%5D'

        payload = f"name={name}&amount_currency={currency}&end_ts={round(end_time, 3)}" \
                  f"&brokerage_pct={brokerage_pct}&amount={amount}&markets={marked_payload}" \
                  f"&pay_dividends=0&max_amount_per_stock={max_amount_per_stock}{volume_multiplier}"

        if self.s.post(f"https://aktiedysten.dk/a/new_game?{payload}").status_code == 200:
            return True
        else:
            return False
