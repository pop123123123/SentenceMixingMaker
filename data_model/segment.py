import sentence_mixing.sentence_mixer as sm
from sentence_mixing.model.exceptions import Interruption


def get_phonem_project_index(ph, project):
    return (
        ph.word.sentence.video.url,
        ph.word.sentence.get_index_in_video(),
        ph.word.get_index_in_sentence(),
        ph.get_index_in_word(),
    )


def get_phonem_from_project_index(index, project):
    """Fail if the video is not present in the projects videos"""
    v = next(v for v in project.videos if v.url == index[0])
    return v.subtitles[index[1]].words[index[2]].phonems[index[3]]


class Combo:
    def __init__(self, sm_combo, segment, id):
        self.id = id
        self.segment = segment
        if type(sm_combo) == list:
            self._phonems = sm_combo
        else:
            self._phonems = sm_combo.get_audio_phonems()

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.segment._sentence == other.segment._sentence
            and self.get_index() == other.get_index()
        )

    def __hash__(self):
        return hash((self.segment._sentence, self.get_index()))

    def __repr__(self):
        return str((self.segment._sentence, self.get_index()))

    def get_index(self):
        return self.id

    def get_audio_phonems(self):
        return self._phonems

    def to_JSON_serializable(self, project):
        return [get_phonem_project_index(ph, project) for ph in self._phonems]

    def from_JSON_serializable(obj, project, seg, id):
        return Combo(
            [get_phonem_from_project_index(index, project) for index in obj],
            seg,
            id,
        )


class Segment:
    def __init__(self, project, sentence, current_combo_index=0, combos=[]):
        self.project = project
        self._sentence = sentence
        self.set_combos(combos)

    def to_JSON_serializable(self):
        obj = self.__dict__.copy()
        obj["combos"] = [
            c.to_JSON_serializable(self.project) for c in self.combos
        ]
        obj.pop("project")
        return obj

    def from_JSON_serializable(obj, project):
        seg = Segment(project, obj["_sentence"], obj["_current_combo_index"])
        seg.set_combos(
            [
                Combo.from_JSON_serializable(c, project, seg, i)
                for i, c in enumerate(obj["combos"])
            ]
        )
        return seg

    def analyze(self, interrupt_callback):
        self.set_combos(
            [
                Combo(c, self, i)
                for i, c in enumerate(
                    sm.process_sm(
                        self._sentence,
                        self.project.videos,
                        interrupt_callback=interrupt_callback,
                    )
                )
            ]
        )

    def get_sentence(self):
        return self._sentence

    def is_analyzed(self):
        return not self.is_analyzing()

    def is_analyzing(self):
        return len(self.combos) == 0

    def need_analysis(self):
        return len(self.combos) == 0 and not self.is_empty()

    def is_empty(self):
        return self._sentence == ""

    def set_combos(self, combos):
        self.combos = combos

    def get_combo_index(self, combo):
        return self.combo.id
