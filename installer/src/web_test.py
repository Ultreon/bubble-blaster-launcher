#  Copyright (c) 2022.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import sys

import click
from PySide2.QtCore import QUrl, QEvent
from PySide2.QtGui import Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QSizePolicy, QWidget, QToolBar, QPushButton, \
    QToolButton, QTextEdit, QPlainTextEdit, QLineEdit


class Main(QWidget):
    def __init__(self, url="https://www.google.com/"):
        super().__init__()

        view = self.view = QWebEngineView(self)
        view.setContentsMargins(0, 0, 0, 0)

        toolBar: QToolBar = QToolBar(self)
        backButton: QToolButton = QToolButton(self)
        backButton.setText("< Back")
        backButton.clicked.connect(view.back)

        nextButton: QToolButton = QToolButton(self)
        nextButton.setText("Next >")
        nextButton.clicked.connect(view.forward)

        self.urlTextEdit: QLineEdit = QLineEdit(url, self)
        self.urlTextEdit.installEventFilter(self)
        self.urlTextEdit.installEventFilter(self)

        toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolBar.addWidget(backButton)
        toolBar.addWidget(nextButton)
        toolBar.addWidget(self.urlTextEdit)

        layout = QVBoxLayout()
        layout.addWidget(toolBar)
        layout.addWidget(view, QVBoxLayout.SizeConstraint.SetMaximumSize)
        layout.setContentsMargins(0, 0, 0, 0)

        view.load(QUrl(url))

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.urlTextEdit:
            if event.key() == Qt.Key_Return and self.urlTextEdit.hasFocus():
                self.view.load(QUrl(self.urlTextEdit.text()))


@click.command()
@click.option('--url', default="https://www.google.com", help='Default url.')
def main(url: str):
    app = QApplication()

    main_: Main = Main(url)
    main_.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
