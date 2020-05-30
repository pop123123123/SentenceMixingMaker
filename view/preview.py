# import threading
from moviepy.editor import concatenate_videoclips
from PySide2 import QtCore, QtGui


def imdisplay(frame, pixmap):
    """Splashes the given image array on the given pygame screen """
    frame = frame[::4, ::4].copy(order="C")

    qimg = QtGui.QImage(
        frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_BGR888
    )
    pixmap.setPixmap(QtGui.QPixmap.fromImage(qimg.rgbSwapped()))


class Previewer:
    def __init__(self, combo, pixmap, graphics_view, fps=24):
        self.clip = concatenate_videoclips(
            [phonem.get_video_clip() for phonem in combo.get_audio_phonems()]
        )
        self.pixmap = pixmap
        self.graphics_view = graphics_view

        self.fps = fps

        self.timer = QtCore.QTimer(self.graphics_view)
        self.timer.timeout.connect(self.update_frame)

        self.t = 0
        self.period_ms = 1.0 / fps

    def run(self):
        self.timer.start(self.period_ms * 1000)
        imdisplay(self.clip.get_frame(0), self.pixmap)
        self.graphics_view.fitInView(self.pixmap, QtCore.Qt.KeepAspectRatio)

    def update_frame(self):
        self.t += self.period_ms
        if self.clip.duration <= self.t:
            self.timer.stop()
        else:
            imdisplay(self.clip.get_frame(self.t), self.pixmap)
