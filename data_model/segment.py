from enum import Enum

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
    def __init__(self, sm_combo, segment):
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

    def get_index(self):
        return self.segment.get_combo_index(self)

    def get_audio_phonems(self):
        return self._phonems

    def to_JSON_serializable(self, project):
        return [get_phonem_project_index(ph, project) for ph in self._phonems]

    def from_JSON_serializable(obj, project, seg):
        return Combo(
            [get_phonem_from_project_index(index, project) for index in obj],
            seg,
        )


class AnalysisState(Enum):
    ANALYZED = 0
    ANALYZING = 1
    NEED_ANALYSIS = 2


class Segment:
    def __init__(self, project, sentence, current_combo_index=0, combos=[]):
        self.project = project
        self._sentence = sentence
        self.set_combos(combos)

        self.analysis_state = AnalysisState.NEED_ANALYSIS

    def to_JSON_serializable(self):
        obj = self.__dict__.copy()
        obj["analysis_state"] = self.analysis_state.value
        obj["combos"] = [
            c.to_JSON_serializable(self.project) for c in self.combos
        ]
        obj.pop("project")
        return obj

    def from_JSON_serializable(obj, project):
        seg = Segment(project, obj["_sentence"], obj["_current_combo_index"])
        seg.analysis_state = AnalysisState(obj["analysis_state"])
        seg.set_combos(
            [
                Combo.from_JSON_serializable(c, project, seg)
                for c in obj["combos"]
            ]
        )
        return seg

    def analyze(self, interrupt_callback):
        self._set_analysis_state(AnalysisState.ANALYZING)
        try:
            self.set_combos(
                [
                    Combo(c, self)
                    for c in sm.process_sm(
                        self._sentence,
                        self.project.videos,
                        seed=self.project.seed,
                        interrupt_callback=interrupt_callback,
                    )
                ]
            )
            self._set_analysis_state(AnalysisState.ANALYZED)
        except Interruption as i:
            self._set_analysis_state(AnalysisState.NEED_ANALYSIS)
            raise i

    def get_sentence(self):
        return self._sentence

    def get_analysis_state(self):
        return self.analysis_state

    def _set_analysis_state(self, state):
        self.analysis_state = state

    def set_combos(self, combos):
        self.combos = combos
        self.combo_index = {id(c): i for i, c in enumerate(combos)}

    def get_combo_index(self, combo):
        return self.combo_index[id(combo)]
