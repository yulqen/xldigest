"""
A Qt version of the old bcompiler master spreadsheet. Re-written for the new
age...
"""
from collections import namedtuple

from PyQt5 import QtWidgets, QtCore

from xldigest.database.connection import Connection
from xldigest.database.base_queries import (
    project_ids_in_returns_with_series_item_of, datamap_items_in_return)
from xldigest.database.models import ReturnItem, Project, SeriesItem, DatamapItem


class ReturnSequence:
    """
    Sequence of return values given a project_id and series_item_id.
    """
    def __init__(self, project_id, dm_key_id):
        self.project_id = project_id
        self.dm_key_id = dm_key_id
        self.data = self._collect()

    def _collect(self):
        session = Connection.session()
        ReturnLine = namedtuple('ReturnLine', [
            'project_name',
            'project_id',
            'series_item_name',
            'series_item_id',
            'key_name',
            'key_id',
            'value'
        ])
        try:
            rows = session.query(
                Project.name,
                Project.id,
                SeriesItem.name,
                SeriesItem.id,
                DatamapItem.key,
                DatamapItem.id,
                ReturnItem.value
            ).join(ReturnItem, DatamapItem, SeriesItem).filter(
                Project.id == self.project_id,
                DatamapItem.id == self.dm_key_id
            )
            return [ReturnLine._make(row) for row in rows]
        except:
            print("Something went wrong")
            raise


def forumulate_data_for_model(
    series_item_id: int,
    project_ids: list,
    dm_keys: list,
) -> list:
    """
    Returns a list of (v1, v2, v3, ..) tuples where vn is the corresponding
    value in each return that matches all the project_ids for a particular
    series_item.
    """
    session = Connection.session()
    collect = []
    for i in list(project_ids):
        db_items = session.query(ReturnItem.value).filter(
            ReturnItem.series_item_id == series_item_id,
            ReturnItem.project_id == i).all()
        db_items_lst = [item[0] for item in db_items]
        collect.append(db_items_lst)
    # time to flip into tuples of related values ("A13", "Bound Materials",..)
    flipped = list(zip(dm_keys, *collect))
    return flipped


class MasterTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data_in, parent=None):
        super().__init__(parent)
        self.data_in = data_in
        self.header = None  # this needs to be generated dynamically Project titles
        self.p_names = list(self.data_in[0])

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.data_in)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.data_in[0])

    def data(self, index, role):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            value = self.data_in[row][col]
            return value

    def headerData(self, section, orientation, role):
        headers = self.p_names
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return headers[section]
            else:
                return section + 1

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled


class MasterWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.datamap_keys = datamap_items_in_return(1, 1)
        self.table_data = forumulate_data_for_model(1, [1, 2], self.datamap_keys)

        self.tv = QtWidgets.QTableView()
        self.proxyModel = QtCore.QSortFilterProxyModel()
        self.tableModel = MasterTableModel(self.table_data, self)
        self.tv.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.tableModel)
        self.tv.setSortingEnabled(True)
        self.tv.horizontalHeader().setStretchLastSection(True)
        self.sortCaseSensitivityCheckBox = QtWidgets.QCheckBox(
            "Case sensitive sorting")
        self.filterCaseSensitivityCheckBox = QtWidgets.QCheckBox(
            "Case sensitive filter")
        self.filterPatternLineEdit = QtWidgets.QLineEdit()
        self.filterPatternLabel = QtWidgets.QLabel("Filter pattern")
        self.filterPatternLabel.setBuddy(self.filterPatternLineEdit)
        self.filterSyntaxCombo = QtWidgets.QComboBox()
        self.filterSyntaxCombo.addItem("Regular Expression",
                                       QtCore.QRegExp.RegExp)
        self.filterSyntaxCombo.addItem("Wildcard", QtCore.QRegExp.Wildcard)
        self.filterSyntaxCombo.addItem("Fixed string",
                                       QtCore.QRegExp.FixedString)
        self.filterSyntaxLabel = QtWidgets.QLabel("Filter syntax:")
        self.filterSyntaxLabel.setBuddy(self.filterSyntaxCombo)
        self.filterColumnCombo = QtWidgets.QComboBox()
        self.filterColumnCombo.addItem("Project 1")
        self.filterColumnLabel = QtWidgets.QLabel("Filter column:")
        self.filterColumnLabel.setBuddy(self.filterColumnCombo)

        self.filterPatternLineEdit.textChanged.connect(self.filterRegExChanged)
        self.filterSyntaxCombo.currentIndexChanged.connect(
            self.filterRegExChanged)
        self.filterColumnCombo.currentIndexChanged.connect(
            self.filterColumnChanged)
        self.filterCaseSensitivityCheckBox.toggled.connect(self.sortChanged)

        proxyGroupBox = QtWidgets.QGroupBox("Master Data")

        proxyLayout = QtWidgets.QGridLayout()
        proxyLayout.addWidget(self.tv, 0, 0, 1, 3)
        proxyLayout.addWidget(self.filterPatternLabel, 1, 0)
        proxyLayout.addWidget(self.filterPatternLineEdit, 1, 1, 1, 2)
        proxyLayout.addWidget(self.filterSyntaxLabel, 2, 0)
        proxyLayout.addWidget(self.filterSyntaxCombo, 2, 1, 1, 2)
        proxyLayout.addWidget(self.filterColumnLabel, 3, 0)
        proxyLayout.addWidget(self.filterColumnCombo, 3, 1, 1, 2)
        proxyLayout.addWidget(self.filterCaseSensitivityCheckBox, 4, 0, 1, 2)
        proxyLayout.addWidget(self.sortCaseSensitivityCheckBox, 4, 2)
        proxyGroupBox.setLayout(proxyLayout)

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addWidget(proxyGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("xldigest Master View")

        self.tv.sortByColumn(1, QtCore.Qt.AscendingOrder)
        self.filterColumnCombo.setCurrentIndex(1)

        self.filterPatternLineEdit.setText("")
        self.filterCaseSensitivityCheckBox.setChecked(False)
        self.sortCaseSensitivityCheckBox.setChecked(False)

    def filterRegExChanged(self):
        syntax = QtCore.QRegExp.PatternSyntax(
            self.filterSyntaxCombo.itemData(
                self.filterSyntaxCombo.currentIndex()))
        caseSensitivity = self.filterCaseSensitivityCheckBox.isChecked()
        regex = QtCore.QRegExp(self.filterPatternLineEdit.text(),
                               caseSensitivity, syntax)
        self.proxyModel.setFilterRegExp(regex)

    def filterColumnChanged(self):
        self.proxyModel.setFilterKeyColumn(
            self.filterColumnCombo.currentIndex())

    def sortChanged(self):
        self.proxyModel.setSortCaseSensitivity(
            self.sortCaseSensitivityCheckBox.isChecked())
