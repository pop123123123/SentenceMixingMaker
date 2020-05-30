# import threading
import numpy as np
from moviepy.editor import concatenate_videoclips
from PySide2 import QtCore, QtGui, QtMultimedia
from sentence_mixing.video_creator.audio import concat_segments


def imdisplay(frame, pixmap):
    """Splashes the given image array on the given pygame screen """
    qimg = QtGui.QImage(
        frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_BGR888
    )
    pixmap.setPixmap(QtGui.QPixmap.fromImage(qimg.rgbSwapped()))


def get_format(rate, wave):
    format = QtMultimedia.QAudioFormat()
    format.setChannelCount(wave.shape[1])
    format.setSampleRate(rate)
    format.setSampleSize(16)
    format.setCodec("audio/pcm")
    format.setSampleType(QtMultimedia.QAudioFormat.SignedInt)
    return format


class Previewer:
    def __init__(self, combo, pixmap, graphics_view, loop=False, fps=15):
        self.clip = concatenate_videoclips(
            [phonem.get_video_clip() for phonem in combo.get_audio_phonems()]
        )

        # audio
        rate, wave = concat_segments(combo.get_audio_phonems())
        self.audio_format = get_format(rate, wave)
        self.data = QtCore.QByteArray(wave.tobytes(order="C"))
        self.audio_input = QtCore.QBuffer(self.data)
        self.audio_output = QtMultimedia.QAudioOutput(
            self.audio_format, graphics_view
        )
        self.audio_output.stateChanged.connect(self.audio_state_handler)

        self.pixmap = pixmap
        self.graphics_view = graphics_view
        self.loop = loop

        self.fps = fps

        self.timer = QtCore.QTimer(self.graphics_view)
        self.timer.timeout.connect(self.update_frame)

        self.t = 0
        self.period_ms = 1.0 / fps

        self.frames = [
            self.clip.get_frame(t)[::4, ::4].copy(order="C")
            for t in np.arange(0, self.clip.duration, self.period_ms)
        ]

    def run(self):
        self.timer.start(self.period_ms * 1000)

        # start audio streaming
        self.audio_input.open(QtCore.QIODevice.ReadOnly)
        self.audio_output.start(self.audio_input)

        self.display_frame()
        self.graphics_view.fitInView(self.pixmap, QtCore.Qt.KeepAspectRatio)

    def stop(self):
        self.timer.stop()
        self.audio_output.stop()
        self.audio_input.close()

    def prepare_next_frame(self):
        frame = self.clip.get_frame(self.t)
        self.frame = frame[::4, ::4].copy(order="C")

    def display_frame(self):
        imdisplay(self.frames[self.t], self.pixmap)

    def audio_state_handler(self, state):
        if state == QtMultimedia.QAudio.IdleState and self.loop:
            self.audio_input.close()
            self.audio_input = QtCore.QBuffer(self.data)
            self.audio_input.open(QtCore.QIODevice.ReadWrite)
            self.audio_output.start(self.audio_input)

    def update_frame(self):
        self.t += 1
        if self.t >= len(self.frames):
            if self.loop:
                self.t = 0
                self.display_frame()
            else:
                self.stop()
        else:
            self.display_frame()
