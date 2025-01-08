# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
# from PyQt6.QtCore import QSize, QDate
# from datetime import date
# from db.db import get_all_records_for_list
# import numpy as np
# import pyqtgraph as pg
# from utils.constants import AppLabels
# from paths import Paths


# class DataPresenterModel:

#     def __init__(self, object_id: int, start_date: date, end_date: date):
#         self.object_id = object_id
#         self.start_date = start_date
#         self.end_date = end_date
#         self.dates = []
#         self.per_exhibit = []
#         self.per_day = []
#         self.was_data_found = False


#         records = get_all_records_for_list(object_id)
#         visitors_per_exhibit: np.ndarray = None
#         timespent_per_exhibit: np.ndarray = None

#         for record in records:
#             record_id = record[0]
#             is_processed = record[3]
#             date_created = record[2].date()
#             if not is_processed or self.start_date > date_created or date_created > self.end_date:
#                 continue

#             npfile = np.load(Paths.record_data_npz(record_id), allow_pickle=True)
#             if np.sum(npfile["visitors"]) == 0:
#                 continue
#             time_spent = self.convert_to_min(npfile["time_spent"])
#             visitors = npfile["visitors"]
            
#             self.dates.append((date_created - date(2000, 1, 1)).days)
#             self.per_day.append(
#                 (
#                     np.sum(visitors),
#                     np.mean(visitors),
#                     np.mean(np.concatenate(time_spent)),
#                 )
#             )

#             if visitors_per_exhibit is None and timespent_per_exhibit is None:
#                 self.was_data_found = True
#                 visitors_per_exhibit = visitors
#                 timespent_per_exhibit = time_spent
#             else:
#                 if len(visitors_per_exhibit) != len(visitors) or len(timespent_per_exhibit) != len(time_spent):
#                     raise Exception("Recordings shape mismatch")
#                 visitors_per_exhibit = np.column_stack((visitors_per_exhibit, visitors))
#                 for i in range(len(timespent_per_exhibit)):
#                     timespent_per_exhibit[i] = list(timespent_per_exhibit[i]) + list(time_spent[i])
        
#         for i in range(len(visitors_per_exhibit)):
#             self.per_exhibit.append((np.sum(visitors_per_exhibit[i]), np.mean(visitors_per_exhibit[i]), np.mean(timespent_per_exhibit[i])))
#         self.per_day = np.array(self.per_day)
#         self.per_exhibit = np.array(self.per_exhibit)


#     def convert_to_min(self, time_spent: np.ndarray):
#         return [[cell / 60 for cell in row] for row in time_spent]

#     def convert_to_hour(self, time_spent: np.ndarray):
#         return [[cell / 3600 for cell in row] for row in time_spent]


# class DataPresenterWidget(QWidget):
#     """
#     total number of visitors per exhibit - bar graph
#     avg number of visitors per exhibit - bar graph
#     avg time spent per exhibit - bar graph

#     change of total number of visitors per exhibit - line graph
#     change of avg number of visitors per exhibit - line graph
#     change of avg time spent per exhibit - line graph

#     """
#     def __init__(self, object_id: int, start_date: date, end_date: date):
#         super().__init__()
#         self.setMinimumSize(QSize(1280, 720))
#         self.model = DataPresenterModel(object_id, start_date, end_date)
#         if self.model.was_data_found:
#             self.prepare_date()
#         else:
#             pass

#     def prepare_date(self):
#         layout = QVBoxLayout()

#         plot_container = pg.GraphicsLayoutWidget()
#         bar_graph1 = plot_container.addPlot(title=AppLabels().BAR_GRAPH1, row=0, col=0)
#         self.create_bar_graph(
#             bar_graph1,
#             np.arange(len(self.model.per_exhibit)),
#             self.model.per_exhibit[:, 0],
#             AppLabels().BAR_GRAPH_VISITORS_YLABEL,
#         )

#         bar_graph2 = plot_container.addPlot(title=AppLabels().BAR_GRAPH2, row=1, col=0)
#         self.create_bar_graph(
#             bar_graph2,
#             np.arange(len(self.model.per_exhibit)),
#             self.model.per_exhibit[:, 1],
#             AppLabels().BAR_GRAPH_VISITORS_YLABEL,
#         )
#         bar_graph3 = plot_container.addPlot(title=AppLabels().BAR_GRAPH3, row=2, col=0)
#         self.create_bar_graph(
#             bar_graph3,
#             np.arange(len(self.model.per_exhibit)),
#             self.model.per_exhibit[:, 2],
#             AppLabels().BAR_GRAPH_TIME_YLABEL,
#         )

#         line_graph1 = plot_container.addPlot(title=AppLabels().LINE_GRAPH1, row=0, col=1)
#         self.create_line_graph(
#             line_graph1,
#             self.model.dates,
#             self.model.per_day[:, 0],
#             AppLabels().LINE_GRAPH_VISITORS_YLABEL,
#         )
#         line_graph2 = plot_container.addPlot(title=AppLabels().LINE_GRAPH2, row=1, col=1)
#         self.create_line_graph(
#             line_graph2,
#             self.model.dates,
#             self.model.per_day[:, 1],
#             AppLabels().LINE_GRAPH_VISITORS_YLABEL,
#         )
#         line_graph3 = plot_container.addPlot(title=AppLabels().LINE_GRAPH3, row=2, col=1)
#         self.create_line_graph(
#             line_graph3,
#             self.model.dates,
#             self.model.per_day[:, 2],
#             AppLabels().LINE_GRAPH_TIME_YLABEL,
#         )

#         layout.addWidget(plot_container)
#         self.setLayout(layout)

#     def create_line_graph(self, plot, x, y, left_label):
#         plot.plot(x, y, pen=pg.mkPen(color="red", width=2))
#         plot.setLabel("bottom", AppLabels().LINE_GRAPH_XLABEL)
#         plot.setLabel("left", left_label)
#         plot.showGrid(x=True, y=True)
        
#         start_date = QDate(2000, 1, 1)
#         formatted_dates = []
#         for day in x:
#             date = start_date.addDays(day)
#             formatted_dates.append(date.toString("dd-MM-yy"))

#         ticks = [(x[i], formatted_dates[i]) for i in range(len(x))]
#         plot.getAxis("bottom").setTicks([ticks])
#         plot.getViewBox().setLimits(
#             xMin=min(x),
#             xMax=max(x),
#             yMin=min(y),
#             yMax=max(y),
#             minXRange=(max(x) - min(x)) / 10,
#             maxXRange=max(x) - min(x),
#             minYRange=(max(y) - min(y)) / 10,
#             maxYRange=max(y) - min(y),
#         )

#     def create_bar_graph(self, plot, x, height, left_label):
#         bar_graph = pg.BarGraphItem(
#             x=x,
#             height=height,
#             width=0.5,
#             brush="blue",
#         )
#         plot.addItem(bar_graph)
#         plot.setLabel("bottom", AppLabels().BAR_GRAPH_XLABEL)
#         plot.setLabel("left", left_label)
#         plot.showGrid(x=True, y=True)

#         ticks = [(x[i], f"{AppLabels().EXHIBIT} {i+1}") for i in range(len(x))]
#         plot.getAxis("bottom").setTicks([ticks])
