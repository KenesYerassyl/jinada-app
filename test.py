import numpy as np
from paths import Paths
from datetime import datetime, timedelta
from db.db import insert_record, get_records_for_export
from db.object import ObjectRecord
from PyQt6.QtCore import QStandardPaths
import os

# def print_data():
#     data = np.load("/Users/Yerassyl/Library/Application Support/.jinada_appdata/record_data/1.npz", allow_pickle=True)
#     print(data["visitors"])
#     print(data["time_spent"])

# print_data()


def generate_data(record_id):
    rng = np.random.default_rng()
    n = 10 # number of polygons 
    visitors = rng.integers(low=20, high=40, size=n)
    for i in range(n):
        if np.random.randint(0, 1000000) % (n - i) == 0:
            visitors[i] += np.random.randint(20, 50)
    time_spent = []
    for num in visitors:
        time_spent.append(rng.integers(low=100, high=200, size=num))
        for i in range(num):
            if np.random.randint(0, 1000000) % (num - i) == 0:
                time_spent[-1][i] += np.random.randint(20, 50)

    visitors = np.array(visitors, dtype=object)
    time_spent = np.array(time_spent, dtype=object)
    np.savez(Paths.record_data(record_id), visitors=visitors, time_spent=time_spent)

def generate_records():
    days = datetime(2024, 11, 1)

    for _ in range(30):
        object_record = ObjectRecord(file_path="some_path", date_uploaded=days)
        object_record.is_processed = True
        id = insert_record(1, object_record)
        generate_data(id)
        days += timedelta(1)

# generate_records()