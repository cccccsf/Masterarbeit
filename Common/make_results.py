#!/usr/bin/python3
import os
import csv
import json


def creat_json_file(path):
    json_file = os.path.join(path, 'results.json')
    if not os.path.exists(json_file):
        info = {}
        with open(json_file, 'w') as f:
            json.dump(info, f, indent=4)
    else:
        pass


def record_data_json(path, item, value, section='basis'):
    json_file = os.path.join(path, 'results.json')
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        creat_json_file(path)
        with open(json_file, 'r') as f:
            data = json.load(f)
    if section not in data:
        data[section] = {}
    data[section][item] = value
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


def creat_csv_file(path):
    csv_file = os.path.join(path, 'results.csv')
    if not os.path.exists(csv_file):
        headers = ['item', 'bilayer', 'upperlayer', 'underlayer', 'interlayer']
        with open(csv_file, 'w', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)


def record_data_csv(path, item, value, layer='bilayer'):
    csv_file = os.path.join(path, 'results.csv')
    if not os.path.exists(csv_file):
        creat_csv_file(path)
    try:
        if layer.lower() == 'bilayer':
            new_line = [item, value]
        elif layer.lower() == 'upperlayer':
            new_line = [item, '', value]
        elif layer.lower() == 'underlayer':
            new_line = [item, '', '', value]
        elif layer.lower() == 'whole layer':
            new_line = [item, value[0], value[1], value[2], value[3]]
        elif layer.lower() == 'interlayer':
            new_line = [item, '', '', '', value]
        with open(csv_file, 'a', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(new_line)
    except Exception as e:
        print(e)
