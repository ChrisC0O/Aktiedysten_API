import requests
import json

class Aktiedysten_API:

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


    def Amount_To_Sum(self, BuyWithAmount, data, minus):

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

    def Sum_To_Amount(self, BuyWithAmount, data):

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


    def Buy(self, exchange, ticker, buy_with_amount, method):

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

        if method == "CURRENCY" or method == "STOCK":
            pass

        else:
            print("Error CURRENCY or STOCK not spelled right")
            quit()

        stock_data = self.s.get(
            f"https://aktiedysten.dk/a/trade_portfolio_options?portfolio_id={self.portfolio_id}&exchange={exchange}&ticker={ticker}")

        if not stock_data.status_code == 200:
            raise ValueError(
                f"Error Ticker['{ticker}'] or Exchange['{exchange}'] does not exist.")

        if method == "CURRENCY":
            buy_with_amount_currency = buy_with_amount
            buy_with_amount_amount = str(self.Sum_To_Amount(buy_with_amount, stock_data))
            buy_with_amount = buy_with_amount_currency

        if method == "STOCK":
            buy_with_amount_currency = str(self.Amount_To_Sum(buy_with_amount, stock_data, False))
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


    def Sell(self, exchange, ticker, buy_with_amount, method):

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

        if method == "CURRENCY" or method == "STOCK":
            None

        else:
            print("Error CURRENCY or STOCK not spelled right")
            quit()

        stock_data = self.s.get(
            f"https://aktiedysten.dk/a/trade_portfolio_options?portfolio_id={self.portfolio_id}&exchange={exchange}&ticker={ticker}")

        if not stock_data.status_code == 200:
            raise ValueError(
                f"Error Ticker['{ticker}'] or Exchange['{exchange}'] does not exist.")

        if method == "CURRENCY":
            buy_with_amount_currency = buy_with_amount
            buy_with_amount_amount = str(self.Sum_To_Amount(buy_with_amount, stock_data))
            buy_with_amount = buy_with_amount_amount

        if method == "STOCK":
            buy_with_amount_currency = str(self.Amount_To_Sum(buy_with_amount, stock_data, True))
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


    def Liquidate_Game(self):

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

            data = self.Sell(exchange, ticker, quantity, "STOCK")
            order_data.append(data)

        return order_data

    def Sell_All(self, ticker):

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
                order_data = self.Sell(exchange, ticker, quantity, "STOCK")

        try:
            return order_data
        except UnboundLocalError:

            raise ValueError(
                f"The Stock [{user_input_ticker.upper()}] does not exist in portfolio")


    def GetGameJson(self):

        data = self.s.get(f"https://aktiedysten.dk/a/my_portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        data = json.loads(data)

        return data

    def GetCurrencyInBank(self):

        total_in_account = self.s.get(f"https://aktiedysten.dk/z/portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        total_in_account = json.loads(total_in_account)

        return total_in_account["Total"]

    def GetInitialAmount(self):

        InitialAmount = self.s.get(f"https://aktiedysten.dk/z/portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        InitialAmount = json.loads(InitialAmount)

        return InitialAmount["Portfolio"]["Game"]["InitialAmount"]

    def GetUserHistory(self):

        history = self.s.get(f"https://aktiedysten.dk/z/portfolio_assets?portfolio_id={self.portfolio_id}&lang=da").text
        history = json.loads(history)
        return history
