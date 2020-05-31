# import threading
import numpy as np
from moviepy.editor import concatenate_videoclips
from PySide2 import QtCore, QtGui, QtMultimedia
from sentence_mixing.video_creator.audio import concat_segments

from worker import Worker


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
    def __init__(self, combo, fps=15):
        self.clip = concatenate_videoclips(
            [phonem.get_video_clip() for phonem in combo.get_audio_phonems()]
        )

        # audio
        rate, wave = concat_segments(combo.get_audio_phonems())
        self.audio_format = get_format(rate, wave)
        self.data = QtCore.QByteArray(wave.tobytes(order="C"))
        self.audio_input = QtCore.QBuffer(self.data)

        self.timer = None
        self.audio_output = None

        self.fps = fps

        self.t = 0
        self.period_ms = 1.0 / fps

        self.frames = [
            self.clip.get_frame(t)[::4, ::4].copy(order="C")
            for t in np.arange(0, self.clip.duration, self.period_ms)
        ]

    def run(self, pixmap, graphics_view, loop=False):
        self.loop = loop
        self.pixmap = pixmap
        self.graphics_view = graphics_view

        self.audio_output = QtMultimedia.QAudioOutput(
            self.audio_format, self.graphics_view
        )
        self.audio_output.stateChanged.connect(self.audio_state_handler)
        self.timer = QtCore.QTimer(self.graphics_view)
        self.timer.timeout.connect(self.update_frame)

        self.timer.start(self.period_ms * 1000)

        # start audio streaming
        self.audio_input.open(QtCore.QIODevice.ReadOnly)
        self.audio_output.start(self.audio_input)

        self.display_frame()
        self.graphics_view.fitInView(self.pixmap, QtCore.Qt.KeepAspectRatio)

    def stop(self):
        if self.timer is not None:
            self.timer.stop()
        if self.audio_output is not None:
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


class Cancellation:
    def __init__(self):
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def is_cancelled(self):
        return self.cancelled


class __PreviewManager:
    def __init__(self):
        self.previews = dict()
        self.previous_lock = QtCore.QReadWriteLock()

        self.jobs = dict()
        self.jobs_lock = QtCore.QReadWriteLock()

        self.first = None
        self.first_lock = QtCore.QReadWriteLock()

        self.queue = QtCore.QSemaphore(1)

    def get_preview_if_in_previews(self, combo):
        p = None
        self.jobs_lock.lockForRead()
        if combo in self.previews:
            p = self.previews[combo]
        self.jobs_lock.unlock()
        return p

    def get_first(self):
        self.first_lock.lockForRead()
        first = self.first
        self.first_lock.unlock()
        return first

    def set_first(self, job):
        self.first_lock.lockForWrite()
        self.first = job
        self.first_lock.unlock()

    def is_in_previews(self, combo):
        self.jobs_lock.lockForRead()
        is_in_previews = combo in self.previews
        self.jobs_lock.unlock()
        return is_in_previews

    def get_preview(self, combo):
        p = self.get_preview_if_in_previews(combo)
        if p is not None:
            return p
        return self.__create_preview(combo)

    def get_cancellation(self, combo):
        cancellation = Cancellation()
        self.jobs_lock.lockForWrite()
        if combo not in self.jobs:
            self.jobs[combo] = set()
        self.jobs[combo].add(cancellation)
        self.jobs_lock.unlock()
        return cancellation

    def delete_job(self, combo, job):
        self.jobs_lock.lockForWrite()
        if combo in self.jobs:
            if job in self.jobs[combo]:
                self.jobs[combo].remove(job)
        self.jobs_lock.unlock()

    def __create_preview(self, combo):
        job = self.get_cancellation(combo)
        enqueue = True
        while enqueue:
            self.queue.acquire(1)
            p = self.get_preview_if_in_previews(combo)
            if p is not None:
                self.queue.release(1)
                self.delete_job(combo, job)
                return p
            first = self.get_first()
            enqueue = first != job
            if self.first is None:
                self.set_first(job)
            if enqueue:
                self.queue.release(1)
        self.set_first(None)
        if job.is_cancelled():
            return
        p = Previewer(combo)
        if job.is_cancelled():
            return p
        self.previous_lock.lockForWrite()
        self.previews[combo] = p
        self.previous_lock.unlock()
        self.queue.release(1)
        self.delete_job(combo, job)
        return p

    def __compute_previews(self, combos):
        for c in combos:
            self.get_preview(c)

    def compute_previews(self, thread_pool, combos):
        w = Worker(self.__compute_previews, combos)
        thread_pool.start(w)

    def cancel(self, segment):
        self.jobs_lock.lockForWrite()
        for c in segment.combos:
            if c in self.jobs:
                for job in self.jobs[c]:
                    job.cancel()
                self.jobs.pop(c)
        self.jobs_lock.unlock()


previewManager = __PreviewManager()
