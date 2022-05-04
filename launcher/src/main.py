#! /usr/bin/python3

import getpass
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
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
import io
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import time
import tkinter.font
import traceback
import uuid
from random import randint
from tarfile import TarFile
from threading import Thread
from tkinter import Tk, Frame, Canvas, ttk, Label, PhotoImage
from typing import Optional, Dict, List, Union, Any, Callable, BinaryIO, Iterable
from zipfile import ZipFile

from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, \
    QComboBox, QToolBar, QToolButton, QListWidget, QListWidgetItem, QWizard, QWizardPage, QCommandLinkButton, \
    QMessageBox, QLineEdit, QFormLayout

WIN32_APP_ID = u"UltreonTeam.BubbleBlaster.Installer.1.0.0.0"

# noinspection PyBroadException
try:
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WIN32_APP_ID)
except Exception:
    pass

os.getlogin = lambda: getpass.getuser()

if hasattr(sys, "_MEIPASS"):
    # noinspection PyProtectedMember
    os.chdir(sys._MEIPASS)

try:
    # noinspection PyUnresolvedReferences
    import win32api
    # noinspection PyUnresolvedReferences
    import pywintypes

    # print(win32api.GetUserNameEx(0))
    # print(win32api.GetUserNameEx(1))
    # print(win32api.GetUserNameEx(2))
    # print(win32api.GetUserNameEx(3))
    # print(win32api.GetUserNameEx(4))
    # print(win32api.GetUserName())

    # os.getlogin = lambda: win32api.GetUserName()
except ImportError as e:
    pass

DATA_FOLDER = None

if platform.system().lower() == "windows":
    DATA_FOLDER = os.path.join(os.getenv("appdata"), ".bubbleblaster/")
    # os.getlogin = lambda: win32api.GetUserNameEx(2)
elif platform.system().lower() == "linux":
    if os.getlogin() == "root":
        DATA_FOLDER = f"/root/.bubbleblaster/"
    else:
        DATA_FOLDER = f"/home/{os.getlogin()}/.bubbleblaster/"
elif (platform.system().lower() == "macos") or (platform.system().lower() == "osx") or (
        platform.system().lower() == "darwin") or (platform.system().lower() == "macosx"):
    if os.getlogin() == "root":
        DATA_FOLDER = f"/root/.bubbleblaster/"
    else:
        DATA_FOLDER = f"/home/{os.getlogin()}/.bubbleblaster/"
else:
    print("This program is currently Windows only")
    print("")
    input("Press ENTER to close this window")
    exit()

VERSIONS_FOLDER = os.path.join(DATA_FOLDER, "Versions")

COL_PLAY_BTN = "#008944"
REL_PLAY_BTN = "raised"
BD_PLAY_BTN = 5

TREEVIEW_BG = "#7f7f7f"
TREEVIEW_FG = "#9f9f9f"
TREEVIEW_SEL_BG = "gold"
TREEVIEW_SEL_FG = "white"

BUTTON_BG = "#7f7f7f"
BUTTON_BG_FOC = "gold"
BUTTON_BG_DIS = "#5c5c5c"
BUTTON_FG = "#a7a7a7"
BUTTON_FG_FOC = "white"
BUTTON_FG_DIS = "#7f7f7f"
BUTTON_BD_COL = "gold"
BUTTON_RELIEF = "flat"
BUTTON_BD_WID = 0

ENTRY_BG = "#7f7f7f"
ENTRY_BG_FOC = "gold"
ENTRY_BG_DIS = "#5c5c5c"
ENTRY_FG = "#a7a7a7"
ENTRY_FG_FOC = "white"
ENTRY_FG_DIS = "#7f7f7f"
ENTRY_BD_COL = "gold"
ENTRY_RELIEF = "flat"
ENTRY_BD_WID = 0
ENTRY_SEL_BG = "gold"
ENTRY_SEL_BG_FOC = "#fce58a"
ENTRY_SEL_BG_DIS = "#ec9712"
ENTRY_SEL_FG = "gold"
ENTRY_SEL_FG_FOC = "white"
ENTRY_SEL_FG_DIS = "#7f7f7f"

LAUNCHER_CFG = os.path.join(DATA_FOLDER, "launchercfg.json")

ICON_INDEV = "Icons/indev.png"
ICON_ALPHA = "Icons/alpha.png"
ICON_BETA = "Icons/beta.png"
ICON_PRE_RELEASE = "Icons/pre-release.png"
ICON_RELEASE = "Icons/release.png"
ICON_UNKNOWN = "Icons/unknown.png"


def create_file(fp):
    with open(fp, "w+") as f:
        f.flush()


