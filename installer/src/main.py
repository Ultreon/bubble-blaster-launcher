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

import os
import platform
import subprocess
import sys
from enum import Enum
from threading import Thread
from typing import Optional

from PySide2.QtCore import QDir
from PySide2.QtGui import QPixmap, QIcon, QCloseEvent
from PySide2.QtWidgets import QApplication, QWizard, QWizardPage, QLabel, QVBoxLayout, QWidget, \
    QComboBox, QHBoxLayout, QPushButton, QFileDialog, QFileSystemModel, QProgressBar, QRadioButton, QTextBrowser, \
    QCheckBox, QMessageBox
from PySide2.QtWinExtras import QtWin
from qt_thread_updater import get_updater

WIN32_APP_ID = u"UltreonTeam.BubbleBlaster.Installer.1.0.0.0"

# noinspection PyBroadException
try:
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WIN32_APP_ID)
except Exception:
    pass

DATA_FOLDER = None
WIZARD_STYLE: QWizard.WizardStyle

if platform.system().lower() == "windows":
    DATA_FOLDER = os.path.join(os.getenv("appdata"), "BubbleBlasterLauncher/")
    WIZARD_STYLE = QWizard.WizardStyle.AeroStyle
elif platform.system().lower() == "linux":
    if os.getlogin() == "root":
        DATA_FOLDER = f"/root/.BubbleBlasterLauncher/"
    else:
        DATA_FOLDER = f"/home/{os.getlogin()}/.BubbleBlasterLauncher/"
    WIZARD_STYLE = QWizard.WizardStyle.ModernStyle
elif (platform.system().lower() == "macos") or (platform.system().lower() == "osx") or (
        platform.system().lower() == "darwin") or (platform.system().lower() == "macosx"):
    if os.getlogin() == "root":
        DATA_FOLDER = f"/root/.BubbleBlasterLauncher/"
    else:
        DATA_FOLDER = f"/Users/{os.getlogin()}/.BubbleBlasterLauncher/"
    WIZARD_STYLE = QWizard.WizardStyle.MacStyle
else:
    print("This program is currently only for Windows, MacOS and Linux", file=sys.stderr)
    exit()


class InstallationType(Enum):
    ONLY_FOR_ME: int = 0
    EVERYBODY: int = 1


INSTALLATION_DIR = DATA_FOLDER.replace("/", os.path.sep)
PRODUCT_NAME = "Bubble Blaster Launcher"
INSTALLATION_TYPE = InstallationType.ONLY_FOR_ME
DOWNLOAD_URL: str = "https://ultreon.github.io/bubble-blaster-launcher/data/downloads/Updater.exe"

VIEW_README = False
LAUNCH_APP = True

TEMP_DIR = "%s/Temporary" % os.getcwd().replace("\\", "/")

WIZARD_STYLE_OVERRIDE: Optional[QWizard.WizardStyle] = None  # QWizard.WizardStyle.ModernStyle

WIN32_START_MENU = r"C:\Users\quint\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Ultreon Team"
WIN32_START_MENU_ITEM = rf"{WIN32_START_MENU}\Bubble Blaster Launcher"


# noinspection PyUnboundLocalVariable,PyArgumentList
def file_size(size: int):
    """
    Get display text of a file size.

    @author: Qboi123
    @param size: the file size in bytes.
    @return: string representation of the file size.
    @version: 1.1.0
    """

    if size < 1024:
        return f"{round(size)} , 1Bytes"
    elif size < (1024 * 1024):
        return f"{round(size / 1024, 1)} kB"
    elif size < (1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024, 1)} MB"
    elif size < (1024 * 1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024 / 1024, 1)} GB"
    elif size < (1024 * 1024 * 1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024 / 1024 / 1024, 1)} TB"
    elif size < (1024 * 1024 * 1024 * 1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024 / 1024 / 1024 / 1024, 1)} PB"
    elif size < (1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024 / 1024 / 1024 / 1024 / 1024, 1)} EB"
    elif size < (1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024 / 1024 / 1024 / 1024 / 1024 / 1024, 1)} ZB"
    elif size < (1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024):
        return f"{round(size / 1024 / 1024 / 1024 / 1024 / 1024 / 1024 / 1024 / 1024, 1)} YB"

    return str(size)


