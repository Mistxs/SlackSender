# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

import pymysql
import requests
from flask import Flask, render_template, request, jsonify, Response, Blueprint

chticket = Blueprint('chticket', __name__)

def rzdfind(date,cityfrom, cityto):
  url = "https://ticket.rzd.ru/apib2b/p/Railway/V1/Search/TrainPricing?service_provider=B2B_RZD"

  payload = json.dumps({
    "Origin": cityfrom,
    "Destination": cityto,
    "DepartureDate": date,
    "TimeFrom": 0,
    "TimeTo": 24,
    "CarGrouping": "DontGroup",
    "GetByLocalTime": True,
    "SpecialPlacesDemand": "StandardPlacesAndForDisabledPersons"
  })
  headers = {
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'sentry-trace': 'a77deacef2644df4a2669794039f9a4e-87b5ea91c660179e-1',
    'sec-ch-ua-platform': '"macOS"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'host': 'ticket.rzd.ru',
    'Cookie': 'session-cookie=177670e7b0b2a17dbd64334d6940ac72715fcb65feb24b902687c9746d324c6084e21755e85917975c092188951a8ad2'
  }

  response = requests.request("POST", url, headers=headers, data=payload).json()
  return response

def getprice(data, current_date_str):
    min_prices = {}
    for item in data["Trains"]:
      vagon = item["CarGroups"]
      for _ in vagon:
        date = current_date_str
        splitted = date.split("T")
        date = splitted[0]
        train = item["DisplayTrainNumber"]
        arrival = item["ArrivalDateTime"]
        departure = item["DepartureDateTime"]
        price = _['MinPrice']
        vagon_type = _['CarTypeName']
        disabledpersonflag = _["HasPlacesForDisabledPersons"]

        if date not in min_prices:
          min_prices[date] = {}

        if vagon_type not in min_prices[date]:
          min_prices[date][vagon_type] = {}


        if not disabledpersonflag and ("price" not in min_prices[date][vagon_type] or price < min_prices[date][vagon_type]["price"]):
          min_prices[date][vagon_type] = {
            "train": train,
            "departure" : departure,
            "arrival": arrival,
            "price": price
          }

    return min_prices



@chticket.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('search')

    connection = pymysql.connect(**db_params)
    with connection.cursor() as cursor:
        sql = "SELECT cyrname, id FROM cities WHERE cyrname LIKE %s LIMIT 10"
        cursor.execute(sql, f"%{search}%")
        result = cursor.fetchall()

    connection.close()

    city_list = [{'label': city['cyrname'], 'value': city['id']} for city in result]
    return jsonify(city_list)



@chticket.route('/search')
def search():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    cityfrom = request.args.get('city1')
    cityto = request.args.get('city2')

    return Response(event_stream(start_date, end_date, cityto, cityfrom), content_type="text/event-stream")


def event_stream(start_date, end_date, cityto, cityfrom):
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    end_date = datetime.strptime(end_date, "%d-%m-%Y")

    total_days = (end_date - start_date).days+1


    a = []
    min_prices_cal = {}

    current_date = start_date

    while current_date <= end_date:
        current_date_str = current_date.strftime("%Y-%m-%dT%H:%M:%S")
        data = rzdfind(current_date_str,cityfrom,cityto)
        min_prices_cal.update(getprice(data, current_date_str))
        current_date += timedelta(days=1)
        # print(min_prices_cal)
        save_tickets_to_db(min_prices_cal, cityfrom, cityto)

        days_passed = (current_date - start_date).days
        progress = (days_passed / total_days) * 100

        progress_data = {
            'progress': progress,
            'data': min_prices_cal
        }

        yield f"data: {json.dumps(progress_data)}\n\n"




# Параметры подключения к базе данных MySQL
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ose7vgt5',
    'db': 'rzd',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_train_data(date, cityfrom, cityto):
    connection = pymysql.connect(**db_params)
    cursor = connection.cursor()

    cursor.execute('''
        SELECT train_number, departure_date, arrival_date, category, ticket_price
        FROM trains
        JOIN tickets ON trains.id = tickets.train_id
        WHERE departure_station_id = %s AND arrival_station_id = %s AND date(departure_date) = %s
    ''', (cityfrom, cityto, date))

    train_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return train_data

def save_tickets_to_db(min_prices_cal, departure_station_id, arrival_station_id):
    connection = pymysql.connect(**db_params)
    cursor = connection.cursor()

    for date, ticket_data in min_prices_cal.items():
        for category, ticket_info in ticket_data.items():
            train_number = ticket_info['train']
            departure_date = ticket_info['departure']
            arrival_date = ticket_info['arrival']
            price = ticket_info['price']

            # Получаем train_id по train_number и departure_date
            cursor.execute('SELECT id FROM trains WHERE train_number = %s AND departure_date = %s',
                           (train_number, departure_date))

            train_id_row = cursor.fetchone()

            if train_id_row:
                train_id = (train_id_row["id"])

                # Проверяем, есть ли уже билеты на этот поезд в таблице tickets
                cursor.execute('SELECT id FROM tickets WHERE train_id = %s and category = %s', (train_id,category))
                existing_tickets = cursor.fetchall()
                if existing_tickets:
                    for ticket_id in existing_tickets:
                        cursor.execute('UPDATE tickets SET ticket_price = %s WHERE id = %s', (price, ticket_id["id"]))
                else:
                    cursor.execute('INSERT INTO tickets (train_id, category, ticket_price) VALUES (%s, %s, %s)', (train_id, category, price))

            else:
                # Добавляем новый поезд и билеты
                cursor.execute(
                    'INSERT INTO trains (train_number, departure_date, arrival_date, departure_station_id, arrival_station_id) VALUES (%s, %s, %s, %s, %s)',
                    (train_number, departure_date, arrival_date, departure_station_id, arrival_station_id))
                train_id = cursor.lastrowid
                cursor.execute('INSERT INTO tickets (train_id, category, ticket_price) VALUES (%s, %s, %s)',
                               (train_id, category, price))
    connection.commit()
    cursor.close()
    connection.close()



