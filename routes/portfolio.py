# This blueprint handles the portfolio page

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
from vnquant import plot as pl
import pandas as pd
from controller import stock_manager
import datetime
from app import model, chat_config
import operator

portfolio = Blueprint('portfolio', __name__, template_folder='templates')

import json

data_stocks = []
start = str('2019-09-01')
end = str('2023-11-01')

@portfolio.route('/', methods=['GET'])
def portfolio_home():
    graph_json = pl.vnquant_candle_stick(
        data='VND',
        title='VND symbol from 2019-09-01 to 2023-11-01',
        xlab='Date', ylab='Price',
        start_date='2019-09-01',
        end_date='2023-11-01',
        data_source='CAFE',
        show_advanced=['volume', 'macd', 'rsi']
    )   

    with open('static/stocks.txt', 'r') as f:
        stocks = f.read().splitlines()

    global data_stocks
    start_date = str(datetime.datetime.now().date() - datetime.timedelta(days=1))
    end_date = str(datetime.datetime.now().date() - datetime.timedelta(days=1))
    if len(data_stocks) == 0 or data_stocks[0].time != str(datetime.datetime.now().date()):
        data_stocks = stock_manager.StockManager(
            symbols=stocks, start=start_date, end=end_date, data_source='CAFE', minimal=True, table_style='levels'
        ).get_stock_data()
        data_stocks.sort(key=operator.attrgetter('time'), reverse=True)

    num_rows = len(data_stocks)

    data_prompt = []
    for i in range(num_rows):
        data_prompt.append({data_stocks[i].name: {"time": data_stocks[i].time, "open": data_stocks[i].open, "high": data_stocks[i].high, "low": data_stocks[i].low, "close": data_stocks[i].close, "volume": data_stocks[i].volume}})

    data_prompt = str(data_prompt)

    prompt = "You are an expert in stock market. With given data_stocks, can you provide some insights that can help new investors?"
    length = "Your response should be at most 300 words. Consider providing insights on the stock market trends, the performance of the stocks, and the potential risks and benefits of investing in these stocks."
    type =  "And your response type should be in the form of a paragraph."
    prevent = "In paragraph, there is no need to include any code or code snippets. Just provide insights."
    prompt = data_prompt + prompt + length + type + prevent
    
    gemini_response= model.generate_content(prompt).text
    # gemini_response = {"text": "No response from gemini"}
    global start, end
    data = {'graph_json': graph_json, 'data_stocks': data_stocks, 'num_rows': num_rows, 'gemini_response': gemini_response, 'start_date': start, 'end_date': end}

    return render_template('home.html', data=data)
    

@portfolio.route('/gemini', methods=['POST'])
def gemini():
    user_input = request.form['userinput']
    response = model.generate_content(user_input)
    return response.text
        

@portfolio.route('/investment', methods=['GET', 'POST'])
def investments():
    if request.method == 'GET':
        return render_template('investment.html')
    stock = request.form['stock']
    amount = request.form['amount']
    return render_template('investment.html', success="Investment successful")

graph_stock_data_name: str = 'VND'

@portfolio.route('/graph', methods=['POST'])
def change_graph():
    try:
        # Parse JSON from the request
        global start, end, graph_stock_data_name

        payload = request.get_json()
        column_data = payload['data']
        graph_stock_data_name = column_data[0]

        # Generate the graph
        graph_json = pl.vnquant_candle_stick(
            data=column_data[0],
            title=f'{column_data[0]} symbol from {start} to {end}',
            xlab='Date', ylab='Price',
            start_date=start,
            end_date=end,
            data_source='CAFE',
            show_advanced=['volume', 'macd', 'rsi']
        )

        # Return the graph data as JSON
        return jsonify(graph_json)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # return render_template('home.html', graph_json=graph_json, data=data, num_rows=len(data), gemini_response="No response from gemini")


@portfolio.route('/date', methods=['POST'])
def change_date():
    try:
        # Parse JSON from the request
        global start, end, graph_stock_data_name

        payload = request.get_json()
        start = payload['start_date']
        end = payload['end_date']

        # Generate the graph
        graph_json = pl.vnquant_candle_stick(
            data=graph_stock_data_name,
            title=f'{graph_stock_data_name} symbol from {start} to {end}',
            xlab='Date', ylab='Price',
            start_date=start,
            end_date=end,
            data_source='CAFE',
            show_advanced=['volume', 'macd', 'rsi']
        )

        # Return the graph data as JSON
        return jsonify(graph_json)
    except KeyError as e:
        return jsonify({"error": f"Missing key: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400