class Downloader:
    """
    @since 1.0.0
    @version 1.0.1
    @author Qboi123
    """

    def __init__(self, url, fp):
        """
        @author: Qboi123
        @version: 1.0.0
        @param url: url to download.
        @param fp: filepath to save the download to.
        """

        self._blockSize = 65536
        from threading import Thread
        self._url = url
        self._fp = fp
        self.fileSize = 1
        self.downloadedSize: int = 0
        self.downloaded: bool = False

        Thread(None, self.download).start()

    # noinspection PyUnboundLocalVariable,PyGlobalUndefined
    def download(self):
        """
        Start the download.

        @author: Qboi123
        @version: 1.0.0
        @return:
        """

        import urllib.request

        self.downloaded = False

        global active
        global total
        global spd
        global h, m, s
        global load
        h = "23"
        m = "59"
        s = "59"
        spd = 0
        total = 0

        dat = None

        while dat is None:
            # Get the total number of bytes of the file to download before downloading
            u = urllib.request.urlopen(str(self._url))
            if os.path.exists(self._fp):
                os.remove(self._fp)
            meta = u.info()
            dat = meta["Content-Length"]
        self.fileSize = int(dat)

        data_blocks = []
        total = 0

        with open(self._fp, "ab+") as f:
            while True:
                block = u.read(self._blockSize)
                data_blocks.append(block)
                self.downloadedSize += len(block)
                _hash = ((60 * self.downloadedSize) // self.fileSize)
                if not len(block):
                    active = False
                    break

                f.write(block)
            f.flush()
            f.close()

        # data = b''.join(data_blocks)
        u.close()

        self.downloaded = True


class WelcomePage(QWizardPage):
    """
    @author: Qboi123
    @version: 1.0.0
    """

    def __init__(self, parent: QWizard) -> None:
        """
        @author: Qboi123
        @version: 1.0.0
        @param parent: the installation wizard.
        """

        super().__init__(parent)

        self.setTitle(f"Welcome to {PRODUCT_NAME} Setup Wizard")
        self.label = QLabel(f"The Setup Wizard will install {PRODUCT_NAME} on your computer. Click Next to continue or Cancel to exit the Setup Wizard.")
        self.label.setWordWrap(True)

        self.setPixmap(wizard.WatermarkPixmap, QPixmap("watermark.png"))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


def set_only_for_me():
    global INSTALLATION_TYPE
    INSTALLATION_TYPE = InstallationType.ONLY_FOR_ME


def set_everybody():
    global INSTALLATION_TYPE
    INSTALLATION_TYPE = InstallationType.EVERYBODY


class InstallTypePage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)

        self.setTitle(f"Installation Type")
        self.setSubTitle(f"Choose the installation type.")
        self.label = QLabel(f"Install {PRODUCT_NAME} for:")
        self.label.setWordWrap(True)
        self.label.setContentsMargins(0, 48, 0, 0)

        types = QWidget(self)
        self.onlyForMe = QRadioButton(f"Only for me ({os.getlogin()})", types)
        self.everybody = QRadioButton(f"Everybody (all users)", types)
        types_layout = QVBoxLayout()
        types_layout.addWidget(self.onlyForMe)
        types_layout.addWidget(self.everybody)
        types.setLayout(types_layout)
        types.setContentsMargins(8, 0, 0, 0)

        self.onlyForMe.setChecked(INSTALLATION_TYPE == InstallationType.ONLY_FOR_ME)
        self.onlyForMe.clicked.connect(set_only_for_me)

        self.everybody.setChecked(INSTALLATION_TYPE == InstallationType.EVERYBODY)
        self.everybody.clicked.connect(set_everybody)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(types)
        self.setLayout(layout)


class LicenseAgreementPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)

        self.setTitle(f"End-User License Agreement")
        self.setSubTitle(f"Please read the following license agreement carefully.")

        self.textBrowser = QTextBrowser()
        self.textBrowser.setHtml(open("license.html", "r").read())
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setReadOnly(True)

        self.accept = QRadioButton("I accept the terms in the License Agreement")
        self.reject = QRadioButton("I do not accept the terms in the License Agreement")
        self.reject.setChecked(True)

        self.accept.clicked.connect(self.completeChanged.emit)
        self.reject.clicked.connect(self.completeChanged.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.textBrowser, QVBoxLayout.SizeConstraint.SetMaximumSize)
        layout.addWidget(self.accept)
        layout.addWidget(self.reject)
        self.setLayout(layout)
        self._wizard = wizard

    def initializePage(self) -> None:
        self.validate_agreement()

    def cleanupPage(self) -> None:
        self._wizard.button(QWizard.WizardButton.NextButton).setEnabled(True)

    def isComplete(self) -> bool:
        return self.accept.isChecked()

    def validate_agreement(self):
        accepted: bool = self.accept.isChecked()

        self._wizard.button(QWizard.WizardButton.NextButton).setEnabled(accepted)
        return accepted

    def validatePage(self) -> bool:
        if self.accept.isChecked():
            return True
        flags = QMessageBox.Ok
        QMessageBox.critical(self, "Agreement Reject", "You didn't accept the license agreement.\nIf you don't want to accept the agreement, you can also cancel the installation.", flags)
        return False