class Downloader:
    def __init__(self, url, fp="", is_temp=False):
        self.isTemp = is_temp
        self.__url = url
        self.__filePath = fp
        self.totalSize = 1
        self.downloaded = 0
        self.done: bool = False

        Thread(None, self.download).start()

    # noinspection PyUnboundLocalVariable,PyGlobalUndefined
    def download(self):
        import urllib.request
        import os

        self.done = False

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

        meta_content_length: Optional[str] = None

        while meta_content_length is None:
            # Get the total number of bytes of the file to download before downloading
            http_io = urllib.request.urlopen(str(self.__url))
            if os.path.exists(self.__filePath):
                os.remove(self.__filePath)
            meta = http_io.info()
            meta_content_length: str = meta["Content-Length"]
        self.totalSize = int(meta_content_length)

        # data_blocks = []
        total = 0

        # Thread(None, lambda: speed(), "SpeedThread").start()

        if self.isTemp:
            self._download_temp(http_io)
        else:
            with open(self.__filePath, "ab+") as f:
                while True:
                    # Reading a block size of 1024.
                    # Todo: make block size customizable.
                    block: bytes = http_io.read(1024)
                    self.downloaded += len(block)
                    if not len(block):
                        active = False
                        break
                    f.write(block)

        # data = b''.join(data_blocks)
        http_io.close()

        if not os.path.exists(f"{DATA_FOLDER}/._Temp"):
            os.makedirs(f"{DATA_FOLDER}/._Temp")

        self.done = True

    # noinspection PyGlobalUndefined
    def _download_temp(self, http_io: BinaryIO):
        import tempfile
        global active
        with tempfile.TemporaryFile("ba+") as f:
            # print(f.file)
            while True:
                block = http_io.read(1024)
                # data_blocks.append(block)
                self.downloaded += len(block)
                _hash = ((60 * self.downloaded) // self.totalSize)
                if not len(block):
                    active = False
                    break
                f.write(block)
            f.close()


def data_path(path: str):
    """
    Get a file or folder path from data path.

    :param path:
    :return:
    """

    return os.path.join(DATA_FOLDER, path)


class SDK:
    _URL = "https://github.com/Ultreon/bubble-blaster/raw/main/sdks.json"
    __INSTANCES: Dict[str, Dict[str, 'SDK']] = None

    # noinspection PyPep8Naming
    def __init__(self, type_: str, version_id: str, executablePath: str, download: Dict[str, str], version: str,
                 date: str, innerPath: str, **data):
        self.executable_path = executablePath
        self.type = type_
        self.versionId = version_id
        self.download_info = download
        self.version = version
        self.date = date
        self.path = os.path.join(DATA_FOLDER, f"Runtime/{type_}/{version_id}")
        self.innerPath = innerPath

        self.data = data

    @classmethod
    def load_or_get(cls, type_: str, version_id: str):
        if cls.__INSTANCES is None:
            import urllib.request
            import urllib.error
            import http.client
            req: http.client.HTTPResponse = urllib.request.urlopen(cls._URL)

            sdks_json: dict = json.load(req)

            print(sdks_json)

            for type__, vers in sdks_json.items():
                print(vers)
                for version_id, data in vers.items():
                    print(data)
                    sdk = SDK(type__, version_id, **data)
                    if cls.__INSTANCES is None:
                        cls.__INSTANCES = {}
                    if not cls.__INSTANCES.keys().__contains__(type__):
                        cls.__INSTANCES[type__] = {}
                    cls.__INSTANCES[type__][version_id] = sdk

        return cls.__INSTANCES[type_][version_id]

    def download(self, message_label: Label, update: Callable[[], None]) -> Optional[str]:
        if os.path.exists(self.path):
            return

        message_label.configure(
            text=f"Prepare Downloading Runtime"
        )

        print("Prepare Downloading Game Runtime")
        if not os.path.exists(os.path.split(os.path.join(DATA_FOLDER, self.path))[0]):
            os.makedirs(os.path.split(os.path.join(DATA_FOLDER, self.path))[0])

        temp_folder: str = os.path.join(DATA_FOLDER, "._Temp")
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        arch = None
        system = None
        if platform.machine().lower() == "i386":
            arch = "x86"
        elif platform.machine().lower() == "amd64":
            arch = "x64"
        elif platform.machine().lower() == "arm32":
            arch = "arm"
        elif platform.machine().lower() == "arm64":
            arch = "arm"
        elif platform.machine().lower() == "armhf":
            arch = "arm"

        if platform.system().lower() == "windows":
            system = "win"
        elif platform.system().lower() == "linux" or platform.system().lower() == "unix":
            system = "lin"
        elif platform.system().lower() == "macos" or platform.system().lower() == "osx" or \
                platform.system().lower() == "macosx" or platform.system().lower() == "mac" or \
                platform.system().lower() == "darwin":
            system = "mac"

        if arch is None:
            print("Unknown machine type: " + platform.machine())
            return "Unknown machine type: " + platform.machine()

        dl_type = f"{system}-{arch}"
        url: str = self.download_info[dl_type]

        if url.endswith("tar.gz"):
            ext = ".tar.gz"
        elif url.endswith("tar"):
            ext = ".tar"
        elif url.endswith("zip"):
            ext = ".zip"
        else:
            print("Invalid download url, file type not supported: " + re.compile(
                r"(?:[a-zA-Z0-9_\-+=\[%\\ .,:;'\"\]]+/)*[a-zA-Z0-9_\-+=\[%\\ ,:;'\"\]]+((?:.[a-zA-Z0-9]*)+)"
            ).match(url).group(1), file=sys.stderr)
            return "Invalid download url, file type not supported: " + re.compile(
                r"(?:[a-zA-Z0-9_\-+=\[%\\ .,:;'\"\]]+/)*[a-zA-Z0-9_\-+=\[%\\ ,:;'\"\]]+((?:.[a-zA-Z0-9]*)+)"
            ).match(url).group(1)

        file_name = os.path.join(temp_folder, f"{uuid.uuid3(uuid.NAMESPACE_X500, url)}{ext}")

        print("Downloading game runtime")

        downloader = Downloader(url, file_name)
        while not downloader.done:
            message_label.configure(
                text=f"Downloading Runtime: {int(100 * downloader.downloaded / downloader.totalSize)}%"
            )
            update()

        print("Extracting game runtime")

        message_label.configure(text=f"Extracting Runtime")

        if ext == ".tar.gz":
            tar = tarfile.open(file_name, "r:gz")
            extraction_thread = Thread(target=lambda: self.extract_tar(tar), name="DataExtractThread")
        elif ext == ".tar":
            tar = tarfile.open(file_name, "r:")
            extraction_thread = Thread(target=lambda: self.extract_tar(tar), name="DataExtractThread")
        elif ext == ".zip":
            zip_ = ZipFile(file_name, "r")
            extraction_thread = Thread(target=lambda: self.extract_zip(zip_), name="DataExtractThread")
        else:
            message_label.configure(text=f"Error Occurred")
            return "Extension invalid: " + ext

        extraction_thread.start()
        while extraction_thread.is_alive():
            update()

        message_label.configure(text=f"Finalizing Runtime")

    def extract_tar(self, tar: TarFile):
        tar.extractall(self.path)
        tar.close()

    def extract_zip(self, zip_: ZipFile):
        zip_.extractall(self.path)
        zip_.close()

        inner: str = os.path.join(self.path, self.innerPath)
        for name in os.listdir(inner):
            old_path = os.path.join(inner, name)
            new_path = os.path.join(self.path, name)
            os.rename(old_path, new_path)
        os.rmdir(inner)

    @staticmethod
    def update(message_label: Label):
        message_label.configure(text="Extracting Runtime")


class Runtime:
    # noinspection PyShadowingBuiltins
    def __init__(self, *, type: str, version: Union[str, int], **data):
        self.sdk = SDK.load_or_get(type, str(version))
        self.type: str = type
        self.version: Union[str, int] = version
        self.data: Dict[str, Any] = data
        self.path = "Runtime/" + type + str(version)


class Version(object):
    # noinspection PyPep8Naming
    def __init__(self, version_id, name, stable: bool, preRelease: bool, release: bool, runtime: dict, buildDate: str,
                 download: str, args: List[str], librariesUrl = None, **data):
        self.versionID = version_id
        self.name = name
        self.stable = stable
        self.preRelease = preRelease
        self.release = release
        self.runtime = Runtime(**runtime)
        self.librariesUrl = librariesUrl
        self.buildDate = buildDate
        self.download = download
        self.args = args
        self.data = data

    def icon(self) -> QIcon:
        if self.versionID.lower().__contains__("indev"):
            icon: QIcon = QIcon(ICON_INDEV)
        elif self.versionID.lower().__contains__("alpha"):
            icon: QIcon = QIcon(ICON_ALPHA)
        elif self.versionID.lower().__contains__("beta"):
            icon: QIcon = QIcon(ICON_BETA)
        elif self.versionID.lower().__contains__("release"):
            icon: QIcon = QIcon(ICON_RELEASE)
        elif self.versionID.lower().__contains__("pre"):
            icon: QIcon = QIcon(ICON_PRE_RELEASE)
        else:
            icon: QIcon = QIcon(ICON_UNKNOWN)

        return icon


class VersionChecker(object):
    def __init__(self):
        self.url = "https://github.com/Ultreon/bubble-blaster/raw/main/versions.json"
        self.versions: List[Version] = []

    def download_version_list(self):
        import urllib.request
        import urllib.error
        import http.client

        print("Downloading Version Database...")

        req: http.client.HTTPResponse = urllib.request.urlopen(self.url)

        db_dict: dict = json.load(req)
        print(f"DB_Dict: {db_dict}")
        self.versions = []
        for version_id, data in db_dict["versions"].items():
            print(version_id)
            self.versions.append(
                Version(version_id, **data))


# noinspection PyUnusedLocal
class QLauncherWindow(Tk):
    def __init__(self):
        # Initialize window
        super(QLauncherWindow, self).__init__()

        # Configure window
        self.playBtn: Any = None
        self.sw: Any = None
        self.title("QBubbles Launcher")
        self.geometry("900x506")
        self.minsize(614, 400)

        # Makes closing the window, kills the process (or program)
        # self.wm_protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), 0))

        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)

        print("Reading launcher config")

        # Reading launcher configuration.
        if os.path.exists(LAUNCHER_CFG):
            with open(os.path.join(LAUNCHER_CFG)) as file_:
                self.launcherConfig = json.JSONDecoder().decode(file_.read())
                # print(self.launcherConfig["tokens"])
            if "tokens" in self.launcherConfig.keys():
                pass
        else:
            print("Launcher config doesn't exists, creating a new one...")
            self.launcherConfig = {}

        # Update launcher config keys if non-existent
        if "fullscreen" not in self.launcherConfig.keys():
            self.launcherConfig["fullscreen"] = False
        if "tokens" not in self.launcherConfig.keys():
            self.launcherConfig["tokens"] = {}
            # print(self.launcherConfig["tokens"])
        if "profilename" not in self.launcherConfig.keys():
            self.launcherConfig["profilename"] = f"player{randint(100, 999)}"
        if "uuid" not in self.launcherConfig.keys():
            self.launcherConfig["uuid"] = None
        self.save_launcher_config()

        # Get local versions.
        self.profiles = []
        if os.path.exists(os.path.join(DATA_FOLDER, "Versions")):
            versions_dir = os.path.join(DATA_FOLDER, "Versions")
            for item in os.listdir(os.path.join(DATA_FOLDER, "Versions")):
                _item_dir = os.path.join(versions_dir, item)
                if os.path.isdir(_item_dir):
                    if os.path.exists(os.path.join(_item_dir, item + ".jar")):
                        if os.path.exists(os.path.join(_item_dir, item + ".json")):
                            self.profiles.append(item)

        # print(self.profiles)

        # return self.auth_token

        print("Getting versions")

        # Getting versions

        self.profiles = []

        # Initialize versions
        # TODO: Add version loading here
        self.versionChecker: VersionChecker = VersionChecker()
        self.versionChecker.download_version_list()
        self.versions: List[Version] = self.versionChecker.versions

        self.profiles: Optional[List[Version]] = self.versions

        # Define selected version
        self.selVersion: Version = self.profiles[0] if len(self.profiles) > 0 else None

        # Define profile name
        if globals().__contains__("win32api"):
            # noinspection PyUnresolvedReferences
            try:
                self.profileName = win32api.GetUserNameEx(3)
            except pywintypes.error:
                self.profileName = os.getlogin()
        else:
            self.profileName = os.getlogin()

        # Update profile name and UUID.
        self.launcherConfig["profilename"] = self.profileName
        # self.launcherConfig["uuid"] = self.session.uuid
        self.save_launcher_config()

        # Setup theme
        self.setup_theme()

        print("Setup UI...")

        self.iconIndev = PhotoImage(file="Icons/indev.png")
        self.iconAlpha = PhotoImage(file="Icons/alpha.png")
        self.iconBeta = PhotoImage(file="Icons/beta.png")
        self.iconRelease = PhotoImage(file="Icons/release.png")
        self.iconPreRelease = PhotoImage(file="Icons/pre-release.png")
        self.iconUnknown = PhotoImage(file="Icons/unknown.png")

        # Initialize colors for the modloader and Minecraft
        # self.colorRift = "#D7D7D7"
        # self.colorForge = "#3E5482"
        # self.colorFabric = "#BFB49C"
        self.colorClassic = "#7A7A7A"
        # self.colorOptifine = "#AD393B"
        # self.colorMinecraft = "#A8744F"

        # self._backgroundImage: PIL.Image.Image = PIL.Image.open("background.png")
        # self._tmp_img_tk = PIL.ImageTk.PhotoImage(self._backgroundImage)

        self.rootFrame = Frame(self, bg="#282828")

        # Version list width
        vlw = 300

        self.online = True

        # Initialize left panel
        self.leftPanel = Frame(self.rootFrame, height=75, width=vlw)

        # Initialize user info and status
        self.userFrame = Canvas(self.leftPanel, bg="#282828", height=75, highlightthickness=0, width=vlw)
        self.userNameText = self.userFrame.create_text(10, 10, text=self.launcherConfig["profilename"],
                                                       font=("helvetica", 10, "bold"), fill="white", anchor="nw")
        self.userStatusIcon = self.userFrame.create_rectangle(11, 41, 19, 49,
                                                              fill="#008542" if self.online else "#434343",
                                                              outline=COL_PLAY_BTN if self.online else "#434343")
        self.userStatusText = self.userFrame.create_text(25, 45,
                                                         text="Online" if self.online else "Offline",
                                                         fill="#a5a5a5", anchor="w", font=("helvetica", 10))
        self.userFrame.pack(fill="x")

        # Slots frame.
        self.sPanel = Frame(self.leftPanel, height=self.rootFrame.winfo_height() - 100, width=vlw)
        self.sPanel.pack(side="left", fill="y")

        # Scrollwindow for the slots frame
        # self.sw = ScrolledWindow(self.sPanel, vlw, self.winfo_height() + 0, expand=True, fill="both",
        #                          scrollbarbg="#666666", scrollbarfg="#888888")

        # Configure the canvas from the scrollwindow
        self.canv = self.sw.canv
        self.canv.config(bg="#1e1e1e")
        self.sw.vbar.config(bg="#1e1e1e", fg="#353535")

        # Initialize frames.
        self.frame_sw = self.sw.scrollwindow
        self.frames = []

        # Defining the list of widgets
        self._id = {}
        self.index = {}
        self.canvass = []
        self.buttons = []

        # Initialize canvas selected and hovered data.
        self.oldSelected: Optional[Canvas] = None
        self.selectedCanvas: Optional[Canvas] = None
        self._hoverCanvasOld: Optional[Canvas] = None
        self._hoverCanvas: Optional[Canvas] = None

        # Define the index variable.
        i = 0

        # Initialize colors, canvas and text.
        self.cColors: Dict[Canvas, str] = {}
        self.tColors: Dict[Canvas, List[str]] = {}

        versions_dir = data_path("versions/")
        if not os.path.exists(versions_dir):
            os.makedirs(versions_dir)

        # Creates items in the versions menu.
        for profile in self.profiles:
            self.frames.append(Frame(self.frame_sw, height=32, width=vlw, bd=0))
            self.canvass.append(Canvas(self.frames[-1], height=32, width=vlw, bg="#1e1e1e", highlightthickness=0, bd=0))
            self.canvass[-1].pack()
            self._id[self.canvass[-1]] = {}

            if profile.versionID.lower().__contains__("indev"):
                icon: PhotoImage = self.iconIndev
            elif profile.versionID.lower().__contains__("alpha"):
                icon: PhotoImage = self.iconAlpha
            elif profile.versionID.lower().__contains__("beta"):
                icon: PhotoImage = self.iconBeta
            elif profile.versionID.lower().__contains__("release"):
                icon: PhotoImage = self.iconRelease
            elif profile.versionID.lower().__contains__("pre"):
                icon: PhotoImage = self.iconPreRelease
            else:
                icon: PhotoImage = self.iconUnknown
            self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=icon,
                                                                               anchor="nw")
            color = self.colorClassic
            if profile not in os.listdir(versions_dir):
                t_color = ["#434343", "#7f7f7f", "#a5a5a5"]
                color = "#434343"
            else:
                t_color = ["#a5a5a5", "#ffffff", "#ffffff"]
            self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(37, 15, text=profile.name,
                                                                               fill=t_color[0], anchor="w",
                                                                               font=("helvetica", 11))
            self.cColors[self.canvass[-1]] = color
            self.tColors[self.canvass[-1]] = t_color
            self.canvass[-1].bind("<ButtonRelease-1>",
                                  lambda event, v=profile, c=self.canvass[-1]: self.select_version(c, v))
            self.canvass[-1].bind("<Double-Button-1>", lambda event, v=profile: self.play_version(v))
            self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canv_motion(c))
            self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canv_leave(c))
            self.index[self.canvass[-1]] = i
            self.frames[-1].pack(side="top")

            i += 1

        self.leftPanel.pack(side="left", fill="y")

        self.rightPanels = Frame(self.rootFrame, bg="#282828")
        self.canvas = Canvas(self.rightPanels, bg="#006060", highlightthickness=0)
        for _ in range(2500):
            x = randint(0, 1920 * 4)
            y = randint(0, 1080 * 4)
            r = randint(21, 80) / 2
            self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="white")
        # self.background = self.canvas.create_image(0, 0, anchor="nw", image=self._tmp_img_tk)
        self.canvas.pack(fill="both", expand=True)
        self.bottomPanel = Frame(self.rightPanels, bg="#262626", height=60)
        # self.playBtn = CustomFontButton(
        #     self.rightPanels, width=200, text="PLAY" if self.online else "PLAY OFFLINE", font_path="Roboto-Regular.ttf",
        #     foreground="white", size=30, command=lambda: self.play(self.selVersion.runtime))
        self.playBtn.place(x=self.bottomPanel.winfo_width() / 2, y=self.bottomPanel.winfo_y() + 10, anchor="n")
        self.label = Label(
            self.bottomPanel, height=1, text="",
            fg="#ffffff", bg="#262626", anchor="center", font=("Helvetica", 11))
        self.bottomPanel.pack(side="bottom", fill="x")
        self.rightPanels.pack(side="right", fill="both", expand=True)
        self.rootFrame.pack(side="left", fill="both", expand=True)

        # Event bindings
        # self.canvas.bind("<Configure>", self.configure_event)
        self.bottomPanel.bind("<Configure>", self.on_bottompanel_configure)

        self.wm_attributes("-fullscreen", self.launcherConfig["fullscreen"])

    def _on_canv_leave(self, hover_canvas):
        """
        Updates canvas when the cursor is leaving the menu item region.

        :param hover_canvas:
        :return:
        """

        if self._hoverCanvasOld is not None:
            if self.selectedCanvas != self._hoverCanvasOld:
                self._hoverCanvasOld.config(bg="#1e1e1e")
                self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][0], font=("helvetica", 11))
            else:
                self._hoverCanvasOld.config(bg=self.cColors[self._hoverCanvasOld])
                self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][2], font=("helvetica", 11))
        self._hoverCanvasOld = None

    def _on_canv_motion(self, hover_canvas):
        """
        Updates menu item hover color, and the old hover menu item color.

        :param hover_canvas:
        :return:
        """

        if self._hoverCanvasOld == hover_canvas:
            return
        if self._hoverCanvasOld is not None:
            if self.selectedCanvas != self._hoverCanvasOld:
                self._hoverCanvasOld.config(bg="#1e1e1e")
                self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][0], font=("helvetica", 11))
            else:
                self._hoverCanvasOld.config(bg=self.cColors[self._hoverCanvasOld])
                self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][2], font=("helvetica", 11))
        self._hoverCanvasOld = hover_canvas

        if hover_canvas != self.selectedCanvas:
            hover_canvas.config(bg="#353535")
            hover_canvas.itemconfig(self._id[hover_canvas]["Title"], fill=self.tColors[hover_canvas][1],
                                    font=("helvetica", 11, "bold"))
        else:
            hover_canvas.config(bg=self.cColors[hover_canvas])
            hover_canvas.itemconfig(self._id[hover_canvas]["Title"], fill=self.tColors[hover_canvas][2],
                                    font=("helvetica", 11, "bold"))
        self._hoverCanvas = hover_canvas

    def _on_canv_lclick(self, c: Canvas):
        """
        Event for clicking on an item in the versions menu.

        :param c:
        :return:
        """

        self.selectedCanvas = c

    def select_version(self, c: Canvas, version):
        """
        Update canvas colors, and sets selected version.

        :param c:
        :param version:
        :return:
        """

        if self.oldSelected is not None:
            self.oldSelected.config(bg="#1e1e1e")
            self.oldSelected.itemconfig(self._id[self.oldSelected]["Title"], fill=self.tColors[self.oldSelected][0],
                                        font=("helvetica", 11))
        self.oldSelected = c

        c.config(bg=self.cColors[c])
        c.itemconfig(self._id[c]["Title"], fill=self.tColors[c][2], font=("helvetica", 11, "bold"))

        self.selectedCanvas = c

        self.selVersion = version

    def play_version(self, version: Version):
        """
        Runs a specific version instead from selected version.

        :param version:
        :return:
        """

        self.selVersion = version
        self.play(runtime=version.runtime)

    def on_bottompanel_configure(self, evt):
        """
        Update play button when resizing the window, this event is called from the bottom panel.

        :param evt:
        :return:
        """
        try:
            self.playBtn.place_forget()
            self.playBtn.place(x=self.bottomPanel.winfo_width() / 2, y=self.bottomPanel.winfo_y() - 10, anchor="n")
        except tkinter.TclError as error:
            pass
        try:
            self.label.place_forget()
            self.label.place(x=20, y=30, width=self.bottomPanel.winfo_width() - 40, anchor="w")
        except tkinter.TclError as error:
            pass

    def save_launcher_config(self):
        """
        Saves launcher configuration

        :return:
        """

        print("Saving launcher configuration...")

        # Open file and write the JSON data.
        with open(os.path.join(LAUNCHER_CFG), "w+") as file_:
            file_.write(json.dumps(self.launcherConfig, sort_keys=True, indent=4) + "\n")

        print("Launcher configuration saved.")

    def download_event(self, x):
        """
        Download event, used to update the play button text to show how far with downloading.

        :param x:
        :return:
        """

        try:
            self.playBtn.config(text=str(x.currentvalue) + "/" + str(x.maxvalue))
        except RuntimeError:  # Fixes crashing when closing the window while downloading
            exit(0)
        self.update()

    def play(self, runtime: Runtime):
        """
        Runs the game version. (Or in other words: Open a process for the game version)

        :return:
        """

        self.label.place(x=20, y=30, width=self.bottomPanel.winfo_width() - 40, anchor="w")

        sdk = runtime.sdk
        runtime_path = os.path.join(DATA_FOLDER, runtime.path)
        java_executable = os.path.normpath(os.path.join(sdk.path, sdk.executable_path))

        self.playBtn.destroy()

        if not os.path.exists(os.path.join(DATA_FOLDER, runtime.path)):
            sdk.download(self.label, self.update)

        print("Preparing Game Jar")
        self.label.configure(text="Preparing Game Jar")
        jar_file = os.path.join(DATA_FOLDER, f"Versions/{self.selVersion.versionID}/{self.selVersion.versionID}.jar")

        if not os.path.exists(jar_file):
            if not self.download(jar_file, self.selVersion):
                return False

        if " " in jar_file:
            jar_file = '"' + jar_file + '"'

        os.chdir(DATA_FOLDER)

        game_dir = DATA_FOLDER
        if " " in game_dir:
            game_dir = '"' + game_dir + '"'

        print("Running game from Java")
        self.label.configure(text="Running game from Java")
        # win32api.ShellExecute()
        subprocess.Popen([java_executable, "-jar", jar_file, f"gameDir={game_dir}"],
                         stdout=sys.stdout, stderr=sys.stderr)
        # command = shlex.join(["cmd", "/c", "start", java_executable, "-jar", jar_file, f"gameDir={game_dir}"])
        # var = os.spawnl(os.P_DETACH, java_executable, "-jar", jar_file, f"gameDir={game_dir}")
        return True

    def download(self, version_path, version: Version) -> bool:
        self.label.configure(text=f"Preparing to download the game...")

        if version.download is None:
            self.label.configure(text=f"Failed to prepare download: Download not available yet.\nRestart the launcher.",
                                 height=2)
            print("Download not available yet.")
            return False

        if not os.path.exists(os.path.split(os.path.join(DATA_FOLDER, version_path))[0]):
            os.makedirs(os.path.split(os.path.join(DATA_FOLDER, version_path))[0])
        print(os.path.split(os.path.join(DATA_FOLDER, version_path))[0])

        print("Downloading game version: " + version.versionID)

        download_path: str = os.path.join(DATA_FOLDER, version_path)
        print("Downloading to path: " + download_path)
        download = Downloader(
            version.download, download_path)
        while not download.done:
            self.label.configure(
                text=f"Downloading game... ({int(100 * download.downloaded / download.totalSize)}%)")
            self.update()

        return True

    def configure_event(self, evt):
        """
        Configure event for updating the background image for the resolution and scale

        @param evt:
        @return:
        """

        self.canvas.update()

    @staticmethod
    def setup_theme():
        # Creating theme
        style = ttk.Style()
        style.theme_settings("default", {
            "TEntry": {
                "configure": {"font": ("Consolas", 10), "relief": "flat", "selectborderwidth": 0},
                "map": {
                    "relief": [("active", ENTRY_RELIEF),
                               ("focus", ENTRY_RELIEF),
                               ("!disabled", ENTRY_RELIEF)],
                    "bordercolor": [("active", ENTRY_BD_COL),
                                    ("focus", ENTRY_BD_COL),
                                    ("!disabled", ENTRY_BD_COL)],
                    "background": [("active", ENTRY_BG_DIS),
                                   ("focus", ENTRY_BG_FOC),
                                   ("!disabled", ENTRY_BG)],
                    "fieldbackground": [("active", ENTRY_BG_DIS),
                                        ("focus", ENTRY_BG_FOC),
                                        ("!disabled", ENTRY_BG)],
                    "foreground": [("active", ENTRY_FG_DIS),
                                   ("focus", ENTRY_FG_FOC),
                                   ("!disabled", ENTRY_FG)],
                    "selectbackground": [("active", ENTRY_SEL_BG_DIS),
                                         ("focus", ENTRY_SEL_BG_FOC),
                                         ("!disabled", ENTRY_SEL_BG)],
                    "selectforeground": [("active", ENTRY_SEL_FG_DIS),
                                         ("focus", ENTRY_SEL_FG_FOC),
                                         ("!disabled", ENTRY_SEL_FG)]
                }
            },
            "TLabel": {
                "configure": {"background": "#5c5c5c",
                              "foreground": "#7f7f7f",
                              "font": ("Consolas", 10)}
            },
            "TButton": {
                "configure": {"font": ("FixedSys", 18, "bold"), "relief": REL_PLAY_BTN, "borderwidth": BD_PLAY_BTN,
                              "highlightcolor": "white"},
                "map": {
                    "background": [("active", "#0a944e"),
                                   ("focus", COL_PLAY_BTN),
                                   ("pressed", "#0C6E3D"),
                                   ("!disabled", COL_PLAY_BTN),
                                   ("disabled", "#5f5f5f")],
                    "lightcolor": [("active", "#27CE40"),
                                   ("focus", "#27CE40"),
                                   ("!disabled", "#27CE40")],
                    "darkcolor": [("active", "#0a944e"),
                                  ("focus", "#27CE40"),
                                  ("!disabled", "#27CE40")],
                    "bordercolor": [("active", "#0A944E"),
                                    ("focus", COL_PLAY_BTN),
                                    ("pressed", "#0C6E3D"),
                                    ("!disabled", COL_PLAY_BTN),
                                    ("disabled", "#5f5f5f")],
                    "foreground": [("active", "white"),
                                   ("focus", "white"),
                                   ("pressed", "white"),
                                   ("!disabled", "white")],
                    "relief": [("active", REL_PLAY_BTN),
                               ("focus", REL_PLAY_BTN),
                               ("pressed", REL_PLAY_BTN),
                               ("!disabled", REL_PLAY_BTN)]
                }
            },
            "Treeview": {
                "configure": {"padding": 0, "font": ("Consolas", 10), "relief": "flat", "border": 0, "rowheight": 24},
                "map": {
                    "background": [("active", TREEVIEW_BG),
                                   ("focus", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_BG),
                                   ("selected", TREEVIEW_BG)],
                    "fieldbackground": [("active", TREEVIEW_BG),
                                        ("focus", TREEVIEW_BG),
                                        ("!disabled", TREEVIEW_BG)],
                    "foreground": [("active", TREEVIEW_FG),
                                   ("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_FG),
                                   ("selected", TREEVIEW_FG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            },
            "Treeview.Item": {
                "configure": {"padding": 0},
                "map": {
                    "background": [("active", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_SEL_BG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "fieldbackground": [("!disabled", TREEVIEW_SEL_BG),
                                        ("active", TREEVIEW_SEL_BG),
                                        ("!selected", TREEVIEW_SEL_BG)],
                    "foreground": [("active", TREEVIEW_SEL_BG),
                                   ("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_SEL_FG),
                                   ("selected", TREEVIEW_SEL_BG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            },
            "Treeview.Cell": {
                "configure": {"padding": 0},
                "map": {
                    "background": [("active", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_SEL_BG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "fieldbackground": [("!disabled", TREEVIEW_SEL_BG),
                                        ("active", TREEVIEW_SEL_BG),
                                        ("!selected", TREEVIEW_SEL_BG)],
                    "foreground": [("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_SEL_FG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            }
        })
        # Using theme and configure
        style.theme_use("default")
        style.configure('TEntry', relief='flat')

        # Configure TEntry layout, for removing border relief
        style.layout('TEntry', [
            ('Entry.highlight', {
                'sticky': 'nswe',
                'children':
                    [('Entry.border', {
                        'border': '5',
                        'sticky': 'nswe',
                        'children':
                            [('Entry.padding', {
                                'sticky': 'nswe',
                                'children':
                                    [('Entry.textarea',
                                      {'sticky': 'nswe'})]
                            })]
                    })]
            })])


class Profile:
    def __init__(self, name: str, version: str):
        self.name: str = name
        self.version: str = version


class ProfileManager:
    def __init__(self):
        self.__data: List = []
        self.__file = os.path.join(DATA_FOLDER, "Profiles.json")

        self.profiles: List[Profile] = []

    def load(self):
        if os.path.exists(self.__file):
            with open(self.__file, "r") as file_:
                self.__data = json.load(file_)

        print(self.__data)

        if isinstance(self.__data, list):
            print(self.__data)
            self.profiles = []
            for item in self.__data:
                print(item)
                if isinstance(item, dict):
                    name: str = "unnamed"
                    if "name" in item:
                        name = item["name"]
                    version: str = "0.0.0"
                    if "version" in item:
                        version = item["version"]

                    profile = Profile(name, version)
                    self.profiles.append(profile)

    def save(self):
        self.__data = []
        for profile in self.profiles:
            self.__data.append({"name": profile.name, "version": profile.version})

        with open(self.__file, "w+") as file_:
            json.dump(self.__data, file_)


class ProfilesList(QListWidget):
    def __init__(self, profile_man: ProfileManager, widget: QWidget):
        super().__init__(widget)

        self.profileMan = profile_man
        self.profiles: List[Profile] = self.profileMan.profiles

    def load_profiles(self):
        for profile in self.profiles:
            item = QListWidgetItem(profile.name)
            item.setData(QListWidgetItem.UserType, profile)
            self.addItem(item)

    def selected_profile(self) -> Optional[Profile]:
        sel_items = self.selectedItems()
        if sel_items.__len__() == 0:
            return None
        return sel_items[0].data(QListWidgetItem.UserType)


class VersionsList(QListWidget):
    def __init__(self, widget: QWidget):
        super().__init__(widget)

        self.versionChecker: VersionChecker = VersionChecker()
        self.versions: Optional[List[Version]] = None

    def load_versions(self):
        self.versionChecker.download_version_list()
        self.versions = self.versionChecker.versions

        for version in self.versions:
            item = QListWidgetItem(version.icon(), version.name)
            item.setData(QListWidgetItem.UserType, version)
            self.addItem(item)

    def selected_version(self) -> Optional[Version]:
        sel_items = self.selectedItems()
        if sel_items.__len__() == 0:
            return None
        return sel_items[0].data(QListWidgetItem.UserType)


class CreatePages:
    class AddOptionsPage(QWizardPage):
        def __init__(self, manage_type: 'ManageWizard.ManageTypePage'):
            super().__init__()

            self.setTitle("Create Profile")
            self.setSubTitle("Enter the name, and select version for the profile")

            self.manageType = manage_type
            self.wizard = self.manageType.wizard

            self.nameEdit = QLineEdit(self)
            self.versionList = VersionsList(self)

            load_thread = Thread(target=self.versionList.load_versions, name="VersionDB-Loader")
            load_thread.start()

            self.nameEdit.textChanged.connect(lambda evt: self.completeChanged.emit())
            self.versionList.selectionChanged = lambda old, new: self.completeChanged.emit()
            self.versionList.deselectionChanged = lambda old, new: self.completeChanged.emit()

            layout = QFormLayout()
            layout.addRow("Name: ", self.nameEdit)
            layout.addRow("Version: ", self.versionList)

            self.setLayout(layout)
            self.setButtonText(QWizard.WizardButton.FinishButton, "Create")
            self.setButtonText(QWizard.WizardButton.NextButton, "Create")

            self.createButton = QPushButton("Create")
            self.createButton.clicked.connect(self.create_profile)

            self.wizard.setButton(QWizard.WizardButton.FinishButton, self.createButton)
            self.wizard.button(self.wizard.BackButton).setEnabled(False)

        def isComplete(self):
            if not self.nameEdit.text().isprintable():
                return False
            if self.nameEdit.text().isspace():
                return False
            if self.nameEdit.text().__len__() == 0:
                return False
            if self.versionList.selectedItems().__len__() == 0:
                return False
            return True

        def create_profile(self):
            name: str = self.nameEdit.text()
            version: Version = self.versionList.selected_version()

            util_panel: UtilitiesPanel = self.wizard.panel
            man = util_panel.profileMan

            man.profiles.append(Profile(name, version.versionID))
            man.save()
            util_panel.reload_profiles()


class DeletePages:
    class SelectProfilePage(QWizardPage):
        def __init__(self, manage_type: 'ManageWizard.ManageTypePage'):
            super().__init__()

            self.setTitle("Delete Profile")
            self.setSubTitle("Select profile, click Delete to delete.")

            self.manageType = manage_type
            self.wizard = self.manageType.wizard

            self.profileList = ProfilesList(self.wizard.panel.profileMan, self)
            self.profileList.load_profiles()

            self.profileList.selectionChanged = lambda old, new: self.completeChanged.emit()
            self.profileList.deselectionChanged = lambda old, new: self.completeChanged.emit()

            layout = QVBoxLayout()
            layout.addWidget(self.profileList)

            self.setLayout(layout)
            self.setButtonText(QWizard.WizardButton.FinishButton, "Delete")
            self.setButtonText(QWizard.WizardButton.NextButton, "Delete")

            self.deleteButton = QPushButton("Delete")
            self.deleteButton.clicked.connect(self.delete_profile)

            self.wizard.setButton(QWizard.WizardButton.FinishButton, self.deleteButton)
            self.wizard.button(self.wizard.BackButton).setEnabled(False)

        def isComplete(self):
            return self.profileList.selectedItems().__len__() != 0

        def delete_profile(self):
            profile: Profile = self.profileList.selected_profile()

            util_panel: UtilitiesPanel = self.wizard.panel
            man = util_panel.profileMan

            man.profiles.remove(profile)
            man.save()
            util_panel.reload_profiles()


class ModifyPages:
    class SelectProfilePage(QWizardPage):
        def __init__(self, manage_type: 'ManageWizard.ManageTypePage'):
            super().__init__()

            self.setTitle("Create Profile")
            self.setSubTitle("Enter the name, and select version for the profile")

            self.profilesList = ProfilesList(manage_type.wizard.panel.profileMan, self)
            self.profilesList.load_profiles()

            layout = QVBoxLayout()
            layout.addWidget(self.profilesList)

            self.setLayout(layout)

            self.manageType = manage_type
            self.wizard = self.manageType.wizard

            self.setFinalPage(False)
            self.wizard.button(QWizard.WizardButton.NextButton).clicked.connect(self.next)
            self.page2: 'ModifyPages.SetOptionsPage' = ModifyPages.SetOptionsPage(self, self.manageType)

        def profile(self):
            return self.profilesList.selected_profile()

        def next(self):
            self.page2.init()
            self.wizard.setPage(2, ModifyPages.SetOptionsPage(self, self.manageType))

    class SetOptionsPage(QWizardPage):
        def __init__(self, sel_prof_page: 'ModifyPages.SelectProfilePage', manage_type: 'ManageWizard.ManageTypePage'):
            super().__init__()

            self.setTitle("Create Profile")
            self.setSubTitle("Enter the name, and select version for the profile")

            self.manageType = manage_type
            self.wizard = self.manageType.wizard

            self.selProfPage = sel_prof_page

            self.nameEdit = QLineEdit(self)
            self.versionList: VersionsList = VersionsList(self)
            self.nameEdit.textChanged.connect(lambda evt: self.completeChanged.emit())
            self.versionList.selectionChanged = lambda old, new: self.completeChanged.emit()
            self.versionList.deselectionChanged = lambda old, new: self.completeChanged.emit()

            layout = QFormLayout()
            layout.addRow("Name: ", self.nameEdit)
            layout.addRow("Version: ", self.versionList)

            self.setLayout(layout)
            self.setButtonText(QWizard.WizardButton.FinishButton, "Create")
            self.setButtonText(QWizard.WizardButton.NextButton, "Create")

            self.createButton = QPushButton("Create")
            self.createButton.clicked.connect(self.edit_profile)

            self.wizard.setButton(QWizard.WizardButton.FinishButton, self.createButton)
            self.wizard.button(self.wizard.BackButton).setEnabled(False)

        def isComplete(self):
            if not self.nameEdit.text().isprintable():
                return False
            if self.nameEdit.text().isspace():
                return False
            if self.nameEdit.text().__len__() == 0:
                return False
            if self.versionList.selectedItems().__len__() == 0:
                return False
            return True

        def edit_profile(self):
            profile: Profile = self.selProfPage.profile()
            profile.name = self.nameEdit.text()

            print(self.versionList.selectedItems())
            profile.version = self.versionList.selected_version().versionID

            util_panel: UtilitiesPanel = self.wizard.panel
            man = util_panel.profileMan
            man.save()
            util_panel.reload_profiles()

        def init(self):
            profile = self.selProfPage.profile()
            self.nameEdit.setText(profile.name)

            self.versionList.load_versions()
            i: int = 0
            found: bool = False
            for version in self.versionList.versions:
                if version.versionID == profile.version:
                    found = True
                    break
                i += 1

            if found:
                self.versionList.setItemSelected(self.versionList.item(i), True)

            print(self.versionList.selectedItems())
            self.completeChanged.emit()


class ManageWizard(QWizard):
    class ManageTypePage(QWizardPage):
        def __init__(self, wizard: 'ManageWizard'):
            super().__init__()

            self.setTitle("Management Type")
            self.setSubTitle("Select the option to Create, Modify or Delete a profile.")

            self.createBtn = QCommandLinkButton("Create", "Add a new profile and download the version if it's not yet downloaded.")
            self.modifyBtn = QCommandLinkButton("Modify", "Next option is to select a profile, then you can edit the name and other options.")
            self.deleteBtn = QCommandLinkButton("Delete", "Delete a profile. Note: this deletes the profile permanently.")

            self.createBtn.clicked.connect(self.on_create)
            self.modifyBtn.clicked.connect(self.on_modify)
            self.deleteBtn.clicked.connect(self.on_delete)

            layout = QVBoxLayout()
            layout.addSpacing(32)
            layout.addWidget(self.createBtn)
            layout.addWidget(self.modifyBtn)
            layout.addWidget(self.deleteBtn)

            self.setLayout(layout)

            self.wizard = wizard
            self.setButtonText(QWizard.WizardButton.FinishButton, "Click an option")

        def on_create(self):
            self.wizard.addPage(CreatePages.AddOptionsPage(self))
            self.wizard.next()

        def on_delete(self):
            self.wizard.addPage(DeletePages.SelectProfilePage(self))
            self.wizard.next()

        def on_modify(self):
            page1 = ModifyPages.SelectProfilePage(self)
            page2 = page1.page2
            self.wizard.addPage(page1)
            self.wizard.addPage(page2)
            self.wizard.next()

        def isComplete(self) -> bool:
            return False

    def __init__(self, panel: 'UtilitiesPanel'):
        super().__init__(panel.panel.main)

        self.setWindowModality(Qt.WindowModality.WindowModal)

        self.setWizardStyle(QWizard.WizardStyle.AeroStyle)
        self.addPage(ManageWizard.ManageTypePage(self))

        self.panel = panel

    def helpRequested(self):
        QMessageBox.information(self, "Help Information", "This dialog is used to manage profiles, you can create, edit or delete profiles here.")


class UtilitiesPanel(QWidget):
    def __init__(self, panel: 'BottomPanel'):
        super().__init__(panel)

        self.combo = QComboBox(self)
        self.combo.setFixedWidth(160)

        # self.combo.addItem("Profile 1")
        # self.combo.addItem("Profile 2")
        # self.combo.addItem("Profile 3")
        # self.combo.addItem("Profile 4")

        self.profileMan = ProfileManager()
        self.profileMan.load()

        self.reload_profiles()

        self.manageBtn = QPushButton("Manage")
        self.manageBtn.clicked.connect(self.manage)

        # self.switch = QPushButton("Switch to edit mode")
        # self.switch.clicked.connect(self.switch_edit_mode)

        # self.versionChecker: VersionChecker = VersionChecker()
        # self.versionChecker.download_version_list()
        # self.versions: List[Version] = self.versionChecker.versions
        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.manageBtn)
        # layout.addWidget(self.switch)
        self.setLayout(layout)
        self.panel = panel

        self.manageWizard: Optional[ManageWizard] = None

    def switch_edit_mode(self):
        self.panel.main.switch_edit_mode()

    def manage(self):
        self.manageWizard = ManageWizard(self)
        self.manageWizard.show()

    def reload_profiles(self):
        self.combo.clear()
        for profile in self.profileMan.profiles:
            self.combo.addItem(profile.name, profile)


class Library:
    def __init__(self, group: str, name: str, version: str, download: str):
        self.group = group
        self.name = name
        self.version = version
        self.download = download


class VersionProfile:
    def __init__(self, libraries: List[Library]):
        self.libraries: List[Library] = libraries


class VersionManager:
    def __init__(self):
        self.__versions: List[VersionProfile] = []
        self.load()

    INSTANCE = __init__()

    def load(self):
        versionUrl = "https://ultreon.github.io/web/data/project/bubble-blaster/versions.json"
        self.__versions = []


class BottomPanel(QWidget):
    def __init__(self, main_: 'Main'):
        super().__init__(main_)

        self.versionManager = VersionManager.INSTANCE

        self.left = UtilitiesPanel(self)

        self.playBtn = QPushButton("PLAY", self)
        self.playBtn.setFixedHeight(48)
        self.playBtn.setFixedWidth(108)
        self.playBtn.clicked.connect(self.play)

        layout = QHBoxLayout()
        layout.addWidget(self.left)
        layout.addStretch(0x1)
        layout.addWidget(self.playBtn)
        layout.addStretch(0x1)

        self.setLayout(layout)
        self.main = main_

    def play(self):
        self.left.versionManager.get_version_data()


class EditMode(QWidget):
    def __init__(self, main_: 'Main'):
        super().__init__(main_)

        self.toolbar = QToolBar()
        self.new = QToolButton()
        self.toolbar.addWidget(self.new)

        self.listView = QListWidget()
        self.listView.setViewMode(QListWidget.ViewMode.IconMode)
        self.listView.addItem(QListWidgetItem(QIcon("Icons/indev.png"), "Indev", self.listView))
        self.listView.addItem(QListWidgetItem(QIcon("Icons/alpha.png"), "Alpha", self.listView))
        self.listView.addItem(QListWidgetItem(QIcon("Icons/beta.png"), "Beta", self.listView))
        self.listView.addItem(QListWidgetItem(QIcon("Icons/pre-release.png"), "Pre-Release", self.listView))
        self.listView.addItem(QListWidgetItem(QIcon("Icons/release.png"), "Release", self.listView))
        self.listView.addItem(QListWidgetItem(QIcon("Icons/unknown.png"), "Unknown", self.listView))

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.listView)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        self.main = main_


class Main(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bubble Blaster Launcher")
        self.setMinimumSize(528, 550)
        self.setBaseSize(1280, 720)
        self.resize(1280, 720)

        self.view = QWebEngineView(self)
        self.view.setContentsMargins(0, 0, 0, 0)

        # self.edit = EditMode(self)

        self.bottom = BottomPanel(self)
        self.bottom.sizePolicy().setHorizontalStretch(0x77)

        layout = QVBoxLayout()
        layout.addWidget(self.view, QVBoxLayout.SizeConstraint.SetMaximumSize)
        # layout.addWidget(self.edit, QVBoxLayout.SizeConstraint.SetMaximumSize)
        layout.addWidget(self.bottom)
        layout.setContentsMargins(0, 0, 0, 0)

        # self.edit.hide()

        self.view.load(QUrl("https://ultreon.github.io/bubble-blaster/ChangeLog"))

        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def switch_edit_mode(self):
        if self.view.isVisible():
            self.view.hide()
            self.edit.show()
        else:
            self.view.show()
            self.edit.hide()


# noinspection PyTypeChecker
class Log(io.IOBase):
    """
    @author: Qboi123
    @since: 0.0.5
    @version: 1.4.3
    @license: GNU General Public License v3.0
    """

    def __init__(self, file_, std, name="Out"):
        """
        @author: Qboi123
        @param file_: log file.
        @param std: system default output.
        @param name: name of the logger.
        @version: 1.0.0
        """

        self.file = file_
        self.std = std
        self.name = name
        self.old = "\n"
        self.fp = None
        if not os.path.exists("Logs"):
            os.makedirs("Logs")

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


def main():
    app = QApplication()
    app.setWindowIcon(QIcon(f"icon.png"))

    main_ = Main()
    main_.show()

    sys.exit(QApplication.exec_())


if __name__ == '__main__':
    start_time = time.time()
    start_ctime = time.ctime(start_time).replace(" ", "-").replace(":", ".")

    if not os.path.exists("%s/Logs" % os.getcwd().replace("\\", "/")):
        os.makedirs("%s/Logs" % os.getcwd().replace("\\", "/"))

    if not os.path.exists("%s/Errors" % os.getcwd().replace("\\", "/")):
        os.makedirs("%s/Errors" % os.getcwd().replace("\\", "/"))

    log_file = time.strftime("%m-%d-%Y %H.%M.%S.log", time.gmtime(start_time))

    stderr = Log(os.getcwd().replace("\\", "/") + "/Errors/" + log_file, sys.stderr, "Err")
    stdout = Log(os.getcwd().replace("\\", "/") + "/Logs/" + log_file, sys.stdout)
    # sys.stderr = stderr
    # sys.stdout = stdout

    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        os.chdir(sys._MEIPASS)

    os.makedirs(os.path.join(DATA_FOLDER, "Logs/Launcher"), exist_ok=True)
    file = open(os.path.join(DATA_FOLDER, time.strftime("Logs/Launcher/Log %Y-%m-%d %H.%M.%S.log")), "w+")

    try:
        # QLauncherWindow().mainloop()/
        main()
    except Exception as e:
        traceback.print_exception(e.__class__, e, e.__traceback__, file=sys.stderr)
