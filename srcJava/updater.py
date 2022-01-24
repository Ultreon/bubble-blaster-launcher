import io
import math
import os
import platform
import sys
import time
from typing import Iterable, Union

import wx
# noinspection PyProtectedMember
import wx._core

DATA_FOLDER = None

if platform.system().lower() == "windows":
    DATA_FOLDER = os.path.join(os.getenv("appdata"), "BubbleBlasterLauncher/")
elif platform.system().lower() == "linux":
    if os.getlogin() == "root":
        DATA_FOLDER = f"/root/.BubbleBlasterLauncher/"
    else:
        DATA_FOLDER = f"/home/{os.getlogin()}/.BubbleBlasterLauncher/"
elif (platform.system().lower() == "macos") or (platform.system().lower() == "osx") or (
        platform.system().lower() == "darwin") or (platform.system().lower() == "macosx"):
    if os.getlogin() == "root":
        DATA_FOLDER = f"/root/.BubbleBlasterLauncher/"
    else:
        DATA_FOLDER = f"/Users/{os.getlogin()}/.BubbleBlasterLauncher/"
else:
    print("This program is currently only for Windows, MacOS and Linux", file=sys.stderr)
    exit()


class Checker(object):
    # noinspection PyUnboundLocalVariable
    def __init__(self, state='a'):
        import xml.etree.ElementTree as ElemTree
        import urllib.request
        import urllib.parse
        print("[Checker]: State: %s" % state)
        # noinspection PyExceptClausesOrder
        url = urllib.request.urlopen(
            "https://github.com/Ultreon/bubble-blaster-launcher/raw/main/launcher_updates.xml"
        )
        output = url.read().decode()
        self._has_internet = True
        self.current = None

        root = ElemTree.fromstring(output)
        for index in range(len(root)):
            elem = root[index]
            if elem.tag == "Update":
                if elem.attrib["state"] >= state:
                    item_i = index
                    break
            if elem.tag == "RunFile":
                self.runFile: str = elem.text

        if not hasattr(self, "runFile"):
            self.runFile = None

        try:
            self.newest = root[item_i]
        except NameError:
            self.newest = root[0]
        print(self.newest)

        self.updates_xml = output

    def is_newest(self):
        import xml.etree.ElementTree as ElemTree
        if os.path.exists(os.getcwd().replace("\\", "/") + "/current_launcher.xml"):
            with open(os.getcwd().replace("\\", "/") + "/current_launcher.xml", "r") as file:
                root = ElemTree.fromstring(file.read())
                file.close()
            for child in root:
                print(child.tag, child.attrib)

            self.current = root[0]
            if self.newest.attrib["time"] <= self.current.attrib["time"]:
                return True
            else:
                return False
        else:
            return False

    def get_newest_release(self):
        import xml.etree.ElementTree as ElemTree
        if os.path.exists(os.getcwd().replace("\\", "/") + "/current_launcher.xml"):
            with open(os.getcwd().replace("\\", "/") + "/current_launcher.xml", "r") as file:
                root = ElemTree.fromstring(file.read())
                file.close()
            for child in root:
                print(child.tag, child.attrib)

            self.current = root[0]

            if self.newest.attrib["time"] <= self.current.attrib["time"]:
                return True
            else:
                return False
        else:
            return False

    def has_internet(self):
        return self._has_internet

    def _get_current(self):
        pass

    def get_xml(self):
        return self.updates_xml

    def get_update_url(self):
        try:
            return self.newest.attrib["url"]
        except AttributeError:
            self.__init__('r')
            return self.newest.attrib["url"]