class FolderPage(QWizardPage):
    """
    @author: Qboi123
    @version: 1.0.0
    """
    def __init__(self, parent: QWizard) -> None:
        """
        @author: Qboi123
        @version: 1.0.8
        @param parent:
        """

        super().__init__(parent)

        self.folder = None
        self.setTitle(f"Select Installation Folder")
        self.setSubTitle(f"This is the folder where {PRODUCT_NAME} will be installed.")
        self.label = QLabel(f"To install in this folder, click \"Next\". To install to a different folder, enter it below or click \"Browse\".")
        self.label.setWordWrap(True)

        self.folderSelection = QWidget()
        folder_layout = QHBoxLayout()
        self.filePath = QComboBox(self)
        self.filePath.setEditable(True)
        self.browseBtn = QPushButton("Browse...", self)
        self.browseBtn.clicked.connect(self.on_browse)
        self.browseBtn.setMaximumWidth(120)
        folder_layout.addWidget(self.filePath)
        folder_layout.addWidget(self.browseBtn)

        fsm = QFileSystemModel()
        fsm.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Hidden)
        index = fsm.setRootPath(INSTALLATION_DIR)
        # fsm.setResolveSymlinks(True)
        self.filePath.setModel(fsm)
        self.filePath.setRootModelIndex(index)
        self.folderSelection.setLayout(folder_layout)
        self.filePath.setCurrentText(INSTALLATION_DIR)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.folderSelection)
        self.setLayout(layout)

    def on_browse(self):
        """

        @author: Qboi123
        @return:
        @version: 1.2.0
        """

        global INSTALLATION_DIR
        dir_ = QFileDialog.getExistingDirectory(self, "Select Installation Folder", INSTALLATION_DIR)
        if dir_ == "" or dir_ is None:
            return
        INSTALLATION_DIR = dir_
        self.filePath.setCurrentText(INSTALLATION_DIR)


class VerifyReadyPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)

        self.setTitle(f"Ready to Install")
        self.setSubTitle(f"The Setup Wizard is ready to begin the {PRODUCT_NAME} installation.")
        self.setButtonText(QWizard.WizardButton.NextButton, "Install")

        self.label = QLabel(f"Click Install to begin the installation. If you want to review or change any of your installation settings, click Back. Click Cancel to exit the wizard..")
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        next_btn = QPushButton("Next >", wizard)
        next_btn.clicked.connect(self.next)
        finish_btn = QPushButton("Finish", wizard)
        finish_btn.clicked.connect(self.next)
        wizard.setButton(QWizard.WizardButton.CommitButton, next_btn)
        wizard.setButton(QWizard.WizardButton.FinishButton, finish_btn)

        wizard.setButtonText(QWizard.WizardButton.CommitButton, wizard.buttonText(QWizard.WizardButton.NextButton))
        self.setCommitPage(True)
        self.runFile = f"{DATA_FOLDER}/Updater.exe"
        self.__update = False

    @staticmethod
    def on_close(event: QCloseEvent):
        event.setAccepted(False)

    def next(self):
        wiz = self.wizard()
        wiz.setOption(wiz.NoCancelButton, True)
        if isinstance(wiz.currentPage(), VerifyReadyPage):
            pag: DownloadPage = wiz.page(download_page)
            pag.init()
            wiz.closeEvent = self.on_close
        p = wiz.currentPage()
        if isinstance(p, DownloadPage):
            pass
            # pag: InstallPage = wiz.page(install_page)
            # pag.init(p.file)
        if isinstance(wiz.currentPage(), ExitPage):
            pag: ExitPage = wiz.page(exit_page)
            pag.run(self.runFile)


class DownloadPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)

        self.setTitle(f"Downloading {PRODUCT_NAME}")

        self.label = QLabel(f"Please wait while the Setup Wizard downloads the files for {PRODUCT_NAME}. This may take several minutes.")
        self.label.setWordWrap(True)

        self.status = QLabel("Status:")
        self.status.setContentsMargins(0, 16, 0, 0)

        self.progress = QProgressBar(self)
        self.progress.setMaximum(100)
        self.progress.setValue(36)
        self.progress.setMaximumHeight(16)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.setCommitPage(True)

        self.downloader: Optional[Downloader] = None
        self.url = DOWNLOAD_URL
        self.file = ""

        self.downloadEmitted: bool = False

    def isComplete(self) -> bool:
        if self.downloader is None:
            return False
        return self.downloader.downloaded

    def init(self):
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
        dl_path = f"{DATA_FOLDER}/Updater.exe"

        self.file = dl_path

        self.downloader = Downloader(self.url, dl_path)
        Thread(target=self.loop, name="DL-InfoLoop").start()

        return

    def loop(self):
        self.progress.setMaximum(self.downloader.fileSize + 1)
        while not self.downloader.downloaded:
            cur_size = self.downloader.downloadedSize
            dl_size = self.downloader.fileSize
            ratio = cur_size / dl_size

            get_updater().call_latest(self.progress.setMaximum, 10000)
            get_updater().call_latest(self.progress.setValue, int(10000 * ratio))
            get_updater().call_latest(self.status.setText, f"Downloaded {file_size(cur_size)} of {file_size(dl_size)}.")
        get_updater().call_latest(self.completeChanged.emit)


class ExitPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard) -> None:
        super().__init__(parent)

        self.setTitle(f"Completing the {PRODUCT_NAME} Setup Wizard")
        self.setButtonText(QWizard.WizardButton.NextButton, "Install")

        self.label = QLabel(f"Click the Finish button to exit the Setup Wizard.")
        self.label.setWordWrap(True)

        self.viewReadme = QCheckBox(f"View readme file")
        self.launch = QCheckBox(f"Launch {PRODUCT_NAME}")

        self.viewReadme.setChecked(VIEW_README)
        self.launch.setChecked(LAUNCH_APP)

        self.viewReadme.setContentsMargins(0, 64, 0, 0)
        self.launch.setContentsMargins(0, 32, 0, 0)

        self.viewReadme.clicked.connect(self.toggle_view_readme)
        self.launch.clicked.connect(self.toggle_launch)

        self.setPixmap(wizard.WatermarkPixmap, QPixmap("watermark.png"))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.viewReadme)
        layout.addWidget(self.launch)
        self.setLayout(layout)

    def toggle_view_readme(self):
        global VIEW_README
        VIEW_README = self.viewReadme.isChecked()

    def toggle_launch(self):
        global LAUNCH_APP
        LAUNCH_APP = self.launch.isChecked()


def help_requested():
    """
    @author: Qboi123
    @version: 0.1.0
    @return:
    """

    help_window = QWidget()
    # noinspection SpellCheckingInspection
    info = QLabel("This is an example help information. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed finibus quam a tellus mattis porta. Ut in dui sed ligula dictum commodo eu lacinia urna. Suspendisse a augue nec eros mollis finibus et sed erat. Etiam consectetur arcu a est accumsan aliquam. Morbi porta lobortis est at consequat. Sed ut ligula mauris. Vivamus ac elit eget odio semper sollicitudin in eu felis. Vestibulum lacinia efficitur orci, nec placerat quam molestie quis.")
    layout = QVBoxLayout()
    layout.addWidget(info)
    help_window.setLayout(layout)
    help_window.show()


def app_launch_path():
    return f"{INSTALLATION_DIR}/Updater.exe"


if __name__ == '__main__':
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        os.chdir(sys._MEIPASS)

    if WIZARD_STYLE_OVERRIDE is not None:
        WIZARD_STYLE = WIZARD_STYLE_OVERRIDE

    app = QApplication([])

    app.setWindowIcon(QIcon(f"icon.png"))

    def back(which: QWizard.WizardButton):
        if which == QWizard.WizardButton.CustomButton1:
            wizard.back()


    wizard: QWizard = QWizard()

    QtWin.setCompositionEnabled(True)
    QtWin.proenableBlurBehindWindow(wizard)
    wizard.DisabledBackButtonOnLastPage = True
    wizard.NoBackButtonOnStartPage = False
    # noinspection PyUnboundLocalVariable
    wizard.setWizardStyle(WIZARD_STYLE)
    wizard.setPixmap(wizard.LogoPixmap, QPixmap("logo.png"))
    wizard.setOption(wizard.WizardOption.ExtendedWatermarkPixmap, False)
    # if wizard.wizardStyle() == QWizard.WizardStyle.AeroStyle:
    #     print("YES")
    #     wizard.HaveCustomButton1 = True
    #     wizard.setButtonText(wizard.CustomButton1, "< Back")
    #     wizard.customButtonClicked.connect(back)
    #     wizard.setFixedSize(QSize(1024, 684))
    wizard.addPage(WelcomePage(wizard))
    wizard.addPage(InstallTypePage(wizard))
    wizard.addPage(LicenseAgreementPage(wizard))
    wizard.addPage(FolderPage(wizard))
    wizard.addPage(VerifyReadyPage(wizard))
    download_page = wizard.addPage(DownloadPage(wizard))
    # install_page = wizard.addPage(InstallPage(wizard))
    exit_page = last_page = wizard.addPage(ExitPage(wizard))
    wizard.setWindowTitle("QBubbles Installation")
    # wizard.helpRequested = help
    wizard.HaveHelpButton = False

    def finish():
        if LAUNCH_APP:
            subprocess.Popen(app_launch_path())


    if wizard.currentId() == wizard.pageIds()[-1]:
        wizard.finished = finish

    wizard.show()

    exec_ = app.exec_()

    sys.exit(exec_)
