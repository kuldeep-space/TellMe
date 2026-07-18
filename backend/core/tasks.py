import uuid
from typing import Callable, Any, Optional
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    started = Signal(str)
    finished = Signal(str)
    error = Signal(str, Exception)
    result = Signal(str, object)
    progress = Signal(str, int)
    # Generic streaming event signal (taskId, EventObject)
    stream_event = Signal(str, object)

class TaskWorker(QRunnable):
    """
    Worker thread that executes a given function with a Task context.
    """
    def __init__(self, task_id: str, fn: Callable, *args, **kwargs):
        super().__init__()
        self.task_id = task_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.is_cancelled = False

    def run(self):
        self.signals.started.emit(self.task_id)
        try:
            # Inject context if the function supports it (e.g. self)
            # For simplicity, if kwargs has 'worker', pass it
            if 'worker' in self.kwargs:
                self.kwargs['worker'] = self
            
            result = self.fn(*self.args, **self.kwargs)
            
            if not self.is_cancelled:
                self.signals.result.emit(self.task_id, result)
        except Exception as e:
            if not self.is_cancelled:
                self.signals.error.emit(self.task_id, e)
        finally:
            self.signals.finished.emit(self.task_id)

class TaskManager(QObject):
    """
    Centralized infrastructure for executing all asynchronous background tasks
    (e.g., AI Requests, Report Generation, PDF Processing).
    """
    
    # Global task events
    task_started = Signal(str)
    task_finished = Signal(str)
    task_failed = Signal(str, Exception)
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TaskManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        self.active_tasks: dict[str, TaskWorker] = {}

    def submit(self, fn: Callable, *args, **kwargs) -> str:
        """Submit a task to the background pool. Returns a Task ID."""
        task_id = str(uuid.uuid4())
        worker = TaskWorker(task_id, fn, *args, **kwargs)
        
        # Connect signals
        worker.signals.started.connect(self._on_task_started)
        worker.signals.finished.connect(self._on_task_finished)
        worker.signals.error.connect(self._on_task_error)
        
        self.active_tasks[task_id] = worker
        self.thread_pool.start(worker)
        return task_id

    def cancel(self, task_id: str):
        """Cancel a running task by ID."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].is_cancelled = True
            # Some functions might need deeper cancellation logic
            
    def get_worker(self, task_id: str) -> Optional[TaskWorker]:
        return self.active_tasks.get(task_id)

    def _on_task_started(self, task_id: str):
        self.task_started.emit(task_id)

    def _on_task_finished(self, task_id: str):
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        self.task_finished.emit(task_id)

    def _on_task_error(self, task_id: str, error: Exception):
        self.task_failed.emit(task_id, error)
