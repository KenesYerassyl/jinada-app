from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
import sys

# from PyQt6.QtCore import Qt, QSize, QTimer, QThread, QThreadPool
# from utils.file_upload import FileUploadWidget
# from utils.video_processing import VideoProcessor
# import sys
# import os


# areas = [
#     [
#         [(615, 251), (500, 393), (759, 493), (775, 454), (545, 390), (668, 253)],
#         [(693, 256), (573, 383), (799, 445), (839, 313)],
#     ],
#     [
#         [
#             (677, 354),
#             (556, 241),
#             (276, 348),
#             (353, 495),
#             (404, 489),
#             (325, 366),
#             (542, 272),
#             (654, 371),
#         ],
#         [(537, 281), (339, 367), (421, 489), (644, 375)],
#     ],
#     [
#         [(653, 219), (649, 500), (746, 500), (744, 229)],
#         [(758, 236), (756, 500), (1020, 500), (1016, 294)],
#     ],
# ]


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setMinimumSize(QSize(1280, 720))
#         self.setWindowTitle("Violette")

#         self.statistics = {}

#         self.threadpool = QThreadPool()

#         self.fileUploadWidget = FileUploadWidget()
#         self.fileUploadWidget.videoAdded.connect(self.addVideoToList)

#         self.videoListWidget = QListWidget()
#         self.numberOfVideos = 0

#         self.pagelayout = QVBoxLayout()
#         self.pagelayout.addWidget(self.fileUploadWidget)
#         self.pagelayout.addWidget(self.videoListWidget)

#         widget = QWidget()
#         widget.setLayout(self.pagelayout)
#         self.setCentralWidget(widget)

#     def addVideoToList(self, filePath):
#         itemWidget = QWidget()
#         itemLayout = QHBoxLayout()
#         itemWidget.setLayout(itemLayout)

#         videoLabel = QLabel(filePath)
#         itemLayout.addWidget(videoLabel)

#         progressBar = QProgressBar()
#         progressBar.setMinimum(0)
#         itemLayout.addWidget(progressBar)

#         downloadButton = QPushButton("Download")
#         downloadButton.setVisible(False)
#         downloadButton.clicked.connect(
#             lambda: self.download_statistics(self.numberOfVideos)
#         )
#         itemLayout.addWidget(downloadButton)

#         listItem = QListWidgetItem()
#         listItem.setSizeHint(itemWidget.sizeHint())
#         self.videoListWidget.addItem(listItem)
#         self.videoListWidget.setItemWidget(listItem, itemWidget)

#         currentId = self.numberOfVideos
#         self.processVideo(filePath, progressBar, downloadButton, currentId)
#         self.numberOfVideos += 1

#     def processVideo(self, filePath, progressBar, downloadButton, currentId):

#         baseName = os.path.basename(filePath)
#         name, extension = os.path.splitext(baseName)
#         targetArea = areas[int(name[-1])]
#         newName = name + "_processed"

#         processor = VideoProcessor(filePath, targetArea, newName, currentId)
#         processor.signals.progress.connect(progressBar.setValue)
#         processor.signals.maximum.connect(progressBar.setMaximum)
#         processor.signals.finished.connect(lambda: downloadButton.setVisible(True))
#         processor.signals.finished.connect(lambda: progressBar.setVisible(False))
#         processor.signals.result.connect(
#             lambda stats, currentId: self.handleResult(stats, currentId)
#         )
#         self.threadpool.start(processor)

#     def handleResult(self, stats, currentId):
#         self.statistics[currentId] = stats

#     def download_statistics(self, currentId):
#         print(self.statistics)
#         if currentId in self.statistics:
#             stats = self.statistics[currentId]
#             filename = f"{currentId}_statistics.txt"
#             with open(filename, "w") as file:
#                 for key, value in stats.items():
#                     file.write(f"{key}: {value}\n")
#             print(f"Downloaded statistics for {currentId} to {filename}")
#         else:
#             print(f"No statistics available for {currentId}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
