from PyQt5 import QtWidgets

from xldigest.widgets.base_import_wizard_ui import Ui_baseWizard
from xldigest.widgets.dialogs import AddPortfolioDialog, AddProjectDialog


class BaseImportWizard(QtWidgets.QWizard, Ui_baseWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.projects = []
        self.portfolio = None
        self.create_portfolio_button.clicked.connect(
            self._create_portfolio_diag)
        self.add_project_button.clicked.connect(self._add_project_diag)
        self.portfolio_added_label.setEnabled(False)
        self.added_projects_table.setColumnCount(1)
        self.added_projects_table.setHorizontalHeaderItem(
            0, QtWidgets.QTableWidgetItem("Projects Added"))
        self.added_projects_table.horizontalHeader().setStretchLastSection(
            True)

    def _create_portfolio_diag(self):
        diag = AddPortfolioDialog()
        if diag.exec_():
            self.portfolio = diag.name_lineEdit.text()
            self.portfolio_added_label.setEnabled(True)
            self.portfolio_added_label.setText(self.portfolio)
            print(diag.name_lineEdit.text())

    def _add_project_diag(self):
        diag = AddProjectDialog()
        if diag.exec_():
            new_project_name = diag.name_lineEdit.text()
            self.projects.append(new_project_name)
            rows = self.added_projects_table.rowCount()
            self.added_projects_table.insertRow(rows)
            p_add = QtWidgets.QTableWidgetItem(new_project_name)
            self.added_projects_table.setItem(rows, 0, p_add)
