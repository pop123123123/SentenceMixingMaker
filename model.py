import sentence_mixing.sentence_mixer as sm


class Project:
    def __init__(self, name, seed, videos):
        self.name = name
        self.seed = seed
        self.videos = videos
        self.segments = []

    def generate_video(self):
        clips = []
        for segment in self.segments:
            clips.append(segment.generate_clip())

        # TODO: assembler les clips
        final_clip = clips
        raise NotImplementedError()

        return final_clip


class Segment:
    def __init__(self, project, sentence, combos=[]):
        self.project = project
        self._sentence = sentence
        self.combos = combos

        self.need_analysis = True
        self._current_combo_index = None

    def analyze(self):
        self.combos = sm.process_sm(
            self._sentence, self.project.videos, seed=self.project.seed
        )
        self.need_analysis = False

    def get_chosen_combo(self):
        return self.combos[self._current_combo_index]

    def generate_clip(self):
        raise NotImplementedError()

    def set_sentence(self, new_sentence):
        self._sentence = new_sentence
        self.need_analysis = True

    def set_chosen_combo_index(self, chosen_combo_index):
        self._current_combo_index = chosen_combo_index
        self.need_analysis = True
