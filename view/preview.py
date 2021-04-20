# import threading
import numpy as np
from moviepy.video.compositing.concatenate import concatenate_videoclips
from PySide2 import QtCore, QtGui, QtMultimedia
from sentence_mixing.video_creator.audio import concat_segments

from worker import Worker

PHONEM_CACHE = dict()

def get_loading_frames(fps):
    w, h = fps, int(9.0 * fps / 16)
    fs = np.arange(w)
    fs = np.stack([fs] * fps) - np.arange(fps).reshape((fps, 1))
    fs = np.stack([fs] * h, axis=-1)
    fs = fs.transpose(0, 2, 1)
    fs = np.stack([fs] * 3, axis=-1)
    fs = (fs > 0).astype(np.uint8) * 160
    return fs.copy(order="C")


def imdisplay(frame, pixmap):
    qimg = QtGui.QImage(
        frame,
        frame.shape[1],
        frame.shape[0],
        3 * frame.shape[1],
        QtGui.QImage.Format_RGB888,
    )
    pixmap.setPixmap(QtGui.QPixmap.fromImage(qimg))


def get_format(rate, wave):
    format = QtMultimedia.QAudioFormat()
    format.setChannelCount(wave.shape[1])
    format.setSampleRate(rate)
    format.setSampleSize(16)
    format.setCodec("audio/pcm")
    format.setSampleType(QtMultimedia.QAudioFormat.SignedInt)
    return format


class Previewer:
    def __init__(self, combo, fps=15, audio_phonems=None):
        self.combo = combo

        # audio
        if combo is not None or audio_phonems is not None:
            if audio_phonems is None:
                audio_phonems = combo.get_audio_phonems()
            rate, wave = concat_segments(audio_phonems)
            self.audio_format = get_format(rate, wave)
            self.data = QtCore.QByteArray(wave.tobytes(order="C"))
            self.audio_input = QtCore.QBuffer(self.data)
        else:
            self.audio_format = None
            self.data = None
            self.audio_input = None

        self.timer = None
        self.audio_output = None

        self.fps = fps

        self.t = 0
        self.period_ms = 1.0 / fps

        if audio_phonems is None:
            self.frames = get_loading_frames(fps)
        else:
            for p in audio_phonems:
                if p not in PHONEM_CACHE:
                    PHONEM_CACHE[p] = [p._get_original_video().get_frame(t)[::4, ::4].copy(order="C") for t in np.arange(p.start, p.end, self.period_ms)]

            self.frames = [f for p in audio_phonems for f in PHONEM_CACHE[p]]

    def __repr__(self):
        return f"<Preview for combo {self.combo}>"

    def run(self, pixmap, graphics_view, loop=False):
        self.loop = loop
        self.pixmap = pixmap
        self.graphics_view = graphics_view

        self.timer = QtCore.QTimer(self.graphics_view)
        self.timer.timeout.connect(self.update_frame)

        self.timer.start(self.period_ms * 1000)
        self.t = 0

        if self.audio_format is not None:
            self.audio_output = QtMultimedia.QAudioOutput(
                self.audio_format, self.graphics_view
            )
            self.audio_output.stateChanged.connect(self.audio_state_handler)
            # start audio streaming
            self.audio_input.open(QtCore.QIODevice.ReadOnly)
            self.audio_output.start(self.audio_input)

        self.display_frame()
        self.graphics_view.fitInView(self.pixmap, QtCore.Qt.KeepAspectRatio)

    def pause(self):
        if self.timer is not None:
            self.timer.stop()
        if self.audio_output is not None:
            self.audio_output.suspend()

    def unpause(self):
        if self.timer is not None:
            self.timer.start()
        if self.audio_output is not None:
            self.audio_output.resume()

    def stop(self):
        if self.timer is not None:
            self.timer.stop()
        if self.audio_output is not None:
            self.audio_output.stop()
        if self.audio_input is not None:
            self.audio_input.close()

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
        self.lock = QtCore.QReadWriteLock()

    def cancel(self):
        self.lock.lockForWrite()
        self.cancelled = True
        self.lock.unlock()

    def is_cancelled(self):
        self.lock.lockForRead()
        cancelled = self.cancelled
        self.lock.unlock()
        return cancelled

    def __repr__(self):
        return f"<Cancellation: {str(self.cancelled)}>"


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
            self.queue.release(1)
            self.delete_job(combo, job)
            return
        p = Previewer(combo)
        self.previous_lock.lockForWrite()
        self.previews[combo] = p
        self.previous_lock.unlock()
        self.queue.release(1)
        self.delete_job(combo, job)
        if job.is_cancelled():
            return
        return p

    def __compute_previews(self, combos):
        cancelled_segments = set()
        p = None
        for c in combos:
            if c.segment not in cancelled_segments:
                self.jobs_lock.lockForRead()
                self.jobs_lock.unlock()
                p = self.get_preview(c)
                if p is None:
                    cancelled_segments.add(c.segment)
        return p

    def compute_previews(self, thread_pool, combos, callback=None):
        w = Worker(self.__compute_previews, combos)
        if callback is not None:
            w.signals.result.connect(callback)
        thread_pool.start(w)

    def cancel(self, segment):
        self.jobs_lock.lockForWrite()
        for c in segment.combos:
            if c in self.jobs:
                for job in self.jobs[c]:
                    job.cancel()
                self.jobs.pop(c)
        self.jobs_lock.unlock()

    def cancel_all(self):
        self.jobs_lock.lockForWrite()
        for c in list(self.jobs.keys()):
            for job in self.jobs[c]:
                job.cancel()
            self.jobs.pop(c)
        self.jobs_lock.unlock()


previewManager = __PreviewManager()
blank_preview = Previewer(None)
