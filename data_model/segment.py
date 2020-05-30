import sentence_mixing.sentence_mixer as sm


class Segment:
    def __init__(self, project, sentence, current_combo_index=None, combos=[]):
        self.project = project
        self._sentence = sentence
        self.combos = combos

        self.need_analysis = True
        self._current_combo_index = current_combo_index

    def analyze(self, interrupt_callback):
        self.combos = sm.process_sm(
            self._sentence,
            self.project.videos,
            seed=self.project.seed,
            interrupt_callback=interrupt_callback,
        )
        self.need_analysis = False

    def get_chosen_combo(self):
        return self.combos[self._current_combo_index]

    def generate_clip(self):
        raise NotImplementedError()

    def get_sentence(self):
        return self._sentence

    def get_chosen_combo_index(self):
        return self._current_combo_index

    def set_sentence(self, new_sentence):
        self._sentence = new_sentence
        self.need_analysis = True

    def set_chosen_combo_index(self, chosen_combo_index):
        self._current_combo_index = chosen_combo_index
        self.need_analysis = True

    def set_combos(self, combos):
        self.combos = combos
