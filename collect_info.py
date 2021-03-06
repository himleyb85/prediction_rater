import requests
import bs4
import json

websites = ["predictwallstreet", "stock-forecasting"]


class Scrape_predictwallstreet(object):
    def __init__(self):
        self.response = requests.get('http://www.predictwallstreet.com/Forecasts/')
        self.html_string = self.response.text
        self.soup = bs4.BeautifulSoup(self.html_string)
        self.todays_predictions = self.get_todays()

    def get_todays(self):
        todays = []
        rows = self.soup.select("div.one-day-forecasts div table tbody tr")
        for row in rows:
            prediction = {}
            symbol = row.select('td h3')[0].get_text()
            pred = row.select('td span')[0].get_text()
            prediction["symbol"] = symbol
            prediction["prediction"] = pred
            prediction["website"] = "predictwallstreet"            
            todays.append(prediction)
        return todays


class Scrape_stockforcasting(object):
    def __init__(self, symbols):    
        self.symbols = symbols
        self.predictions = self.get_predictions()

    def get_predictions(self):
        all_preds = []
        headers = {"X-AjaxPro-Method": "PredictCompanyTrial"}
        for symbol in self.symbols:
            pred = {}
            res = requests.post("http://www.stock-forecasting.com/ajaxpro/ForeCore.PredictionHelper,ForeCore.ashx", data=json.dumps({"symbol":symbol}), headers=headers)
            html_str = res.text
            split_list = html_str.split(":")
            rule = split_list[13][:1]
            pred["symbol"] = symbol
            pred["prediction"] = "Up" if rule == '1' else 'Down'
            pred["website"] = "stock-forecasting"
            all_preds.append(pred)
        return all_preds


class Stock_history(object):
    def __init__(self, symbols):
        self.symbols = symbols
        self.history = self.yester_stock_via_api()

    def yester_stock_via_api(self):
        hist = []
        for symbol in self.symbols:
            stock = {}
            res = requests.get('http://dev.markitondemand.com/Api/v2/Quote/json?symbol=' + symbol[0])
            the_json = res.json()
            if "ChangePercent" in the_json.keys():
                stock["symbol"] = symbol[0]
                stock["change"] = the_json["ChangePercent"]
                hist.append(stock)
            else:
                hist.append(self.backup_scraper(symbol[0]))
        return hist

    def backup_scraper(self, symbol):
        stock = {}
        res = requests.get('https://www.quandl.com/c/stocks/' + symbol.lower())
        html_string = res.text
        soup = bs4.BeautifulSoup(html_string)
        change = soup.select("h1 span")[0].get_text()
        stock["symbol"] = symbol
        stock["change"] = float(change[1:-1]) if change[0] == "+" else float(change[1:-1]) * -1
        return stock
