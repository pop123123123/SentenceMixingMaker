import sentence_mixing.sentence_mixer as sm

from model import Project, Segment


def load_project(project_path):
    raise NotImplementedError()

    # TODO: get pickle project
    project = None
    return ProjectControler(project, project_path), SegmentControler(project)


def new_project(name, seed, videos_url):
    videos = sm.get_videos(videos_url)
    project = Project(name, seed, videos)
    return ProjectControler(project), SegmentControler(project)


class ProjectControler:
    def __init__(self, project, project_path=None):
        self.project = project
        self.project_path = project_path

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


class SegmentControler:
    def __init__(self, project):
        self.project = project
        self.selected_segment = None

    def create_segment(self, sentence):
        new_segment = Segment(self.project, sentence)
        self.project.segments.append(new_segment)

    def remove_segment(self, sentence):
        if self.selected_segment == sentence:
            self.selected_segment = None

        self.project.segments.remove(sentence)

    def duplicate_segment(self, segment):
        # TODO: le faire proprement (pas de duplication des phonemes)
        raise NotImplementedError()

    def get_segment(self, index):
        return self.project.segments[index]

    def change_current_combo_index(self, new_combo_index):
        self.selected_segment.set_chosen_combo_index(new_combo_index)

    def change_selected(self, new_selected_segment):
        self.selected_segment = new_selected_segment

    def refresh_segment(self):
        self.selected_segment.analyze()

    def get_segment_preview(self):
        return self.selected_segment.generate_clip()
