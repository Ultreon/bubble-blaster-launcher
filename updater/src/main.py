"""
@see /launcher/src/main.py
@license GNU General Public License v3.0
@copyright Licensed under GPLv3
@organization Ultreon Team
@author: Qboi123
@since: 0.0.1
@version: 1.0.0
"""

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

import io
import os
import sys
import time
import warnings
from threading import Thread
from typing import Iterable, Union, Optional

# noinspection PyProtectedMember
import click
from PySide2.QtGui import QIcon, QCloseEvent
from PySide2.QtWidgets import QWizardPage, QLabel, QProgressBar, QVBoxLayout, QWizard, QPushButton, QApplication, \
    QMessageBox
from qt_thread_updater import get_updater

WIN32_APP_ID = u"UltreonTeam.BubbleBlaster.Installer.1.0.0.0"

# noinspection PyBroadException
try:
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WIN32_APP_ID)
except Exception:
    pass

SOURCE_DIR = os.path.join(*os.path.split(__file__)[:-1])
CUR_UPDATE_XML = os.getcwd().replace("\\", "/") + "/CurrentLauncher.xml"
TEMP_DIR = "%s/Temporary" % os.getcwd().replace("\\", "/")
LAUNCHER_XML = "https://github.com/Ultreon/bubble-blaster-launcher/raw/main/launcher_updates.xml"

if hasattr(sys, "_MEIPASS"):
    SOURCE_DIR = getattr(sys, "_MEIPASS")


class Version:
    def __init__(self, version, sub_version, release, state, state_build, time_: int):
        self.version = version
        self.sub_version = sub_version
        self.release = release
        self.state = state
        self.state_build = state_build

        self.time = time_


