from PyQt6.QtCore import QObject, QThreadPool, pyqtSignal
from utils.video_processing_worker import VideoProcessingWorker
from threading import Lock
from utils.model import Model
from utils.tracker_utility import TrackerUtility
from utils.constants import Error


class Singleton(type(QObject), type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class CentralVideoProcessingManager(QObject, metaclass=Singleton):
    progress_updated = pyqtSignal(int, int, int)
    finished = pyqtSignal(int, int)
    tasks = {}
    thread_pool = QThreadPool.globalInstance()
    model = Model()
    tracker = TrackerUtility()
    _lock = Lock()

    def __init__(self):
        super().__init__()

    def add_task(self, object_id, record_id):
        task = {"record_id": record_id, "progress": 0}
        try:
            worker = VideoProcessingWorker(
                object_id, task["record_id"], self.model, self.tracker, visual=True
            )
            worker.signals.progress_updated.connect(self.on_progress_updated)
            worker.signals.finished.connect(self.on_finished)

            if object_id not in self.tasks:
                self.tasks[object_id] = []
            self.tasks[object_id].append(task)
            self.thread_pool.start(worker)
        except Exception as e:
            print(f"{Error.ERROR_WHILE_ADDING_TASK} {e}")

    def get_tasks(self, object_id):
        return self.tasks[object_id]

    def remove_task(self, object_id, record_id):
        if object_id in self.tasks:
            for task in self.tasks[object_id]:
                if task["record_id"] == record_id:
                    self.tasks[object_id].remove(task)
                    break
            if not self.tasks[object_id]:
                del self.tasks[object_id]

    def update_task(self, object_id, record_id, progress):
        if object_id in self.tasks:
            for task in self.tasks[object_id]:
                if task["record_id"] == record_id:
                    task["progress"] = progress
                    break

    def on_progress_updated(self, object_id, record_id, progress):
        self.update_task(object_id, record_id, progress)
        self.progress_updated.emit(object_id, record_id, progress)

    def on_finished(self, object_id, record_id):
        self.remove_task(object_id, record_id)
        self.finished.emit(object_id, record_id)
