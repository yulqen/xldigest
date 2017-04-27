from PyQt5 import QtWidgets


class AddPortfolioDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        name_label = QtWidgets.QLabel("Portfolio Name")
        self.name_lineEdit = QtWidgets.QLineEdit("Portfolio Name")
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                               QtWidgets.QDialogButtonBox.Cancel)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self.name_lineEdit, 0, 1)
        grid.addWidget(buttonBox, 2, 0, 1, 2)
        self.setLayout(grid)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
