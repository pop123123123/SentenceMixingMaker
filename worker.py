from PySide2 import QtCore
from sentence_mixing import sentence_mixer


class WorkerSignals(QtCore.QObject):
    finished = QtCore.Signal()
    error = QtCore.Signal(str)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(int)


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.result.emit(
                result
            )  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