# noinspection PyUnboundLocalVariable,PyArgumentList
class Updater(wx.Panel):
    # noinspection PyUnusedLocal
    def __init__(self, url, xml, version, subversion, release, state, statebuild, *args, **kw):
        """
        Updater for Bubble Blaster Launcher.

        @param url:
        @param xml:
        @param version:
        @param subversion:
        @param release:
        @param state:
        @param statebuild:
        """
        super().__init__(*args, **kw)
        v = version
        sv = subversion
        r = release
        st = state
        stb = statebuild

        if (not os.path.exists("%s/game/downloaded" % os.getcwd().replace("\\", "/"))) or \
                not checker.is_newest():
            print("[Updater]: Downloading Launcher")
            launcher: str = self.download(url, "Downloading Launcher")
            print("[Updater]: Extracting Launcher")
            self.extract(launcher, "%s/game" % os.getcwd().replace("\\", "/"), "Extracting Launcher",
                         "BubbleBlasterLauncher-",
                         v, sv, r, st, stb)
            with open("%s/game/downloaded" % os.getcwd().replace("\\", "/"), "w+") as file:
                file.write("True")

        # Write current update file.
        with open("%s/current_launcher.xml" % os.getcwd().replace("\\", "/"), "w+") as file:
            file.write(xml)

    @staticmethod
    def replace_in_file(fp, old, new):
        with open(fp, "r") as file:
            d = file.read()
        with open(fp, "w") as file:
            d = d.replace(old, new)
            file.write(d)

    @staticmethod
    def extract(file, dir_, message, folder=None, v=None, sv=None, r=None, st=None, stb=None):
        """
        Extract a file into a directory.

        @param file: file to extract.
        @param dir_: directory to extract to.
        @param message: message.
        @param folder: folder.
        @param v: version.
        @param sv: sub-version.
        @param r: release.
        @param st: state
        @param stb: state-build.
        @return:
        """
        import zipfile
        import shutil

        load_ = wx.ProgressDialog("Please Wait...", "", style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ESTIMATED_TIME)
        load_.Show()

        if st == "a":
            copy = "%s.%s.%s-%s.%s" % (v, sv, r, "alpha", stb)
        elif st == "b":
            copy = "%s.%s.%s-%s.%s" % (v, sv, r, "beta", stb)
        elif st == "c":
            copy = "%s.%s.%s-%s.%s" % (v, sv, r, "rc", stb)
        elif st == "r":
            copy = "%s.%s.%s" % (v, sv, r)
        else:
            copy = None

        load_.SetTitle("Extracting...")
        load_.SetRange(100)
        load_.Update(0, "Extracting...\n" + message)

        zip_file = zipfile.ZipFile(file)
        if copy is not None:
            print("[Checking]:", folder == "BubbleBlasterLauncher-")
            print("[Checking]:", folder)
            if folder == "BubbleBlasterLauncher-":
                shutil.rmtree('%s/game' % os.getcwd().replace("\\", "/"), ignore_errors=True)

            load_.Update(1, "Extracting...\n" + message)
            zip_file.extractall("%s/temp" % os.getcwd().replace("\\", "/"))
            load_.Update(98, "Extracting...\n" + message)
            print(("%s/temp/" + folder + "%s") % (os.getcwd().replace("\\", "/"), copy), dir_)
            if folder == "Tkinter-Python-":
                for item in os.listdir(("%s/temp/" + folder + "%s") % (os.getcwd().replace("\\", "/"), copy)):
                    shutil.move(("%s/temp/" + folder + "%s/" + item) % (os.getcwd().replace("\\", "/"), copy),
                                dir_ + "/" + item)
            else:
                shutil.move(("%s/temp/" + folder + "%s") % (os.getcwd().replace("\\", "/"), copy), dir_)

            while not os.path.exists(dir_):
                time.sleep(1)
        else:
            if not os.path.exists(dir_):
                os.makedirs(dir_)
            load_.Update(99, "Extracting...\n" + message)
            zip_file.extractall(dir_)

        load_.Update(100, "Extracting...\n" + message)

    # noinspection PyProtectedMember
    def download(self, url, message="Downloading Launcher", fp=None) -> str:
        """
        Downloads a file.

        @param url: url to download.
        @param message: message for downloading.
        @param fp: file path to save to, use None to use temp file.
        @return: the file path it's downloaded to.
        """

        import random

        progress = wx.ProgressDialog("Please Wait...", "", style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE |
                                                                 wx.PD_ESTIMATED_TIME)

        progress.SetSize(400, 320)
        progress.Show()

        progress.SetTitle("Downloading...")
        progress.SetRange(100)
        progress.Update(0, "Downloading...\n" + message)

        value = random.randint(0x100000000000, 0xffffffffffff)
        if fp is None:
            filepath = hex(value)[2:] + ".tmp"
        else:
            filepath = fp

        if not os.path.exists("%s/temp" % os.getcwd().replace("\\", "/")):
            os.makedirs("%s/temp" % os.getcwd().replace("\\", "/"))

        downloader = Downloader(url, "%s/temp/%s" % (os.getcwd().replace("\\", "/"), filepath))
        # Thread(None, download.download, "DownloadThread")

        progress.SetRange(downloader.fileSize + 1)
        while not downloader.downloaded:
            # print("Downloaded: ", download.file_downloaded_bytes)
            # print("Total: ", download.file_total_bytes)
            try:
                progress.SetRange(downloader.fileSize)
                progress.Update(int(100 * downloader.downloadedSize / downloader.fileSize), message + "\n" +
                                self.file_size(downloader.downloadedSize) + " of " + self.file_size(
                    downloader.fileSize))
            except wx._core.wxAssertionError:
                pass

        # load.Destroy()

        return "%s/temp/%s" % (os.getcwd().replace("\\", "/"), filepath)

    @staticmethod
    def run():
        """
        Run the launcher.

        @return:
        """

        cwd: str = os.getcwd().replace("\\", "/")
        os.chdir(f"{cwd}/game")

        import subprocess
        cwd = os.path.normpath(os.getcwd())
        file: str = f"{cwd}/{checker.runFile}".replace(os.path.sep, "/")
        # print('[Run]: "{file}" "{py}"'.format(file=file, py=py))
        cmd = '"{file}"'.format(file=file)

        print("[Run-Game]: Running game with: %s" % cmd)

        process = os.system(cmd)
        print("[Run-Game]: Process Returned: %s" % process)
        if process != 0:
            print('[Run-Game]: Retrying with subprocess...')
            subprocess.call([file])
            while process is None:
                time.sleep(1)
            print("[Run-Game]: Process Returned: %s" % process)

    def file_size(self, size: int):
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


