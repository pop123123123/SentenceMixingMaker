import PySide2.Qt as Qt
import PySide2.QtCore as QtCore
import sentence_mixing.sentence_mixer as sm


class Project:
    def __init__(self, name, seed, videos):
        self.name = name
        self.seed = seed
        self.videos = videos
        self.segment_model = SegmentModel(self)

    def generate_video(self):
        clips = []
        for segment in self.segments:
            clips.append(segment.generate_clip())

        # TODO: assembler les clips
        final_clip = clips
        raise NotImplementedError()

        return final_clip


GET_PREFIX = "get_"
SET_PREFIX = "set_"
COLUMN_INDEX_TO_ATTRIBUTE = {0: "sentence", 1: "chosen_combo_index"}


class SegmentModel(QtCore.QAbstractTableModel):
    def __init__(self, project, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)
        self.project = project
        self.segments = []

    def _get_segment_from_index(self, index):
        return self.segments[index.row()]

    def _get_attribute_from_index(self, index):
        global GET_PREFIX
        global COLUMN_TO_ATTRIBUTE

        segment = self._get_segment_from_index(index)

        getter_name = GET_PREFIX + COLUMN_INDEX_TO_ATTRIBUTE[index.column()]
        getter = getattr(segment, getter_name, None)

        return getter()

    def _set_attribute_from_index(self, index, new_value):
        global SET_PREFIX
        global COLUMN_TO_ATTRIBUTE

        segment = self._get_segment_from_index(index)

        setter_name = SET_PREFIX + COLUMN_INDEX_TO_ATTRIBUTE[index.column()]
        setter = getattr(segment, setter_name, None)

        return setter(new_value)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self._get_attribute_from_index(index)
            # return self.segments[index.row()].sentence

        if role == QtCore.Qt.DecorationRole:
            return self.segments[index.row()].need_analysis

        if role == QtCore.Qt.EditRole:
            return self._get_attribute_from_index(index)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.EditRole:
            self._set_attribute_from_index(index, value)
            # self.segments[index] = value
            self.dataChanged.emit(index, index, (QtCore.Qt.EditRole,))
        else:
            return False
        return True

    def rowCount(self, index):
        return len(self.segments)

    def columnCount(self, index):
        global COLUMN_INDEX_TO_ATTRIBUTE
        return len(COLUMN_INDEX_TO_ATTRIBUTE)

    def insertRow(self, position):
        return self.insertRows(position, 1, None)

    def insertRows(self, position, count, parent):
        self.beginInsertRows(
            QtCore.QModelIndex(), position, position + count - 1
        )

        for row in range(0, count):
            self.segments.insert(position, Segment(self.project, ""))

        self.endInsertRows()
        return True

    def removeRow(self, position):
        return self.removeRows(position, 1, None)

    def removeRows(self, position, count, parent):
        self.beginRemoveRows(
            QtCore.QModelIndex(), position, position + count - 1
        )

        for row in range(0, count):
            del self.segments[position]

        self.endRemoveRows()
        return True


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
