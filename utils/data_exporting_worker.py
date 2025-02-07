from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
import logging
from utils.constants import AppLabels, Error
import traceback
import datetime
import pandas as pd
import numpy as np
from paths import Paths
from typing import Dict, List
from db.db import get_records_for_export, get_object_by_id

class DataExportingWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, start_date: datetime.date, end_date: datetime.date, object_id: int, filepath: str):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.object_id = object_id
        self.filepath = filepath


    def export_data(self) -> None:
        try:
            try:
                object_info = get_object_by_id(self.object_id)
                records = get_records_for_export(self.start_date, self.end_date, self.object_id)
            except Exception as e:
                raise Exception(f"Error getting object info or records: {e}")
            
            data: Dict[str, List] = {
                AppLabels().DATA_EXPORT_NAME: [object_info["name"]],
                AppLabels().DATA_EXPORT_DATES: [self.start_date.strftime("%Y-%m-%d %H:%M:%S"), self.end_date.strftime("%Y-%m-%d %H:%M:%S")],
                AppLabels().DATA_EXPORT_INFRAME: [],
                AppLabels().DATA_EXPORT_NUMOFVISITORS: [],
                AppLabels().DATA_EXPORT_TIMESPENT_TOT: [],
                AppLabels().DATA_EXPORT_TIMESPENT_AVG: [],
            }

            max_num_of_frames = 0

            for record in records:
                try:
                    np_data = np.load(Paths.record_data_npz(record_id=record), allow_pickle=True)
                    np_data["time_spent"] = [np.sum(item) for item in np_data["time_spent"]]
                    max_num_of_frames = max(max_num_of_frames, len(np_data["visitors"]))
                    
                    for i in range(len(np_data["visitors"])):
                        if i >= len(data[AppLabels().DATA_EXPORT_NUMOFVISITORS]):
                            data[AppLabels().DATA_EXPORT_NUMOFVISITORS].append(np_data["visitors"][i])
                            data[AppLabels().DATA_EXPORT_TIMESPENT_TOT].append(np_data["time_spent"][i])
                        else:
                            data[AppLabels().DATA_EXPORT_NUMOFVISITORS][i] += np_data["visitors"][i]
                            data[AppLabels().DATA_EXPORT_TIMESPENT_TOT][i] += np_data["time_spent"][i]

                except FileNotFoundError:
                    logging.warning(f"File not found for record ID: {record}")
                    continue

            for i in range(max_num_of_frames):

                data[AppLabels().DATA_EXPORT_INFRAME].append(i + 1)
                if data[AppLabels().DATA_EXPORT_NUMOFVISITORS][i] > 0:
                    data[AppLabels().DATA_EXPORT_TIMESPENT_TOT][i] /= 60.0
                    avg_time = data[AppLabels().DATA_EXPORT_TIMESPENT_TOT][i] / data[AppLabels().DATA_EXPORT_NUMOFVISITORS][i]
                    data[AppLabels().DATA_EXPORT_TIMESPENT_AVG].append(avg_time)
                else:
                    data[AppLabels().DATA_EXPORT_TIMESPENT_AVG].append(0)

            max_num_of_frames = max(max_num_of_frames, 2)

            for key in data:
                if len(data[key]) < max_num_of_frames:
                    data[key].extend([''] * (max_num_of_frames - len(data[key])))

            df = pd.DataFrame(data).T

            with pd.ExcelWriter(self.filepath, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Sheet1", header=False)
                worksheet = writer.sheets["Sheet1"]
                for column in worksheet.columns:
                    max_length = max(len(str(cell.value)) for cell in column)
                    worksheet.column_dimensions[column[0].column_letter].width = max_length + 2
            logging.info(f"Exported data to {self.filepath}")
        except Exception as e:
            raise Exception(f"Something went wrong in func export_data(): {e}")


    @pyqtSlot()
    def run(self):
        try:
            self.export_data()
            self.finished.emit()
        except Exception as e:
            logging.error(f"{traceback.format_exc()}\n{e}")
            self.error.emit(Error().ERROR_DURING_FILE_EXPORTING)