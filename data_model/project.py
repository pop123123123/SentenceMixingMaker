import pickle
from copy import copy

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets

from data_model.segment import Segment


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
