import io
import os as system
import sys as application
import time
from typing import Iterable, Union

import wx
# noinspection PyProtectedMember
import wx._core


class Checker(object):
    # noinspection PyUnboundLocalVariable
    def __init__(self, state='a'):
        import xml.etree.ElementTree as ElemTree
        import urllib.request
        import urllib.parse
        print("[Checker]: State: %s" % state)
        # noinspection PyExceptClausesOrder
        url = urllib.request.urlopen(
            "https://github.com/Ultreon/bubble-blaster-launcher/raw/master/updates.xml"
        )
        output = url.read().decode()
        self._has_internet = True
        self.current = None
        # except urllib.error.URLError:
        #     self._has_internet = False
        #     return
        # except urllib.error.HTTPError:
        #     self._has_internet = False
        #     return

        root = ElemTree.fromstring(output)
        for index in range(len(root)):
            if root[index].attrib["state"] >= state:
                item_i = index
                break

        try:
            self.newest = root[item_i]
        except NameError:
            self.newest = root[0]
        print(self.newest)
        #
        # for index in range(len(root)-1, -1, -1):
        #     print(root[index].attrib["state"])
        #     if root[index].attrib["state"] >= state:
        #         item_i = index
        #         print(root[index].attrib)
        self.updates_xml = output

    def is_newest(self):
        import xml.etree.ElementTree as ElemTree
        if system.path.exists(system.getcwd().replace("\\", "/") + "/updates.xml"):
            with open(system.getcwd().replace("\\", "/") + "/updates.xml", "r") as file:
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
        if system.path.exists(system.getcwd().replace("\\", "/") + "/updates.xml"):
            with open(system.getcwd().replace("\\", "/") + "/updates.xml", "r") as file:
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
        Updater for Qplay Launcher.
        LOL

        :param url:
        :param xml:
        :param version:
        :param subversion:
        :param release:
        :param state:
        :param statebuild:
        """
        super().__init__(*args, **kw)
        v = version
        sv = subversion
        r = release
        st = state
        stb = statebuild

        if (((not system.path.exists("%s/game/downloaded" % system.getcwd().replace("\\", "/"))) or
                not checker.is_newest()) or
                not (system.path.exists("%s/runtime/downloaded" % system.getcwd().replace("\\", "/")))) or (
                not system.path.exists("%s/runtime/tkinter_downloaded" % system.getcwd().replace("\\", "/"))) or (
                not system.path.exists("%s/runtime/pip_installed" % system.getcwd().replace("\\", "/"))):
            pass
        if (not system.path.exists("%s/game/downloaded" % system.getcwd().replace("\\", "/"))) or not checker.is_newest():
            print("[Updater]: Downloading Launcher")
            launcher = self.download(url, "Downloading Launcher")
        if not system.path.exists("%s/runtime/downloaded" % system.getcwd().replace("\\", "/")):
            print("[Updater]: Downloading Runtime")
            runtime = self.download("https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip",
                                    message="Downloading Runtime")
        if not system.path.exists("%s/runtime/tkinter_downloaded" % system.getcwd().replace("\\", "/")):
            print("[Updater]: Downloading Tkinter")
            tkinter = self.download("https://github.com/Qboi123/Tkinter-Python/archive/8.6.9.zip",
                                    message="Downloading Tkinter")
        if not system.path.exists("%s/runtime/pip_installed" % system.getcwd().replace("\\", "/")):
            print("[Updater]: Downloading Pip Installer")
            pip = self.download("https://bootstrap.pypa.io/get-pip.py", fp="get-pip.py",
                                message="Downloading Pip Installer")

        if (not system.path.exists("%s/game/downloaded" % system.getcwd().replace("\\", "/"))) or not checker.is_newest():
            print("[Updater]: Extracting Launcher")
            self.extract(launcher, "%s/game" % system.getcwd().replace("\\", "/"), "Extracting Launcher",
                         "Qplay-Launcher-",
                         v, sv, r, st, stb)
            with open("%s/game/downloaded" % system.getcwd().replace("\\", "/"), "w+") as file:
                file.write("True")
        if not system.path.exists("%s/runtime/downloaded" % system.getcwd().replace("\\", "/")):
            print("[Updater]: Extracting Runtime")
            self.extract(runtime, "%s/runtime" % system.getcwd().replace("\\", "/"), "Extracting Runtime")
            with open("%s/runtime/downloaded" % system.getcwd().replace("\\", "/"), "w+") as file:
                file.write("True")
        if not system.path.exists("%s/runtime/tkinter_downloaded" % system.getcwd().replace("\\", "/")):
            print("[Updater]: Extracing Tkinter")
            self.extract(tkinter, "%s/runtime" % system.getcwd().replace("\\", "/"), "Extracting Tkinter",
                         "Tkinter-Python-", 8, 6, 9, 'r')
            with open("%s/runtime/tkinter_downloaded" % system.getcwd().replace("\\", "/"), "w+") as file:
                file.write("True")
        if not system.path.exists("%s/runtime/pip_installed" % system.getcwd().replace("\\", "/")):
            import shutil
            load_ = wx.ProgressDialog("Please Wait...", "")
            load_.ShowModal()

            load_.SetTitle("Installing...")
            load_.SetRange(100)
            load_.Update(0, "Installing...\nInstalling Pip")

            runtime_dir = "%s/runtime" % system.getcwd().replace("\\", "/")

            print("[Updater]: Extracing from './runtime/python37.zip' to './runtime/Lib'")
            self.extract(runtime_dir + "/python37.zip", runtime_dir + "/Lib/",
                         "Extracing...\nExtracting Python Runtime "
                         "Library")

            exitcode = 1

            print("[Updater]: Executing Pip Installer")
            while exitcode == 1:
                exitcode = system.system("runtime\\python.exe temp/get-pip.py")
            print("Pip exited with code: %s" % exitcode)

            load_.Update(66, "Installing...\nInstalling Pip")

            self.replace_in_file("%s/runtime/python37._pth" % system.getcwd().replace("\\", "/"), "#import site", "import "
                                                                                                              "site")
            self.replace_in_file("%s/runtime/python37._pth" % system.getcwd().replace("\\", "/"), ".\n",
                                 "./Lib\n./DLLs")
            dlls = """runtime/_sqlite3.pyd
