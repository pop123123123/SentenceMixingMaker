import pickle
from copy import copy

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from data_model.segment import Segment

FORMAT_VERSION = 1
MAGIC_NUMBER = 0x70303070


def load_project(project_path):
    """Loads project from p00p file"""
    file = QtCore.QFile(project_path)
    if not file.open(QtCore.QIODevice.ReadOnly):
        raise EnvironmentError(file.errorString())
    else:
        in_ = QtCore.QDataStream(file)

        # Read and check the header
        magic = in_.readInt32()
        if magic != MAGIC_NUMBER:
            raise EnvironmentError("Bad file format")

        # Read the version
        version = in_.readInt32()
        if version > 1:
            raise EnvironmentError("File too new for this version.")
        in_.setVersion(QtCore.QDataStream.Qt_5_14)

        # Read the data
        data_size = in_.readInt32()
        data = in_.readRawData(data_size)

        file.close()
        return pickle.loads(bytes(data))


class Project:
    def __init__(self, path, seed, urls):
        self.set_path(path)
        self.seed = seed
        self.urls = urls
        self.videos = None
        self.segments = []

    def set_videos(self, videos):
        assert not self.are_videos_ready()
        self.videos = videos

    def set_path(self, path):
        if not path.endswith(".p00p"):
            path += ".p00p"
        self.path = path

    def generate_video(self):
        clips = []
        for segment in self.segments:
            clips.append(segment.generate_clip())

        # TODO: assembler les clips
        final_clip = clips
        raise NotImplementedError()

        return final_clip

    def are_videos_ready(self):
        return self.videos is not None

    def save(self):
        """Saves the project at project path as p00p file"""
        file = QtCore.QFile(self.path)
        if not file.open(QtCore.QIODevice.WriteOnly):
            raise EnvironmentError(file.errorString())
        else:
            data = QtCore.QByteArray(pickle.dumps(self, protocol=4))
            out = QtCore.QDataStream(file)
            out.writeInt32(MAGIC_NUMBER)
            out.writeInt32(FORMAT_VERSION)
            out.setVersion(QtCore.QDataStream.Qt_5_14)
            out << data
            file.close()

    def duplicate_segment(self, segment):
        """Performs a shallow copy of the given segment and appends it to the segment list"""

        segment_copy = copy(segment)
        self.add_segment(segment_copy)

    def get_segment(self, index):
        """Returns segment at specific index"""

        return self.project.segments[index]

    def change_current_combo_index(self, new_combo_index):
        """Change index to current selected combo"""

        self.selected_segment.set_chosen_combo_index(new_combo_index)

    def export_video(self, video_path):
        raise NotImplementedError()

        # video = self.get_whole_preview()
        # TODO: write video in file video_path

    def add_segment(self, segment):
        """Append segment at the end of the project's segment list"""

        self.segments.append(segment)

    def create_segment(self, sentence):
        """Create a segment from a sentence and appends it at the end of project's segment list"""

        self.add_segment(Segment(self, sentence))

    def remove_segment(self, segment_index):
        """Remove a segment from project's segment list"""

        self.segments.pop(segment_index)
