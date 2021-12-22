#! /usr/bin/python3
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
from typing import Optional, Dict, List, Union, Any, Callable, BinaryIO
from zipfile import ZipFile

try:
    # noinspection PyUnresolvedReferences
    import win32api
except ImportError as e:
    pass
from PIL import Image, ImageTk, ImageDraw, ImageFont

DATA_FOLDER = None

if platform.system().lower() == "windows":
    DATA_FOLDER = f"C:/Users/{os.getlogin()}/AppData/Roaming/.bubbleblaster/"
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
    def _download_temp(self, httpIO: BinaryIO):
        import tempfile
        global active
        with tempfile.TemporaryFile("ba+") as f:
            # print(f.file)
            while True:
                block = httpIO.read(1024)
                # data_blocks.append(block)
                self.downloaded += len(block)
                _hash = ((60 * self.downloaded) // self.totalSize)
                if not len(block):
                    active = False
                    break
                f.write(block)
            f.close()


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class CustomScrollbar(Canvas):
    def __init__(self, parent, **kwargs):
        self.command = kwargs.pop("command", None)
        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        Canvas.__init__(self, parent, **kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        # coordinates are irrelevant; they will be recomputed
        # in the 'set' method\
        self.old_y = 0
        self._id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kwargs):
        command = kwargs.pop("command", None)
        self.command = command if command is not None else self.command
        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        super().configure(**kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"
        self.itemconfig(self._id, fill=kwargs["fg"], outline=kwargs["fg"])

    def config(self, cnf=None, **kwargs):
        self.configure(cnf, **kwargs)

    def redraw(self, event):
        # The command is presumably the `yview` method of a widget.
        # When called without any arguments it will return fractions
        # which we can pass to the `set` command.
        self.set(*self.command())

    def set(self, first, last):
        first = float(first)
        last = float(last)
        height = self.winfo_height()
        x0 = 4
        x1 = self.winfo_width() - 4
        y0 = max(int(height * first), 0) + 8
        y1 = min(int(height * last), height) - 8
        self._x0 = x0
        self._x1 = x1
        self._y0 = y0
        self._y1 = y1

        # noinspection PyTypeChecker
        self.coords("thumb", x0, y0, x1, y1)

    def on_press(self, event):
        self.bind("<Motion>", self.on_click)
        self.pressed_y = event.y
        self.on_click(event)

    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        y = event.y / self.winfo_height()
        y0 = self._y0
        y1 = self._y1
        a = y + ((y1 - y0) / -(self.winfo_height() * 2))
        self.command("moveto", a)


# noinspection PyUnusedLocal
class ScrolledWindow(Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected
    to canvas scrollregion.

    2. self.scrollwindow is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>.scrollwindow
    to get them inserted into canvas

    __init__(self, parent, canv_w = 400, canv_h = 400, *args, **kwargs)
    docstring:
    Parent = master of scrolled window
    canv_w - width of canvas
    canv_h - height of canvas

    """

    def __init__(self, parent, canv_w=400, canv_h=400, expand=False, fill=None, height=None, width=None, *args,
                 scrollcommand=lambda: None, scrollbarbg=None, scrollbarfg="darkgray", **kwargs):
        """Parent = master of scrolled window
        canv_w - width of canvas
        canv_h - height of canvas

       """
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.scrollCommand = scrollcommand

        # creating a scrollbars

        if width is None:
            __width = 0
        else:
            __width = width

        if height is None:
            __height = 0
        else:
            __height = width

        self.canv = Canvas(self.parent, bg='#FFFFFF', width=canv_w, height=canv_h,
                           scrollregion=(0, 0, __width, __height), highlightthickness=0)

        self.vbar = CustomScrollbar(self.parent, width=10, command=self.canv.yview, bg=scrollbarbg, fg=scrollbarfg)
        self.canv.configure(yscrollcommand=self.vbar.set)

        self.vbar.pack(side="right", fill="y")
        self.canv.pack(side="left", fill=fill, expand=expand)

        # creating a frame to insert to canvas
        self.scrollwindow = Frame(self.parent, height=height, width=width)

        self.scrollwindow2 = self.canv.create_window(0, 0, window=self.scrollwindow, anchor='nw', height=height,
                                                     width=width)

        self.canv.config(  # xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, canv_h, canv_w))

        self.scrollwindow.bind('<Configure>', self._configure_window)
        self.scrollwindow.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollwindow.bind('<Leave>', self._unbound_to_mousewheel)

        return

    def _bound_to_mousewheel(self, event):
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # self.scrollCommand(int(-1 * (event.delta / 120)), self.scrollwindow.winfo_reqheight(), self.vbar.get(),
        # self.vbar)

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight() + 1)
        # noinspection PyTypeChecker
        self.canv.config(scrollregion='0 0 %s %s' % size)
        # if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
        #     # update the canvas's width to fit the inner frame
        #     # self.canv.config(width=self.scrollwindow.winfo_reqwidth())
        # if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
        #     # update the canvas's width to fit the inner frame
        #     # self.canv.config(height=self.scrollwindow.winfo_reqheight())


# noinspection PyPep8Naming,PyShadowingNames
class CustomFontButton(ttk.Button):
    def __init__(self, master, text, width=None, foreground="black", truetype_font=None, font_path=None, size=None,
                 **kwargs):
        """
        Custom font for buttons.

        :param master:
        :param text:
        :param width:
        :param foreground:
        :param truetype_font:
        :param font_path:
        :param size:
        :param kwargs:
        """

        if truetype_font is None:
            if font_path is None:
                raise ValueError("Font path can't be None")

            # Initialize font
        print(tkinter.font.names())
        # tkinter.font.nametofont("TkTextFont").cget("family")
        # exit(1)

        truetype_font = ImageFont.truetype(font_path, size)

        w, h = truetype_font.getsize(text)

        h += 5
        # w, h = draw
        W = width + 20
        H = h + 20
        #
        # if width > width_2:
        #     width_ = width
        # else:
        #     width_ = width_2
        # print(width_2, width)

        image = Image.new("RGBA", (W, H), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # print(width)
        # print(width / 2)

        draw.text((((W - w) / 2) + 1, ((H - h) / 2) + 2), text, font=truetype_font, fill="#00000037", align="center")
        draw.text(((W - w) / 2, (H - h) / 2), text, font=truetype_font, fill=foreground)

        self._photoimage = ImageTk.PhotoImage(image)
        ttk.Button.__init__(self, master, image=self._photoimage, **kwargs)

        self.truetype_font = truetype_font
        self.font_path = font_path
        self.fsize = size
        self.text = text
        self.foreground = foreground
        self.width = width

    def configure(self, cnf=None, **kw):
        truetype_font = kw.pop("truetype_font", None)
        font_path = kw.pop("font_path", None)
        size = kw.pop("fsize", None)
        text = kw.pop("text", None)
        foreground = kw.pop("foreground", None)
        width = kw.pop("width", None)
        if foreground is None:
            foreground = kw.pop("fg", None)

        if (truetype_font is None) and (font_path is None) and (size is None) and (text is None) and (
                foreground is None) and (width is None):
            changed = False
        else:
            changed = True

        if truetype_font is None:
            truetype_font = self.truetype_font
        if font_path is None:
            font_path = self.font_path
        if size is None:
            size = self.fsize
        if text is None:
            text = self.text
        if foreground is None:
            foreground = self.foreground
        if width is None:
            width = self.width

        if changed:
            # Initialize font
            truetype_font = ImageFont.truetype(font_path, size)
            w, h = truetype_font.getsize(text)
        else:
            w, h = truetype_font.getsize(text)

        # print(width, width_2)
        # exit()

        if changed:
            # w, h = draw
            W = width + 20
            H = h + 20
            image = Image.new("RGBA", (W, H), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # print(width_2, width)

            draw.text(((W - w) / 2, ((H - h) / 2) - 2), text, font=truetype_font, fill=0x0000007f, align="center")
            draw.text(((W - w) / 2, (H - h) / 2), text, font=truetype_font, fill=foreground, align="center")

            self._photoimage = ImageTk.PhotoImage(image)
            super().configure(cnf, image=self._photoimage, **kw)

        else:
            super().configure(cnf, **kw)

        self.truetype_font = truetype_font
        self.font_path = font_path
        self.fsize = size
        self.text = text
        self.foreground = foreground

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)


class LauncherConfig(object):
    def __init__(self, token):
        """
        Not Implemented!

        :param token:
        """

        self.token = token


def get_resized_img(img, video_size):
    """
    Get resized image.

    :param img:
    :param video_size:
    :return:
    """

    width, height = video_size  # these are the MAX dimensions
    video_ratio = width / height
    img_ratio = img.size[0] / img.size[1]
    if video_ratio >= 1:  # the video is wide
        if img_ratio <= video_ratio:  # image is not wide enough
            height_new = int(width / img_ratio)
            size_new = width, height_new
        else:  # image is wider than video
            width_new = int(height * img_ratio)
            size_new = width_new, height
    else:  # the video is tall
        if img_ratio >= video_ratio:  # image is not tall enough
            width_new = int(height * img_ratio)
            size_new = width_new, height
        else:  # image is taller than video
            height_new = int(width / img_ratio)
            size_new = width, height_new
    return img.resize(size_new, resample=Image.LANCZOS)


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

    def __init__(self, type_: str, versionId: str, executablePath: str, download: Dict[str, str], version: str,
                 date: str, innerPath: str, **data):
        self.executable_path = executablePath
        self.type = type_
        self.versionId = versionId
        self.download_info = download
        self.version = version
        self.date = date
        self.path = os.path.join(DATA_FOLDER, f"Runtime/{type_}/{versionId}")
        self.innerPath = innerPath

        self.data = data

    @classmethod
    def load_or_get(cls, type_: str, versionId: str):
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

        return cls.__INSTANCES[type_][versionId]

    def download(self, messageLabel: Label, update: Callable[[], None]) -> Optional[str]:
        if os.path.exists(self.path):
            return

        messageLabel.configure(
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
            messageLabel.configure(
                text=f"Downloading Runtime: {int(100 * downloader.downloaded / downloader.totalSize)}%"
            )
            update()

        print("Extracting game runtime")

        messageLabel.configure(text=f"Extracting Runtime")

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
            messageLabel.configure(text=f"Error Occurred")
            return "Extension invalid: " + ext

        extraction_thread.start()
        while extraction_thread.is_alive():
            update()

        messageLabel.configure(text=f"Finalizing Runtime")

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
    def update(messageLabel: Label):
        messageLabel.configure(text="Extracting Runtime")


class Runtime:
    # noinspection PyShadowingBuiltins
    def __init__(self, *, type: str, version: Union[str, int], **data):
        self.sdk = SDK.load_or_get(type, str(version))
        self.type: str = type
        self.version: Union[str, int] = version
        self.data: Dict[str, Any] = data
        self.path = "Runtime/" + type + str(version)


class Version(object):
    def __init__(self, version_id, name, stable: bool, preRelease: bool, release: bool, runtime: dict, buildDate: str,
                 download: str, args: List[str], **data):
        self.versionID = version_id
        self.name = name
        self.stable = stable
        self.preRelease = preRelease
        self.release = release
        self.runtime = Runtime(**runtime)
        self.buildDate = buildDate
        self.download = download
        self.args = args
        self.data = data


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
            self.versions.append(
                Version(version_id, **data))


# noinspection PyUnusedLocal
class QLauncherWindow(Tk):
    def __init__(self):
        # Initialize window
        super(QLauncherWindow, self).__init__()

        # Configure window
        self.title("QBubbles Launcher")
        self.geometry("900x506")
        self.minsize(614, 400)

        # Makes closing the window, kills the process (or program)
        self.wm_protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), 0))

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
            self.profileName = win32api.GetUserNameEx(3)
        else:
            self.profileName = os.getlogin()

        # Update profile name and UUID.
        self.launcherConfig["profilename"] = self.profileName
        # self.launcherConfig["uuid"] = self.session.uuid
        self.save_launcher_config()

        # Setup theme
        self.setup_theme()

        print("Setup UI...")

        # Initialize icons for the modloader and Minecraft
        # self.iconRift = PhotoImage(file="icons/rift.png")
        # self.iconForge = PhotoImage(file="icons/forge.png")
        # self.iconFabric = PhotoImage(file="icons/fabric.png")
        # self.iconClassic = PhotoImage(file="icons/classic.png")
        # self.iconOptifine = PhotoImage(file="icons/optifine.png")
        # self.iconMinecraft = PhotoImage(file="icons/minecraft.png")

        self.iconIndev = PhotoImage(file="icons/indev.png")
        self.iconAlpha = PhotoImage(file="icons/alpha.png")
        self.iconBeta = PhotoImage(file="icons/beta.png")
        self.iconRelease = PhotoImage(file="icons/release.png")
        self.iconPreRelease = PhotoImage(file="icons/pre-release.png")
        self.iconUnknown = PhotoImage(file="icons/unknown.png")

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
        self.sw = ScrolledWindow(self.sPanel, vlw, self.winfo_height() + 0, expand=True, fill="both",
                                 scrollbarbg="#666666", scrollbarfg="#888888")

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
        self.playBtn = CustomFontButton(
            self.rightPanels, width=200, text="PLAY" if self.online else "PLAY OFFLINE", font_path="Roboto-Regular.ttf",
            foreground="white", size=30, command=lambda: self.play(self.selVersion.runtime))
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
        Update playbutton when resizing the window, this event is called from the bottom panel.

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
        Download event, used to update the playbutton text to show how far with downloading.

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
        Runs the game version. (Or in other words: Open an process for the game version)

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

        # print("Downloading game data: " + version.versionID)
        #
        # download = Downloader(
        #     version.downloadData, os.path.join(DATA_FOLDER, "._Temp", version.downloadData.split("/")[-1]))
        # while not download.done:
        #     self.playBtn.configure(
        #         text=f"Data {int(download.downloaded / 1024 / 1024)}/"
        #              f"{int(download.totalSize / 1024 / 1024)}")
        #     self.update()
        #
        # print("Downloading game requirements: " + version.versionID)
        #
        # download = Downloader(
        #     version.downloadReqs, os.path.join(DATA_FOLDER, "._Temp", version.downloadReqs.split("/")[-1]))
        # while not download.done:
        #     self.playBtn.configure(
        #         text=f"Reqs {int(download.downloaded / 1024 / 1024)}/"
        #              f"{int(download.totalSize / 1024 / 1024)}")
        #     self.update()
        #
        # print("Installing requirements: " + version.versionID)
        # self.playBtn.configure(text=f"Install Reqs")
        # self.update()
        # reqsfile = os.path.join(DATA_FOLDER, "._Temp", version.downloadReqs.split("/")[-1])
        # if " " in reqsfile:
        #     reqsfile = '"' + reqsfile + '"'
        # pip_installer = Thread(target=lambda: os.system("pip install -r " + reqsfile), name="PipInstaller")
        # pip_installer.start()
        # while pip_installer.is_alive():
        #     self.update()
        #
        # print("Extracting game data: " + version.versionID)
        # self.playBtn.configure(text=f"Extract Data")
        # zipfile = ZipFile(os.path.join(DATA_FOLDER, "._Temp", version.downloadData.split("/")[-1]), "r")
        #
        # dataextract_thread = Thread(
        #     target=lambda: zipfile.extractall(
        #         os.path.join(DATA_FOLDER, "data", version.versionID).replace('\\', "/")),
        #     name="DataExtractThread")
        # dataextract_thread.start()
        # while dataextract_thread.is_alive():
        #     self.update()
        # zipfile.close()
        return True

    def configure_event(self, evt):
        """
        Configure event for updating the background image for the resolution and scale

        :param evt:
        :return:
        """
        # Closes previous opened image
        # self._backgroundImage.close()

        # Open image and resize it
        # self._backgroundImage: PIL.Image.Image = PIL.Image.open("background.png")
        # self._backgroundImage = get_resized_img(self._backgroundImage, (evt.width, evt.height))

        # Convert to tkinter.PhotoImage(...)
        # self._tmp_img_tk = PIL.ImageTk.PhotoImage(self._backgroundImage)

        # Update background
        # self.canvas.itemconfig(self.background, image=self._tmp_img_tk)
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


if __name__ == '__main__':
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        os.chdir(sys._MEIPASS)

    os.makedirs(os.path.join(DATA_FOLDER, "Logs/Launcher"), exist_ok=True)
    file = open(os.path.join(DATA_FOLDER, time.strftime("Logs/Launcher/Log %Y-%m-%d %H.%M.%S.log")), "w+")
    sys.stdout = file
    sys.stderr = file


    def func_0(code: int, exit__: Callable[[int], None]):
        file.close()
        exit__(code)

    exit_ = sys.exit
    import builtins

    # noinspection PyShadowingBuiltins
    def exit(code: int):
        func_0(code, exit_)
    builtins.exit = lambda code: func_0(code, exit_)
    sys.exit = lambda code: func_0(code, exit_)

    try:
        QLauncherWindow().mainloop()
    except Exception as e:
        traceback.print_exception(e.__class__, e, e.__traceback__, file=sys.stderr)
    exit(0)