# noinspection PyPep8Naming
class Process(object):
    def __init__(self):

        self.process = None
        # self.process.Bind(wx.EVT_IDLE, self.OnIdle)

        # We can either derive from wx.Process and override OnTerminate
        # or we can let wx.Process send this window an event that is
        # caught in the normal way...
        # self.process.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)

    def OnExecuteBtn(self, cmd):

        self.process = wx.Process(self)
        self.process.Redirect()
        pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)
        print('OnExecuteBtn: "%s" pid: %s\n' % (cmd, pid))
        #
        # self.inp.Enable(True)
        # self.sndBtn.Enable(True)
        # self.termBtn.Enable(True)
        # self.cmd.Enable(False)
        # self.exBtn.Enable(False)
        # self.inp.SetFocus()

    def Execute(self, command):
        self.OnExecuteBtn(command)

    def OnSendText(self, text):
        print('OnSendText: "%s"\n' % text)
        text += '\n'
        self.process.GetOutputStream().write(text.encode('utf-8'))

    def Send(self, text):
        self.OnSendText(text)

    def OnCloseStream(self):
        print('OnCloseStream\n')
        self.process.CloseOutput()

    def Close(self):
        self.OnCloseStream()

    def OnIdle(self):
        if self.process is not None:
            stream = self.process.GetInputStream()
            err_stream = self.process.GetErrorStream()

            if stream.CanRead():
                text = stream.read()
                sys.stdout.write(text)
            if stream.CanRead():
                stderr_ = err_stream.read()
                sys.stderr.write(stderr_)

    def OnProcessEnded(self, evt):
        print('OnProcessEnded, pid:%s,  exitCode: %s\n' %
              (evt.GetPid(), evt.GetExitCode()))

        stream = self.process.GetInputStream()
        err_stream = self.process.GetErrorStream()

        if stream.CanRead():
            text = stream.read()
            sys.stdout.write(text)
        if stream.CanRead():
            stderr_ = err_stream.read()
            sys.stderr.write(stderr_)

        self.process.Destroy()
        self.process = None
        os.kill(os.getpid(), 0)

    def ShutdownDemo(self):
        """
        Called when the demo application is switching to a new sample. Tell
        the process to close (by closing its output stream) and then wait
        for the termination signals to be received and processed.

        @return:
        """

        if self.process is not None:
            self.process.CloseOutput()
            wx.MilliSleep(250)
            wx.Yield()
            self.process = None


