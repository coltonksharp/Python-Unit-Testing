import unittest
from datetime import datetime
import requests
import json
import pygal
import webbrowser

# Validation Functions
def validate_symbol(symbol):
    return symbol.isalpha() and symbol.isupper() and 1 <= len(symbol) <= 7

def validate_chart_type(chart_type):
    return chart_type in {'1', '2'}

def validate_time_series(time_series):
    return time_series.isdigit() and 1 <= int(time_series) <= 4

def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Main Functions
def get_symbol():
    symbol = input("Enter the stock symbol you are looking for: ")
    while not validate_symbol(symbol):
        print("Invalid symbol! Please enter a capitalized, 1-7 alpha characters.")
        symbol = input("Enter the stock symbol you are looking for: ")
    return symbol

def get_chart():
    chart_type = ''
    while not validate_chart_type(chart_type):
        print("Invalid chart type! Please enter 1 or 2.")
        chart_type = input("Enter the chart type you want (1, 2): ")
    return 'Bar' if chart_type == '1' else 'Line'

def get_time_series():
    while True:
        time_series = input("Enter the time series option (1, 2, 3, 4): ")
        if validate_time_series(time_series):
            return ['INTRADAY', '60min'] if time_series == '1' else ['DAILY', 'null'] if time_series == '2' else ['WEEKLY', 'null'] if time_series == '3' else ['MONTHLY', 'null']
        print("Invalid time series option! Please enter a number between 1 and 4.")

def get_dates():
    start_date = input("Enter the beginning date in YYYY-MM-DD format: ")
    while not validate_date(start_date):
        print("Invalid date format! Please use YYYY-MM-DD.")
        start_date = input("Enter the beginning date in YYYY-MM-DD format: ")

    end_date = input("Enter the end date in YYYY-MM-DD format: ")
    while not validate_date(end_date):
        print("Invalid date format! Please use YYYY-MM-DD.")
        end_date = input("Enter the end date in YYYY-MM-DD format: ")

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    while end_date_obj < start_date_obj:
        print("End date cannot be before the start date.")
        start_date = input("Enter the beginning date in YYYY-MM-DD format: ")
        while not validate_date(start_date):
            print("Invalid date format! Please use YYYY-MM-DD.")
            start_date = input("Enter the beginning date in YYYY-MM-DD format: ")

        end_date = input("Enter the end date in YYYY-MM-DD format: ")
        while not validate_date(end_date):
            print("Invalid date format! Please use YYYY-MM-DD.")
            end_date = input("Enter the end date in YYYY-MM-DD format: ")

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    return [start_date_obj, end_date_obj]

# Testing Functions
class TestProject3Inputs(unittest.TestCase):
    def test_validate_symbol(self):
        self.assertTrue(validate_symbol('AAPL'))
        self.assertFalse(validate_symbol('ABC123'))
        self.assertFalse(validate_symbol('abc123'))

    def test_validate_chart_type(self):
        self.assertTrue(validate_chart_type('1'))
        self.assertTrue(validate_chart_type('2'))
        self.assertFalse(validate_chart_type('3'))

    def test_validate_time_series(self):
        self.assertTrue(validate_time_series('1'))
        self.assertTrue(validate_time_series('2'))
        self.assertFalse(validate_time_series('5'))

    def test_validate_date(self):
        self.assertTrue(validate_date('2022-01-01'))
        self.assertFalse(validate_date('01-01-2022'))

def main():
    while True:
        try:
            symbol = get_symbol()
            chart_type = get_chart()
            values = get_time_series()
            start_end = get_dates()

            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_{}&symbol={}&interval={}&apikey=9I22O100RNSZ6IPR'.format(values[0], symbol, values[1])

            response = requests.get(url)
            data = json.loads(response.text)

            i = 0
            key = ""

            for item in data:
                if i == 1:
                    key = item
                i += 1

            dates = []

            for item in data[key]:
                dates.append(item)

            usable_dates = []
            open_values = []
            high_values = []
            low_values = []
            close_values = []

            for x in dates:
                x_time_obj = datetime.strptime(x, '%Y-%m-%d')

                if x_time_obj >= start_end[0] and x_time_obj <= start_end[1]:
                    for item in data[key][x]:
                        if 'open' in item:
                            open_values.append(float(data[key][x][item]))
                        elif 'high' in item:
                            high_values.append(float(data[key][x][item]))
                        elif 'low' in item:
                            low_values.append(float(data[key][x][item]))
                        elif 'close' in item:
                            close_values.append(float(data[key][x][item]))

            if chart_type == 1:
                bar_chart = pygal.Bar()
                bar_chart.title = 'Stock Data for IBM: {} to {}'.format(str(start_end[0]), str(start_end[1]))
                bar_chart.x_labels = [x for x in usable_dates]
                bar_chart.add('open', open_values)
                bar_chart.add('high', high_values)
                bar_chart.add('low', low_values)
                bar_chart.add('close', close_values)
                bar_chart.render_to_file('bar_chart.svg')
                webbrowser.open('bar_chart.svg')
            
            elif chart_type == 2:
                line_chart = pygal.HorizontalLine()
                line_chart.title = 'Stock Data for IBM: {} to {}'.format(str(start_end[0]), str(start_end[1]))
                line_chart.x_labels = [x for x in usable_dates]
                line_chart.add('open', open_values)
                line_chart.add('high', high_values)
                line_chart.add('low', low_values)
                line_chart.add('close', close_values)
                line_chart.render_to_file('line_chart.svg')
                webbrowser.open('line_chart.svg')

            run_again = input("Would you like to view more stock data? Press 'y' to continue: ")

            if run_again.lower() != 'y':
                break

        except:
            print("Invalid option. Try again.")
            continue

if __name__ == '__main__':
    unittest.main()
    main()