runtime/_lzma.pyd
runtime/_hashlib.pyd
runtime/_decimal.pyd
runtime/select.pyd
runtime/_socket.pyd
runtime/_elementtree.pyd
runtime/_multiprocessing.pyd
runtime/_overlapped.pyd
runtime/_asyncio.pyd
runtime/_msi.pyd
runtime/_queue.pyd
runtime/_ctypes.pyd
runtime/_bz2.pyd
runtime/libcrypto-1_1.dll
runtime/libssl-1_1.dll
runtime/pyexpat.pyd
runtime/_tkinter.pyd
runtime/_ssl.pyd
runtime/tk86t.dll
runtime/tcl86t.dll
runtime/unicodedata.pyd
runtime/winsound.pyd"""
            dlls = dlls.split("\n")
            if not system.path.exists("%s/runtime/DLLs/" % system.getcwd().replace("\\", "/")):
                system.makedirs("%s/runtime/DLLs/" % system.getcwd().replace("\\", "/"))
                load_.Update(70, "Installing...\nInstalling Pip")

            for file in dlls:
                dst = file.replace("runtime/", "runtime/DLLs/")
                shutil.copy(("%s/" + file) % system.getcwd().replace("\\", "/"),
                            ("%s/" + dst) % system.getcwd().replace("\\", "/"))
            load_.Update(81, "Installing...\nInstalling Pip")

            if not system.path.exists(runtime_dir + '/Lib/tkinter'):
                shutil.move(runtime_dir + "/tkinter", runtime_dir + "/Lib")
            # with open("%s/runtime/python37._pth" % os.getcwd().replace("\\", "/"), "r") as file:
            #     a = file.read()
            #     load.Update(77, "Installing...\nInstalling Pip")
            # with open("%s/runtime/python37._pth" % os.getcwd().replace("\\", "/"), "w") as file:
            #     a = a.replace("#import site", "import site")
            #     file.write(a)
            #     load.Update(88, "Installing...\nInstalling Pip")
            # with open("%s/runtime/pip_installed" % os.getcwd().replace("\\", "/"), "w+") as file:
            #     file.write("True")

            load_.Update(82, "Installing...\nInstalling Pip: \nExtracing Python Runtime Library")

            with open("%s/runtime/pip_installed" % system.getcwd().replace("\\", "/"), "w+") as file:
                file.write("True")
                file.close()

        if (not system.path.exists("%s/game/downloaded" % system.getcwd().replace("\\", "/")) or not (
                system.path.exists("%s/runtime/downloaded" % system.getcwd().replace("\\", "/")))) or (
                not system.path.exists("%s/runtime/tkinter_downloaded" % system.getcwd().replace("\\", "/"))) or (
                not system.path.exists("%s/runtime/pip_installed" % system.getcwd().replace("\\", "/"))):
            load_.Destroy()

        if (not system.path.exists("%s/game/patched" % system.getcwd().replace("\\", "/"))) or not checker.is_newest():
            print("[Updater]: Patching Launcher")
            add = """import sys, os