class Downloader:
    def __init__(self, url, fp):
        self._blockSize = 131072
        from threading import Thread
        self._url = url
        self._fp = fp
        self.fileSize = 1
        self.downloadedSize: int = 0
        self.downloaded: bool = False

        Thread(None, self.download).start()

    # noinspection PyUnboundLocalVariable,PyGlobalUndefined
    def download(self):
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
                os.makedirs("%s/temp/" % os.getcwd().replace("\\", "/"))
                with open(self._fp, "ab+") as f:
                    f.write(block)
                    f.close()

        # data = b''.join(data_blocks)
        u.close()

        self.downloaded = True


# noinspection PyTypeChecker
class Log(io.IOBase):
    def __init__(self, file, std, name="Out"):
        self.file = file
        self.std = std
        self.name = name
        self.old = "\n"
        self.fp = None
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def write(self, o: str):
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
        for line in lines:
            self.write(line)

    # noinspection PyUnusedLocal,SpellCheckingInspection
    def potato(self, exefile):
        self.flush()

    def flush(self):
        pass

    def fileno(self):
        self.fp = open(self.file, "a+")
        return self.fp.fileno()

    def read(self):
        import time
        a_ = self.std.read()
        self.fp = open(self.file, "a+")
        self.fp.write("[{time}] [In]: ".format(time=time.ctime(time.time())) + a_)
        self.fp.close()


if __name__ == '__main__':
    startup = time.time()
    startup2 = time.ctime(startup).replace(" ", "-").replace(":", ".")

    if not os.path.exists("%s/logs" % os.getcwd().replace("\\", "/")):
        os.makedirs("%s/logs" % os.getcwd().replace("\\", "/"))

    if not os.path.exists("%s/errors" % os.getcwd().replace("\\", "/")):
        os.makedirs("%s/errors" % os.getcwd().replace("\\", "/"))

    log_file = time.strftime("%m-%d-%Y %H.%M.%S.log", time.gmtime(startup))

    # stderr = open(os.getcwd().replace("\\", "/") + "/logs/stderr-" + hex(int(startup))[2:]+".log", "w+")
    # stdout = open(os.getcwd().replace("\\", "/") + "/logs/stdout-" + hex(int(startup))[2:]+".log", "w+")
    stderr = Log(os.getcwd().replace("\\", "/") + "/errors/" + log_file, sys.__stderr__,
                 "Err")
    stdout = Log(os.getcwd().replace("\\", "/") + "/logs/" + log_file, sys.__stdout__)
    stdin = Log(os.getcwd().replace("\\", "/") + "/logs/" + log_file, sys.__stdout__)
    sys.stderr = stderr
    sys.stdout = stdout
    sys.stdin = stdin

    checker = Checker(state="r")
    print(f"[Updater]: HAS INTERNET = {checker.has_internet()}")
    print(f"[Updater]: IS NEWEST = {checker.is_newest()}")
    print(f"[Updater]: UPDATE URL = {checker.get_update_url()}")

    b = checker.newest.attrib

    if (not checker.is_newest()) or (not checker.has_internet()) or \
            ((not os.path.exists("%s/game/downloaded" % os.getcwd().replace("\\", "/")) or not (
                    os.path.exists("%s/runtime/downloaded" % os.getcwd().replace("\\", "/")))) or (
                     not os.path.exists("%s/runtime/tkinter_downloaded" % os.getcwd().replace("\\", "/"))) or (
                     not os.path.exists("%s/runtime/pip_installed" % os.getcwd().replace("\\", "/")))):
        app = wx.App()
        # root = wx.Frame()
        # root.Show(False)
        a = Updater(checker.get_update_url(), checker.get_xml(), b["version"], b["subversion"], b["release"],
                    b["state"],
                    b["statebuild"])
        a.run()
        app.Destroy()
    else:
        # noinspection PyTypeChecker
        Updater.run()
