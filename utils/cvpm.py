from PyQt6.QtCore import QObject, QThreadPool, pyqtSignal
from threading import Lock
from utils.video_processing_worker import VideoProcessingWorker
import logging
import time

# TODO: make cancel emit to worker class
# NOTE: COMMUNICATION BETWEEN THREADS MUST BE DONE THROUGH SIGNALS AND SLOTS !!!

class Singleton(type(QObject), type):
    """Metaclass for Singleton pattern implementation."""
    _lock = Lock()

    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        """Override __call__ to ensure only one instance of the class."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__call__(*args, **kwargs)
                logging.debug(f"Created new singleton instance of {cls.__name__}")
        return cls._instance


class CentralVideoProcessingManager(QObject, metaclass=Singleton):
    """Manager for handling video processing tasks in a central manner."""

    progress_updated = pyqtSignal(int, int, int)
    finished = pyqtSignal(int, int)
    tasks = {}
    thread_pool = QThreadPool.globalInstance()
    lock = Lock()

    def __init__(self):
        super().__init__()
        logging.info("Initialized CentralVideoProcessingManager.")

    def add_task(self, object_id: int, record_id: int) -> None:
        """
        Adds a new video processing task to the task queue and starts processing.
        
        Args:
            object_id (int): Unique identifier for the object.
            record_id (int): Unique identifier for the record being processed.
        """
        try:
            worker = VideoProcessingWorker(object_id, record_id, visual=True)
            worker.signals.progress_updated.connect(self.on_progress_updated)
            worker.signals.finished.connect(self.on_finished)
            task = {"record_id": record_id, "progress": 0, "worker": worker, "start_time": time.time()}

            with self.lock:
                if object_id not in self.tasks:
                    self.tasks[object_id] = []
                self.tasks[object_id].append(task)
                logging.info(f"Task added for object {object_id}, record {record_id}")
            self.thread_pool.start(worker)
        except Exception as e:
            logging.error(f"Error while trying to add task to the queue: {e}")

    def get_tasks(self, object_id: int) -> dict:
        """
        Retrieves all tasks associated with the given object_id.

        Args:
            object_id (int): Unique identifier for the object.

        Returns:
            list: List of tasks for the object.
        """
        with self.lock:
            return self.tasks[object_id]

    def remove_task(self, object_id: int, record_id: int) -> None:
        try:
            with self.lock:
                if object_id in self.tasks:
                    logging.info(f"Removing task for object {object_id}, record {record_id}.")
                    for task in self.tasks[object_id]:
                        if task["record_id"] == record_id:
                            worker = task["worker"]
                            if worker:
                                worker.signals.progress_updated.disconnect()
                                worker.signals.finished.disconnect()
                            del worker
                            self.tasks[object_id].remove(task)
                            logging.info(f"Task for object {object_id} has been canceled.")
                            break

                    if len(self.tasks[object_id]) == 0:
                        del self.tasks[object_id]
                        logging.debug(f"Deleted task list for object {object_id}.")
        except Exception as e:
            logging.error(f"Error removing task: {e}")

    def cancel_tasks(self, object_id: int, record_id: int = -1) -> None:
        try:
            with self.lock:
                if object_id in self.tasks:
                    for task in self.tasks[object_id]:
                        if record_id != -1 and task["record_id"] != record_id:
                            continue
                        worker = task["worker"]
                        if worker:
                            worker.cancel()
                            worker.signals.progress_updated.disconnect()
                            worker.signals.finished.disconnect()
                        del worker
                        if record_id != -1:
                            break
                        logging.info(f"Task for object {object_id} has been canceled.")
                    del self.tasks[object_id]
        except Exception as e:
            logging.error(f"Error canceling tasks with object id {object_id}: {e}")


    def update_task(self, object_id: int, record_id: int, progress: int) -> None:
        """
        Updates the progress of an existing task.

        Args:
            object_id (int): Unique identifier for the object.
            record_id (int): Unique identifier for the record.
            progress (int): The new progress value.
        """
        try:
            with self.lock:
                if object_id in self.tasks:
                    for task in self.tasks[object_id]:
                        if task["record_id"] == record_id:
                            task["progress"] = progress
                            break
        except Exception as e:
            logging.error(f"Error updating task progress: {e}")

    def on_progress_updated(self, object_id: int, record_id: int, progress: int) -> None:
        """
        Slot method to handle progress updates from worker threads.

        Args:
            object_id (int): Unique identifier for the object.
            record_id (int): Unique identifier for the record.
            progress (int): The progress value from the worker.
        """
        self.update_task(object_id, record_id, progress)
        self.progress_updated.emit(object_id, record_id, progress)

    def on_finished(self, object_id: int, record_id: int) -> None:
        """
        Slot method to handle task completion.

        Args:
            object_id (int): Unique identifier for the object.
            record_id (int): Unique identifier for the record.
        """
        time_elapsed = -1

        #TEMP BEGIN: For debugging purposes
        if object_id in self.tasks:
            for task in self.tasks[object_id]:
                if task["record_id"] == record_id:
                    time_elapsed = time.time() - task["start_time"]
                    logging.info("Task finished in {:.2f} minutes.".format(time_elapsed / 60))
                    break
        #TEMP END
        self.remove_task(object_id, record_id)
        self.finished.emit(object_id, record_id)
        logging.info(f"Task finished for object {object_id}, record {record_id}.")
