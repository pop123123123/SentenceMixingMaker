from copy import copy

import sentence_mixing.sentence_mixer as sm

from model import Project, Segment


def load_project(project_path):
    raise NotImplementedError()

    # TODO: get pickle project
    project = None
    return ProjectControler(project, project_path)


def new_project(name, seed, videos_url):
    videos = sm.get_videos(videos_url)
    project = Project(name, seed, videos)
    return ProjectControler(project)


class ProjectControler:
    def __init__(self, project, project_path=None):
        self.project = project
        self.project_path = project_path
        self.selected_segment = None

    def set_project_path(self, project_path):
        self.project_path = project_path

    def get_whole_preview(self):
        return self.project.generate_video()

    def export_video(self, video_path):
        raise NotImplementedError()

        # video = self.get_whole_preview()
        # TODO: write video in file video_path

    def save_project(self):
        raise NotImplementedError()

        if self.project_path is None:
            raise Exception("Please, set project path before saving")
        # TODO: pickle serialize project

    def add_segment(self, segment):
        """Append segment at the end of the project's segment list"""

        self.project.segments.append(segment)

    def create_segment(self, sentence):
        """Create a segment from a sentence and appends it at the end of project's segment list"""

        new_segment = Segment(self.project, sentence)
        self.add_segment(new_segment)

    def remove_segment(self, segment_index):
        """Remove a segment from project's segment list"""

        deleted_segment = self.project.segments.pop(segment_index)

        # If the deleted segment was the selected segment, de-selects it
        if self.selected_segment == deleted_segment:
            self.selected_segment = None

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

    def change_selected(self, new_selected_segment):
        """Change selected segment"""

        self.selected_segment = new_selected_segment

    def refresh_segment(self, segment):
        """Relaunches analysis for given segment"""

        segment.analyze()

    def get_segment_preview(self):
        """Returns selected segment's preview"""

        return self.selected_segment.generate_clip()
