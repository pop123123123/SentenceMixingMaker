import pickle
from copy import copy

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from data_model.segment import Segment
from model_ui.segment_model import ChosenCombo

FORMAT_VERSION = 2
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
        if version > FORMAT_VERSION:
            raise EnvironmentError("File too new for this version.")
        in_.setVersion(QtCore.QDataStream.Qt_5_14)

        # Read the data
        data_size = in_.readInt32()
        data = in_.readRawData(data_size)

        file.close()
        return Project.from_JSON_serializable(pickle.loads(bytes(data)))


class Project:
    def __init__(self, path, seed, urls):
        self.set_path(path)
        self.seed = seed
        self.urls = urls
        self.videos = None
        self.segments = {}
        self.ordered_segments = []
        self.ready = False

    def from_JSON_serializable(schema):
        p = Project(schema["path"], schema["seed"], schema["urls"])
        p.ordered_segments = [ChosenCombo.from_JSON_serializable(p, c) for c in schema["ordered_segments"]]
        return p

    def to_JSON_serializable(self):
        schema = {
            "path": self.path,
            "seed": self.seed,
            "urls": self.urls,
            "ordered_segments": [c.to_JSON_serializable() for c in self.ordered_segments]
        }
        return schema

    def set_videos(self, videos):
        assert not self.are_videos_ready()
        self.videos = videos

    def init_project(self, videos):
        self.set_videos(videos)

        for chosenCombo in self.ordered_segments:
            if chosenCombo.sentence not in self.segments:
                self.create_segment(chosenCombo.sentence)
        self.ready = True

    def set_path(self, path):
        if path is not None and not path.endswith(".p00p"):
            path += ".p00p"
        self.path = path

    def are_videos_ready(self):
        return self.videos is not None and self.ready

    def save(self):
        """Saves the project at project path as p00p file"""
        file = QtCore.QFile(self.path)
        if not file.open(QtCore.QIODevice.WriteOnly):
            raise EnvironmentError(file.errorString())
        else:
            data = QtCore.QByteArray(pickle.dumps(self.to_JSON_serializable(), protocol=4))
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

    def get_segment(self, sentence):
        """Returns segment of specified sentence"""
        if sentence not in self.segments:
            self.create_segment(sentence)

        return self.segments[sentence]

    def change_current_combo_index(self, new_combo_index):
        """Change index to current selected combo"""

        self.selected_segment.set_chosen_combo_index(new_combo_index)

    def create_segment(self, sentence):
        """Create a segment from a sentence and stores it"""

        self.segments[sentence] = Segment(self, sentence)

    def _remove_segment(self, sentence):
        """Remove a segment from project's segment dict"""

        self.segments.pop(sentence)
