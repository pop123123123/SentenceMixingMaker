from enum import Enum

from PySide2 import QtCore
from sentence_mixing import sentence_mixer
from sentence_mixing.model.exceptions import Interruption


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
        self.interruption_flag = False

    @QtCore.Slot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)

            if self.should_be_interrupted():
                raise Interruption(self.should_be_interrupted)
        except Interruption:
            self.signals.error.emit("Thread interrupted")
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.result.emit(
                result
            )  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

    def should_be_interrupted(self):
        return self.interruption_flag

    def interrupt(self):
        """Only works if self.fn contains an interruption system"""
        self.interruption_flag = True


class AnalysisState(Enum):
    ANALYZED = 0
    ANALYZING = 1
    NEED_ANALYSIS = 2


class AnalyzeWorker(Worker, QtCore.QObject):
    stateChanged = QtCore.Signal(str)

    def __init__(self, segment):
        QtCore.QObject.__init__(self)
        super(AnalyzeWorker, self).__init__(
            self.analyze_segment, self.should_be_interrupted
        )
        self.segment = segment

    def analyze_segment(self, interrupt_callback):
        try:
            self.segment.analyze(interrupt_callback)
            self.stateChanged.emit(self.segment.get_sentence())
        except Interruption as i:
            #            self.stateChanged.emit(self.segment.get_sentence(), AnalysisState.NEED_ANALYSIS)
            raise i
