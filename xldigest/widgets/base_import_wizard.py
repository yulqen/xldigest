from PyQt5 import QtWidgets

from xldigest.widgets.base_import_wizard_ui import Ui_baseWizard


class BaseImportWizard(QtWidgets.QWizard, Ui_baseWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