sys.path.append(os.getcwd().replace("\\\\", "/"))
"""
            with open("%s/game/launcher.pyw" % system.getcwd().replace("\\", "/"), "r") as file:
                file_launcher = file.read()
            with open("%s/game/launcher.pyw" % system.getcwd().replace("\\", "/"), "w+") as file:
                file.write(add + file_launcher)
            with open("%s/game/patched" % system.getcwd().replace("\\", "/"), "w+") as file:
                file.write("True")
                file.close()
        with open("%s/game/requirements.txt" % system.getcwd().replace("\\", "/"), "r") as file:
            print("[Updater]: Installing Libraries")
            self.install_libraries(file.read())
            file.close()
        with open("%s/runtime/packages_installed" % system.getcwd().replace("\\", "/"), "w+") as file:
            file.write("True")
            file.close()

        with open("%s/updates.xml" % system.getcwd().replace("\\", "/"), "w+") as file:
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
        import zipfile
        import shutil

        load_ = wx.ProgressDialog("Please Wait...", "")
        load_.ShowModal()

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
        load_.Update(0, "Extracing...\n" + message)

        zip_file = zipfile.ZipFile(file)
        if copy is not None:
            print("[Checking]:", folder == "Qplay-Launcher-")
            print("[Checking]:", folder)
            if folder == "Qplay-Launcher-":
                shutil.rmtree('%s/game' % system.getcwd().replace("\\", "/"), ignore_errors=True)
            load_.Update(1, "Extracing...\n" + message)
            zip_file.extractall("%s/temp" % system.getcwd().replace("\\", "/"))
            load_.Update(98, "Extracing...\n" + message)
            print(("%s/temp/" + folder + "%s") % (system.getcwd().replace("\\", "/"), copy), dir_)
            if folder == "Tkinter-Python-":
                for item in system.listdir(("%s/temp/" + folder + "%s") % (system.getcwd().replace("\\", "/"), copy)):
                    shutil.move(("%s/temp/" + folder + "%s/" + item) % (system.getcwd().replace("\\", "/"), copy),
                                dir_ + "/" + item)
            else:
                shutil.move(("%s/temp/" + folder + "%s") % (system.getcwd().replace("\\", "/"), copy), dir_)

            while not system.path.exists(dir_):
                time.sleep(1)
        else:
            if not system.path.exists(dir_):
                system.makedirs(dir_)
            load_.Update(99, "Extracing...\n" + message)
            zip_file.extractall(dir_)

        load_.Update(100, "Extracing...\n" + message)

    # noinspection PyProtectedMember
    @staticmethod
    def download(url, message="Downloading Launcher", fp=None):
        import random

        load_ = wx.ProgressDialog("Please Wait...", "")
        load_.ShowModal(True)

        load_.SetTitle("Downloading...")
        load_.SetRange(100)
        load_.Update(0, "Downloading...\n" + message)

        value = random.randint(0x100000000000, 0xffffffffffff)
        if fp is None:
            filepath = hex(value)[2:] + ".tmp"
        else:
            filepath = fp

        if not system.path.exists("%s/temp" % system.getcwd().replace("\\", "/")):
            system.makedirs("%s/temp" % system.getcwd().replace("\\", "/"))

        download = Download(url, "%s/temp/%s" % (system.getcwd().replace("\\", "/"), filepath))
        # Thread(None, download.download, "DownloadThread")

        load_.SetRange(download.file_total_bytes + 1)
        while not download.downloaded:
            # print("Downloaded: ", download.file_downloaded_bytes)
            # print("Total: ", download.file_total_bytes)
            try:
                load_.SetRange(download.file_total_bytes + 1)
                load_.Update(download.file_downloaded_bytes, "Downloading...\n" + message)
            except wx._core.wxAssertionError:
                pass

        # load.Destroy()

        return "%s/temp/%s" % (system.getcwd().replace("\\", "/"), filepath)

    @staticmethod
    def install_libraries(requirements: str):
        import subprocess

        req = requirements.replace("\n", ", ")

        requirements = requirements.replace("\n", " ")
        print("[Run-Pip]: Installing Packages: %s" % req)
        application = '"%s/runtime/python.exe"' % system.getcwd().replace("\\", "/")
        args = " -m pip install " + requirements.replace("\n", " ")
        cmd = application + args

        print("[Run-Pip]: %s" % cmd)

        process = system.system(cmd)
        print("[Run-Pip]: Process Returned: %s" % process)
        if process != 0:
            print('[Run-Pip]: Retrying with subprocess...')
            process = subprocess.call([application, "-m", "pip", "install", *requirements.split(" ")])
            while process is None:
                time.sleep(1)
            print("[Run-Pip]: Process Returned: %s" % process)

    @staticmethod
    def run():
        # import subprocess

        system.chdir("%s/game" % system.getcwd().replace("\\", "/"))

        import subprocess
        file = '%s/qbubbles.exe' % system.path.normpath(system.path.join(__file__, "..")).replace("\\", "/")
        # print('[Run]: "{file}" "{py}"'.format(file=file, py=py))
        cmd = '"{file}"'.format(file=file)

        print("[Run-Game]: %s" % cmd)

        process = system.system(cmd)
        print("[Run-Game]: Process Returned: %s" % process)
        if process != 0:
            print('[Run-Game]: Retrying with subprocess...')
            subprocess.call([file])
            while process is None:
                time.sleep(1)
            print("[Run-Game]: Process Returned: %s" % process)

        # print("[Run]: \"%s/../runtime/python.exe\" \"%s/launcher.pyw\"" % (
        #     os.getcwd().replace("\\", "/"), os.getcwd().replace("\\", "/")))
        #
        # subprocess.run(("%s/../runtime/python.exe"% os.getcwd().replace("\\", "/"),
        #                "%s/launcher.pyw\"" % os.getcwd().replace("\\", "/")), stderr=stderr, stdout=stdout)


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
            errstream = self.process.GetErrorStream()

            if stream.CanRead():
                text = stream.read()
                application.stdout.write(text)
            if stream.CanRead():
                stderr = errstream.read()
                application.stderr.write(stderr)

    def OnProcessEnded(self, evt):
        print('OnProcessEnded, pid:%s,  exitCode: %s\n' %
              (evt.GetPid(), evt.GetExitCode()))

        stream = self.process.GetInputStream()
        errstream = self.process.GetErrorStream()

        if stream.CanRead():
            text = stream.read()
            application.stdout.write(text)
        if stream.CanRead():
            stderr = errstream.read()
            application.stderr.write(stderr)

        self.process.Destroy()
        self.process = None
        system.kill(system.getpid(), 0)

    def ShutdownDemo(self):
        # Called when the demo application is switching to a new sample. Tell
        # the process to close (by closign its output stream) and then wait
        # for the termination signals to be received and processed.
        if self.process is not None:
            self.process.CloseOutput()
            wx.MilliSleep(250)
            wx.Yield()
            self.process = None


class Download:
    def __init__(self, url, fp):
        from threading import Thread
        self._url = url
        self._fp = fp
        self.file_total_bytes = 1
        self.file_downloaded_bytes = 0
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
            if system.path.exists(self._fp):
                system.remove(self._fp)
            meta = u.info()
            dat = meta["Content-Length"]
        self.file_total_bytes = int(dat)

        data_blocks = []
        total = 0

        # Thread(None, lambda: speed(), "SpeedThread").start()

        while True:
            block = u.read(1024)
            data_blocks.append(block)
            self.file_downloaded_bytes += len(block)
            _hash = ((60 * self.file_downloaded_bytes) // self.file_total_bytes)
            if not len(block):
                active = False
                break

            try:
                with open(self._fp, "ab+") as f:
                    f.write(block)
                    f.close()
            except FileNotFoundError:
                system.makedirs("%s/temp/" % system.getcwd().replace("\\", "/"))
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
        if not system.path.exists("logs"):
            system.makedirs("logs")

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
        a = self.std.read()
        self.fp = open(self.file, "a+")
        self.fp.write("[{time}] [In]: ".format(time=time.ctime(time.time())) + a)
        self.fp.close()


if __name__ == '__main__':
    startup = time.time()
    startup2 = time.ctime(startup).replace(" ", "-").replace(":", ".")

    if not system.path.exists("%s/logs" % system.getcwd().replace("\\", "/")):
        system.makedirs("%s/logs" % system.getcwd().replace("\\", "/"))

    if not system.path.exists("%s/errors" % system.getcwd().replace("\\", "/")):
        system.makedirs("%s/errors" % system.getcwd().replace("\\", "/"))

    log_file = time.strftime("%m-%d-%Y %H.%M.%S.log", time.gmtime(startup))

    # stderr = open(os.getcwd().replace("\\", "/") + "/logs/stderr-" + hex(int(startup))[2:]+".log", "w+")
    # stdout = open(os.getcwd().replace("\\", "/") + "/logs/stdout-" + hex(int(startup))[2:]+".log", "w+")
    stderr = Log(system.getcwd().replace("\\", "/") + "/errors/" + log_file, application.__stderr__,
                 "Err")
    stdout = Log(system.getcwd().replace("\\", "/") + "/logs/" + log_file, application.__stdout__)
    stdin = Log(system.getcwd().replace("\\", "/") + "/logs/" + log_file, application.__stdout__)
    application.stderr = stderr
    application.stdout = stdout
    application.stdin = stdin

    checker = Checker(state="r")
    print("[Updater]: hasInternet()=%s" % checker.has_internet())
    print("[Updater]: isNewest()=%s" % checker.is_newest())
    print("[Updater]: getUpdateURL()=%s" % checker.get_update_url())

    b = checker.newest.attrib

    if (not checker.is_newest()) or (not checker.has_internet()) or \
            ((not system.path.exists("%s/game/downloaded" % system.getcwd().replace("\\", "/")) or not (
                    system.path.exists("%s/runtime/downloaded" % system.getcwd().replace("\\", "/")))) or (
                     not system.path.exists("%s/runtime/tkinter_downloaded" % system.getcwd().replace("\\", "/"))) or (
                     not system.path.exists("%s/runtime/pip_installed" % system.getcwd().replace("\\", "/")))):
        app = wx.App()
        # root = wx.Frame()
        # root.Show(False)
        a = Updater(checker.get_update_url(), checker.get_xml(), b["version"], b["subversion"], b["release"],
                    b["state"],
                    b["statebuild"])
        app.Destroy()
        a.run()
    else:
        # noinspection PyTypeChecker
        Updater.run()
