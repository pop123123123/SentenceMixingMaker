import sentence_mixing.model.exceptions as sm_exceptions
from proglog import ProgressBarLogger
from PySide2 import QtCore, QtWidgets


class VideoAssemblerSignals(QtCore.QObject):
    """Theses signals are related to video assembly"""

    update_message = QtCore.Signal(str)
    update_total = QtCore.Signal(int)
    update_index = QtCore.Signal(int)


class VideoAssemblerLogger(ProgressBarLogger):
    """
    This class is used to log the progression (using prolog library)
    It is related to a Qt ProgressBar and communicates using signals
    """

    def __init__(self, progress_dialog):
        super(VideoAssemblerLogger, self).__init__()
        self.signals = progress_dialog.signals
        self.interruption_check_fn = None

    def set_interruption_callback(self, callback):
        """
        Sets interruption checking function
        This function should return a boolean value
        It will be tested at every step
        """

        self.interruption_check_fn = callback

    def _check_for_interruption(self):
        """
        Interrupts the program if interruption_check_fn is defined and returns True
        raises:
        Interruption - tells the caller thread to stop its execution
        """

        if (
            self.interruption_check_fn is not None
            and self.interruption_check_fn()
        ):
            raise sm_exceptions.Interruption(self.interruption_check_fn)

    def callback(self, **changes):
        """Provides progression type related message"""

        self._check_for_interruption()

        if "message" in changes.keys():
            self.signals.update_message.emit(changes["message"])

    def bars_callback(self, bar, attr, value, old_value=None):
        """Called everytime a new step is reached"""

        self._check_for_interruption()

        if attr == "total":
            self.signals.update_total.emit(value)
        elif attr == "index":
            self.signals.update_index.emit(value)


class VideoAssemblerProgressDialog(QtWidgets.QProgressDialog):
    """This progress bar is specific to VideoAssembly features"""

    def __init__(self, parent):
        super(VideoAssemblerProgressDialog, self).__init__(
            "Assembling sequences...", "Abort", 0, 1, parent
        )

        self.setAutoClose(False)
        self.setAutoReset(False)

        self.signals = VideoAssemblerSignals()

        self.signals.update_message.connect(self.setLabelText)
        self.signals.update_total.connect(self.setMaximum)
        self.signals.update_index.connect(self.setValue)