class Checker(object):
    """
    Update checker for the Bubble Blaster Launcher.

    @author: Qboi123
    @version: 1.0.4
    """

    # noinspection PyUnboundLocalVariable
    def __init__(self, state='alpha'):
        """
        @author: Qboi123
        @param state: the release state.
        @version: 1.0.3
        """

        self.curRunFile = None
        import xml.etree.ElementTree as ElemTree
        import urllib.request
        import urllib.parse
        print("[Checker]: State: %s" % state)
        # noinspection PyExceptClausesOrder
        url = urllib.request.urlopen(LAUNCHER_XML)
        output = url.read().decode()
        self._has_internet = True
        self.current = None

        root = ElemTree.fromstring(output)
        for index in range(len(root)):
            elem = root[index]
            if elem.tag == "Update":
                if elem.attrib["state"] >= state:
                    item_i = index
            if elem.tag == "RunFile":
                self.runFile: str = elem.text

        if not hasattr(self, "runFile"):
            raise ValueError("No RunFile element was found in launcher update xml.")

        try:
            self.newest = root[item_i]
        except NameError:
            self.newest = root[0]

        self.updates_xml = output

        if os.path.exists(CUR_UPDATE_XML):
            with open(CUR_UPDATE_XML, "r") as file:
                root = ElemTree.fromstring(file.read())

                for index in range(len(root)):
                    elem = root[index]
                    if elem.tag == "RunFile":
                        self.curRunFile: str = elem.text
                    if elem.tag == "Update":
                        a = elem.attrib
                        self.current_: Version(a["version"], a["subversion"], a["release"], a["state"], a["statebuild"],
                                               int(a["time"]))

                if not hasattr(self, "curRunFile"):
                    raise ValueError("No RunFile element was found in launcher update xml.")

                file.close()

            self.current = root[0]

    def is_newest(self) -> bool:
        """
        Find out if the version checker found an update (returns False) or not.

        @author: Qboi123
        @return: true if there are no updates, false if there are.
        @version: 1.1.0
        """

        return self.current is not None and self.newest.attrib["time"] <= self.current.attrib["time"]

    def get_newest_release(self):
        """
        Get the newest release.

        @author: Qboi123
        @return: the newest release.
        @version: 1.1.0
        @deprecated use Checker.is_newest(self) instead.
        """

        warnings.warn(DeprecationWarning("Use Checker.is_newest(self) instead."))
        return self.is_newest()

    def has_internet(self):
        """
        Check if the user has internet atm.

        @author: Qboi123
        @return: true if connected to the internet.
        @version: 1.0.0
        """

        return self._has_internet

    # noinspection PyMethodMayBeStatic
    def _get_current(self):
        """
        @author: Qboi123
        @return:
        @version: 0.0.2
        """

        warnings.warn(DeprecationWarning("Use Checker.current instead."))

    def get_xml(self):
        """
        Get the launcher_updates.xml data.

        @author: Qboi123
        @return:
        @version: 1.0.0
        """

        return self.updates_xml

    def get_update_url(self):
        """
        @author: Qboi123
        @return:
        @version: 1.0.0
        """

        try:
            return self.newest.attrib["url"]
        except AttributeError:
            self.__init__('r')
            return self.newest.attrib["url"]

    def has_installation(self):
        return self.current is not None


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

        while True:
            block = u.read(self._blockSize)
            data_blocks.append(block)
            self.downloadedSize += len(block)
            _hash = ((60 * self.downloadedSize) // self.fileSize)
            if not len(block):
                active = False
                break

            try:
                with open(self._fp, "ab+") as f:
                    f.write(block)
                    f.close()
            except FileNotFoundError:
                os.makedirs("%s/Temporary/" % os.getcwd().replace("\\", "/"))
                with open(self._fp, "ab+") as f:
                    f.write(block)
                    f.close()

        # data = b''.join(data_blocks)
        u.close()

        self.downloaded = True


# noinspection PyTypeChecker
class Log(io.IOBase):
    """
    @author: Qboi123
    @since: 0.0.5
    @version: 1.4.3
    @license: GNU General Public License v3.0
    """

    def __init__(self, file, std, name="Out"):
        """
        @author: Qboi123
        @param file: log file.
        @param std: system default output.
        @param name: name of the logger.
        @version: 1.0.0
        """

        self.file = file
        self.std = std
        self.name = name
        self.old = "\n"
        self.fp = None
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def write(self, o: str):
        """
        @author: Qboi123
        @version: 1.0.0
        @param o:
        @return:
        """

        if self.old[-1] == "\n":
            self.std.write("[" + time.ctime(time.time()) + "] [" + self.name + "]: " + o)
            self.fp = open(self.file, "a+")
            self.fp.write("[" + time.ctime(time.time()) + "] [" + self.name + "]: " + o)
            self.fp.close()
        else:
            self.std.write(o)
            self.fp = open(self.file, "a+")
            self.fp.write(o)
            self.fp.close()
        self.old = o

    def writelines(self, lines: Iterable[Union[bytes, bytearray]]) -> None:
        """
        @author: Qboi123
        @version: 1.0.0
        @param lines:
        @return:
        """

        for line in lines:
            self.write(line)

    # noinspection PyUnusedLocal,SpellCheckingInspection
    def potato(self, exefile):
        """
        @author: Qboi123
        @version: P.O.T.A.T.O
        @license Creative Commons Zero (only the method / function)
        @param exefile: nothing
        @return: void
        """

        self.flush()

    def flush(self):
        """
        @author: Qboi123
        @version: 0.0.1
        @return:
        """

        pass

    def fileno(self):
        """
        @author: Qboi123
        @version: 1.0.0
        @return:
        """

        self.fp = open(self.file, "a+")
        return self.fp.fileno()

    def read(self):
        """
        @author: Qboi123
        @version: 1.0.0
        @return:
        """

        import time
        a_ = self.std.read()
        self.fp = open(self.file, "a+")
        self.fp.write("[{time}] [In]: ".format(time=time.ctime(time.time())) + a_)
        self.fp.close()


def run(run_file):
    """
    Run the launcher.

    @author: Qboi123
    @version: 1.0.1
    @return:
    """

    cwd: str = os.getcwd().replace("\\", "/")
    os.chdir(f"{cwd}/Launcher")

    import subprocess
    cwd = os.path.normpath(os.getcwd())
    file: str = f"{cwd}/{run_file}".replace(os.path.sep, "/")

    print(f"[Runner]: Running: {file}")

    subprocess.Popen([file])


class UpdateFoundPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, wizard: QWizard, run_file: str, new_version: int, current_version: Optional[int],
                 update) -> None:
        super().__init__(wizard)

        self.setTitle(f"Update Available" if update else "Install Launcher")

        self.label = QLabel(
            f"There's a new update available for the launcher\nPress Next to update, or Cancel to go with the current version." if update else
            f"The launcher isn't installed yet, press Next to install.")
        self.label.setWordWrap(True)

        if not update:
            wizard.setOption(wizard.NoCancelButton, True)

        if update:
            self.new = QLabel("New update: " + time.strftime("%d %B %Y at %H:%M", time.gmtime(new_version)))
            self.new.setContentsMargins(0, 16, 0, 0)
            if current_version is not None:
                self.cur = QLabel("Current update: " + time.strftime("%d %B %Y at %H:%M", time.gmtime(current_version)))

        self.setFinalPage(False)
        self.setCommitPage(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        if update:
            layout.addWidget(self.new)
            if current_version is not None:
                layout.addWidget(self.cur)
        self.setLayout(layout)

        next_btn = QPushButton("Next >", wizard)
        next_btn.clicked.connect(self.next)
        finish_btn = QPushButton("Finish", wizard)
        finish_btn.clicked.connect(self.next)
        wizard.setButton(QWizard.WizardButton.CommitButton, next_btn)
        wizard.setButton(QWizard.WizardButton.FinishButton, finish_btn)

        wizard.setButtonText(QWizard.WizardButton.CommitButton, wizard.buttonText(QWizard.WizardButton.NextButton))
        self.setCommitPage(True)
        self.runFile = run_file
        self.__update = update

        if update:
            wizard.closeEvent = self.on_close1

    @staticmethod
    def on_close(event: QCloseEvent):
        event.setAccepted(False)

    # noinspection PyUnusedLocal
    def on_close1(self, event: QCloseEvent):
        if self.__update:
            run(self.runFile)

    def next(self):
        wiz = self.wizard()
        wiz.setOption(wiz.NoCancelButton, True)
        if isinstance(wiz.currentPage(), UpdateFoundPage):
            pag: DownloadPage = wiz.page(1)
            pag.init()
            wiz.closeEvent = self.on_close
        p = wiz.currentPage()
        if isinstance(p, DownloadPage):
            pag: InstallPage = wiz.page(2)
            pag.init(p.file)
        if isinstance(wiz.currentPage(), InstallPage):
            run(self.runFile)


class DownloadPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard, url, update: bool) -> None:
        super().__init__(parent)

        self.setTitle(f"Downloading Launcher update..." if update else
                      f"Downloading Launcher...")

        self.label = QLabel(f"Please wait while the Setup Wizard downloads the update for the launcher." if update else
                            f"Please wait while the Setup Wizard downloads the launcher.")
        self.label.setWordWrap(True)

        self.status = QLabel("Status:")
        self.status.setContentsMargins(0, 16, 0, 0)

        self.progress = QProgressBar(self)
        self.progress.setMaximumHeight(16)

        self.setFinalPage(False)
        self.setCommitPage(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.setCommitPage(True)
        self.downloader: Optional[Downloader] = None
        self.url = url
        self.file = ""

        self.downloadEmitted: bool = False

    def isComplete(self) -> bool:
        if self.downloader is None:
            return False
        return self.downloader.downloaded

    def init(self):
        import random

        cwd = os.getcwd().replace("\\", "/")

        value = random.randint(0x100000000000, 0xffffffffffff)
        filepath = hex(value)[2:] + ".tmp"

        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        dl_path = f"{cwd}/Temporary/{filepath}"

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

            # self._mutex.lock()
            get_updater().call_latest(self.progress.setMaximum, 10000)
            get_updater().call_latest(self.progress.setValue, int(10000 * ratio))
            get_updater().call_latest(self.status.setText,
                                      f"Downloaded {file_size(cur_size)} of {file_size(dl_size)}.")
            # self._mutex.unlock()
        get_updater().call_latest(self.completeChanged.emit)


class InstallPage(QWizardPage):
    """
    @license: GNU General Public License v3.0
    @author: Qboi123
    @version: 0.1.0
    """

    def __init__(self, parent: QWizard, update_xml: str, v, sv, r, st, stb, update: bool) -> None:
        super().__init__(parent)

        self.update_xml = update_xml
        self.setTitle(f"Installing Launcher update..." if update else
                      f"Installing Launcher...")

        self.label = QLabel(f"Please wait while the Setup Wizard installs the update for the launcher." if update else
                            f"Please wait while the Setup Wizard installs the launcher.")
        self.label.setWordWrap(True)

        self.status = QLabel("Status:")
        self.status.setContentsMargins(0, 16, 0, 0)

        self.progress = QProgressBar(self)
        self.progress.setMaximumHeight(16)

        self.setFinalPage(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.setCommitPage(True)
        self.__v = v
        self.__sv = sv
        self.__r = r
        self.__st = st
        self.__stb = stb

    def init(self, archive: str):
        Thread(target=lambda: self.extract(archive), name="Extraction").start()

    def extract(self, archive: str):
        import zipfile
        import shutil

        # Prepare vars
        cwd = os.getcwd()
        src = archive
        dst = "%s/Launcher" % os.getcwd().replace("\\", "/")
        extract_dir = "BubbleBlasterLauncher-"

        print("[Extractor]: IS_BUBBLE_BLASTER_FOLDER -> ", extract_dir == "BubbleBlasterLauncher-")
        print("[Extractor]: EXTRACTION_FOLDER -> ", extract_dir)

        get_updater().call_latest(self.status.setText, "Extracting...")
        zip_file = zipfile.ZipFile(src)

        # Remove old launcher directory and contents.
        get_updater().call_latest(self.status.setText, "Status: removing old launcher...")
        shutil.rmtree(f'{cwd}/Launcher', ignore_errors=True)

        path = os.fspath(f"{cwd}/Temporary/{extract_dir}")
        members = zip_file.namelist()

        # Extract all files of the zip file.
        member_count = members.__len__()
        get_updater().call_latest(self.progress.setMaximum, member_count)
        extracted = 0
        for member in members:
            # Update extraction progress
            get_updater().call_latest(self.progress.setValue, extracted)
            get_updater().call_latest(self.status.setText, f"Status: extracting {member}")

            # Extract one member.
            zip_file.extract(member, path, None)
            extracted += 1

        zip_file.close()

        os.remove(archive)

        # Move extracted data to the launcher installation folder.
        get_updater().call_latest(self.status.setText, "Status: moving extracted data to launcher installation.")
        shutil.move(f"{cwd}/Temporary/{extract_dir}", dst)

        get_updater().call_latest(self.progress.setValue, member_count)

        # Show error if launcher installation folder doesn't exist.
        if not os.path.exists(dst):
            get_updater().call_latest(lambda: self.crash(dst))
        else:
            with open(CUR_UPDATE_XML, "w+") as file:
                file.write(self.update_xml)
                file.flush()
                file.close()

    def crash(self, dst: str):
        QMessageBox.critical(self, "Extraction Error", f"Destination path doesn't exists:\n{dst}")
        sys.exit(1)


@click.command()
def main():
    checker = Checker()
    checker.is_newest()

    if not checker.is_newest():
        new = checker.newest.attrib
        app = QApplication()
        app.setWindowIcon(QIcon(f"{SOURCE_DIR}/icon.png"))

        wiz = QWizard()
        wiz.setWindowIcon(QIcon(f"{SOURCE_DIR}/icon.png"))
        wiz.setWindowTitle(f"Launcher Updater")
        wiz.addPage(UpdateFoundPage(wiz, checker.runFile, int(checker.newest.attrib["time"]),
                                    int(checker.current.attrib["time"]) if checker.current is not None else 0,
                                    checker.has_installation()))
        wiz.addPage(DownloadPage(wiz, checker.get_update_url(), checker.has_installation()))
        wiz.addPage(
            InstallPage(wiz, checker.updates_xml, new["version"], new["subversion"], new["release"], new["state"],
                        new["statebuild"],
                        checker.has_installation()))
        wiz.show()
        sys.exit(app.exec_())
    else:
        run(checker.curRunFile)


if __name__ == '__main__':
    startup = time.time()
    startup2 = time.ctime(startup).replace(" ", "-").replace(":", ".")

    if not os.path.exists("%s/Logs" % os.getcwd().replace("\\", "/")):
        os.makedirs("%s/Logs" % os.getcwd().replace("\\", "/"))

    if not os.path.exists("%s/Errors" % os.getcwd().replace("\\", "/")):
        os.makedirs("%s/Errors" % os.getcwd().replace("\\", "/"))

    log_file = time.strftime("%m-%d-%Y %H.%M.%S.log", time.gmtime(startup))

    stderr = Log(os.getcwd().replace("\\", "/") + "/Errors/" + log_file, sys.stderr, "Err")
    stdout = Log(os.getcwd().replace("\\", "/") + "/Logs/" + log_file, sys.stdout)
    sys.stderr = stderr
    sys.stdout = stdout

    main()
