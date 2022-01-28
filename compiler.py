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
import shlex
import shutil
import traceback

import sys
from typing import MutableSequence, Tuple, Optional


class CompilerError(BaseException):
    pass


# noinspection PyUnusedClass
class Compiler(object):
    """
    @author: Qboi123
    @version: 2.0.0
    """

    def __init__(self, exclude: MutableSequence[str], icon: Optional[str], main_folder: str, main_file: str,
                 hidden_imports: MutableSequence[str], dlls: MutableSequence[str] = None, one_file=False,
                 hide_console=False, fix_recursion_limit=True, upx_dir: str = None, log_level: str = "INFO",
                 app_name: str = "", extra_binaries: MutableSequence[Tuple[str, str]] = None,
                 import_paths: MutableSequence[str] = None, add_hooks_dirs: MutableSequence[str] = None,
                 runtime_hooks: MutableSequence[str] = None, exclude_modules: MutableSequence[str] = None,
                 key: str = None, debug: str = None, no_unicode=False, clean=False, apply_symbol_table=False,
                 no_upx=False, version_file: str = None, manifest_file: str = None, require_admin=False,
                 enable_remote=False,
                 win_private_assemblies=False, win_no_prefer_redirects=False, osx_bundle_identifier: str = None,
                 runtime_tmpdir: str = "", bootloader_ignore_signals=False, *additional_args):
        """
        Compiler class, compiling python workspace.
        @param exclude: files to exclude in the build.
        @param icon: icon for the exe.
        @param main_folder: the main source code folder.
        @param main_file: the main file.
        @param hidden_imports: hidden imports to include.
        @param dlls: DLL files to include.
        @param one_file: enable one-file mode.
        @param hide_console: hide console when running exe.
        @param fix_recursion_limit: fix the recursion limit.
        @param upx_dir: UPX directory.
        @param log_level: the log level.
        @param app_name: the app's name.
        @param extra_binaries: extra binaries to include.
        @param import_paths: ???
        @param add_hooks_dirs: ???
        @param runtime_hooks: ???
        @param exclude_modules: exclude some modules.
        @param key:
        @param debug: enable debugging mode.
        @param no_unicode:
        @param clean: clean build.
        @param apply_symbol_table:
        @param no_upx: disable UPX.
        @param version_file: path to exe version file.
        @param manifest_file: path to exe manifest.
        @param require_admin: let built exe require UAC Administrator to run.
        @param enable_remote:
        @param win_private_assemblies:
        @param win_no_prefer_redirects:
        @param osx_bundle_identifier:
        @param runtime_tmpdir: runtime temp directory. %userprofile%\\AppData\\local\\Temp for Windows.
        @param bootloader_ignore_signals:
        @param additional_args: additional arguments.
        """
        if hidden_imports is None:
            hidden_imports = list()

        exclude.append("obj")
        exclude.append("build")
        exclude.append("bin")
        exclude.append(".gitignore")
        exclude.append(".gitattributes")
        exclude.append(".git")
        exclude.append(".idea")

        # One File
        self.oneFile = one_file

        # Hide the console
        self.hideConsole = hide_console

        # Internal options
        self.mainFolder = main_folder
        self.mainFile = main_file
        self.mainContents = os.listdir(main_folder)
        self.dllFiles = dlls
        self.exclude = exclude
        self.icon = icon
        self.allFiles = []
        self.rootFiles = []

        # General Options
        self.upxDirectory = upx_dir
        self.noUnicode = no_unicode
        self.cleanCompile = clean
        self.logLevel = log_level
        self.appName = app_name

        # What to bundle, and where to search
        self.extraBinaries = extra_binaries
        self.importPaths = import_paths
        self.hiddenImports = hidden_imports
        self.additionalHooksDirs = add_hooks_dirs
        self.runtimeHooks = runtime_hooks
        self.excludeModules = exclude_modules
        self.key = key

        # How to generate
        self.debug = debug
        self.applySymbolTable = apply_symbol_table
        self.noUPX = no_upx

        # Windows specific options
        self.versionFile = version_file
        self.manifestFile = manifest_file
        self.requireAdmin = require_admin
        self.enableRemoteControl = enable_remote

        # Windows Side-by-side Assembly searching options
        self.privateAssemblies = win_private_assemblies
        self.noPreferRedirects = win_no_prefer_redirects

        # Mac OS X specific options
        self.osxBundleIdentifier = osx_bundle_identifier

        # Rarely used special options
        self.runtimeTempDir = runtime_tmpdir
        self.bootloaderIgnoreSignals = bootloader_ignore_signals

        # Manual Command Entry
        self.additionalArgs = additional_args

        if fix_recursion_limit:
            sys.setrecursionlimit(5000)

        self.check()

    def check(self):
        """
        Check for errors
        :return:
        """
        if self.icon in self.exclude:
            raise CompilerError("Can't exclude icon!")

    def automatic(self):
        """
        Automatic mode
        :return:
        """
        self.reindex()
        args_list = self.get_args()
        command = self.get_command(args_list)

        self.compile(command)

    def get_command(self, args_list):
        """
        Get command for PyInstaller
        :param args_list:
        :return:
        """
        args = self.parse_arg_list(args_list)
        return "pyinstaller " + args

    # noinspection PyBroadException
    def compile(self, command):
        """
        Compile the workspace, with the given command for PyInstaller
        :param command:
        :return:
        """
        from PyInstaller import __main__ as pyi
        # auto_py2exe.__main__.temporary_directory = self.join_path(self.mainFolder, "obj")

        build_dir = self.join_path(self.mainFolder, "../build")
        # output = self.join_path(os.path.normpath(os.path.join(self.mainFolder, "..")), "build/exe")

        os.makedirs(build_dir, exist_ok=True)

        # Notify the user of the workspace and setup building to it
        print(f"Started build of the source code at {self.mainFolder}")
        print(f"Building in the current instances temporary directory at {build_dir}")
        print("To get a new temporary directory, restart this application")
        dist_path = os.path.join(build_dir, 'dist')
        build_path = os.path.join(build_dir, 'build')
        spec_path = os.path.join(build_dir, 'spec')

        for file in self.rootFiles:
            shutil.copy(file, spec_path)

        extra_args = ['--distpath', dist_path] + ['--workpath', build_path] + ['--specpath', spec_path]

        # Run PyInstaller
        failed: bool
        sys.argv = shlex.split(command) + extra_args  # Put command into sys.argv and extra args
        try:
            print(f"Executing: {command}")
            pyi.run()  # Execute PyInstaller
            failed = False
        except Exception as e:
            print("An error occurred, traceback follows:", file=sys.stderr)
            traceback.print_exception(e.__class__, e, e.__traceback__)
            failed = True

        # Move project if there was no failure
        if failed:
            print("Compiling failed, check log for more information.", file=sys.stderr)
        else:
            print("Successfully built project.")
            # output_directory = os.path.abspath(output)  # Use absolute directories
            # print("Moving project to: {0}".format(output_directory))
            # try:
            #     self.move_project(dist_path, output_directory)
            # except:
            #     print("Failed to move project, traceback follows:", file=sys.stderr)
            #     print(traceback.format_exc())

        print("Complete.")

    @staticmethod
    def move_project(src, dst):
        """
        Move the project from <src-old> to <dst>. Mostly common it moves the project to "./bin"
        :param src:
        :param dst:
        :return:
        """
        """ Move the output package to the desired path (default is output/ - set in script.js) """
        # Make sure the destination exists
        if not os.path.exists(dst):
            os.makedirs(dst)

        # Move all files/folders in dist/
        for file_or_folder in os.listdir(src):
            _dst = os.path.join(dst, file_or_folder)
            # If this already exists in the destination, delete it
            if os.path.exists(_dst):
                if os.path.isfile(_dst):
                    os.remove(_dst)
                else:
                    shutil.rmtree(_dst)
            # Move file
            shutil.move(os.path.join(src, file_or_folder), dst)

    @staticmethod
    def join_path(path, *paths):
        """
        Joins path using the "os" package, then replaces every "\" with "/"
        :param path:
        :param paths:
        :return:
        """
        return os.path.join(path, *paths).replace("\\", "/")

    def _reindex_relpath(self, folder):
        """
        Reindex the relative path to <folder>
        @param folder:
        @return:
        """
        for export_path in os.listdir(self.join_path(self.mainFolder, folder)):
            export_path = self.join_path(folder, export_path)
            path = self.join_path(self.mainFolder, export_path)
            if export_path in self.exclude:
                continue
            if export_path not in ["bin", "obj", "__pycache__", self.mainFile] and not export_path.endswith(
                    "__pycache__"):
                if os.path.split(export_path)[-1] not in ["__pycache__"]:
                    if os.path.isfile(path):
                        # print("Indexed File: (%s, %s)" % (path, os.path.join(*os.path.split(export_path)[:-1])))
                        self.allFiles.append((export_path, os.path.join(*os.path.split(export_path)[:-1])))
                    if os.path.isdir(path):
                        # print("Indexed Folder: %s" % export_path)
                        self._reindex_relpath(export_path)

    def reindex(self):
        """
        Reindex all files in the workspace
        :return:
        """
        self.allFiles = []
        for export_path in self.mainContents:
            path = self.join_path(self.mainFolder, export_path)
            if export_path in self.exclude:
                print(export_path)
                continue
            if export_path not in ["bin", "obj", "__pycache__", self.mainFile] and not export_path.endswith(
                    "__pycache__"):
                if os.path.isfile(path):
                    # print("Indexed File: (%s, %s)" % (path, "."))
                    self.allFiles.append((export_path, "."))
                if os.path.isdir(path):
                    # print("Indexed Folder: %s" % export_path)
                    self._reindex_relpath(export_path)
                self.rootFiles.append(path)

    def get_args(self) -> list:
        """
        Get arguments for the PyInstaller command
        :return:
        """
        args = ["-y"]
        if self.oneFile:
            args.append("-F")
        if self.hideConsole:
            args.append("-w")
        if self.icon:
            args.append("-i \"%s\"" % self.join_path(self.mainFolder, self.icon))
        # print("All Files: %s" % self.allFiles)
        for file_location, exported_location in self.allFiles:
            args.append("--add-data \"%s\";\"%s\"" % (file_location.replace("\\", "/"), exported_location))
            # print("--add-data \"%s\";\"%s\"" % (file_location.replace("\\", "/"), exported_location))
        if self.dllFiles:
            for file in self.dllFiles:
                args.append("--add-data \"%s\";\".\"" % self.join_path(self.mainFolder, file.replace("\\", "/")))
        if self.upxDirectory:
            args.append("--upx-dir \"%s\"" % self.upxDirectory)
        if self.noUnicode:
            args.append("-a")
        if self.cleanCompile:
            args.append("--clean")
        if self.logLevel:
            args.append("--log-level %s" % self.logLevel.upper())
        if self.appName:
            args.append("-n \"%s\"" % self.appName)
        if self.extraBinaries:
            for src, dist in self.extraBinaries:
                args.append("--add-binary \"%s\";\"%s\"" % (src, dist))
        if self.importPaths:
            for path in self.importPaths:
                args.append("-p %s" % path)
        if self.hiddenImports:
            for hidden_import in self.hiddenImports:
                args.append("--hidden-import \"%s\"" % hidden_import)
        if self.additionalHooksDirs:
            for hooks_dir in self.additionalHooksDirs:
                args.append("--additional-hooks-dir \"%s\"" % hooks_dir)
        if self.runtimeHooks:
            for runtime_hook in self.runtimeHooks:
                args.append("--runtime-hook \"%s\"" % runtime_hook)
        if self.excludeModules:
            for exclude in self.excludeModules:
                args.append("--exclude-module \"%s\"" % exclude)
        if self.key:
            args.append("--key \"%s\"" % self.key)
        if self.debug:
            args.append("--debug \"%s\"" % self.debug)
        if self.applySymbolTable:
            args.append("-s")
        if self.noUPX:
            args.append("--noupx")
        if self.versionFile:
            args.append("--version-file \"%s\"" % self.versionFile)
        if self.manifestFile:
            args.append("-m \"%s\"" % self.manifestFile)
        if self.requireAdmin:
            args.append("--uac-admin")
        if self.enableRemoteControl:
            args.append("--uac-uiaccess")
        if self.privateAssemblies:
            args.append("--win-private-assemblies")
        if self.noPreferRedirects:
            args.append("--win-no-prefer-redirects")
        if self.osxBundleIdentifier:
            args.append("--osx-bundle-identifier \"%s\"" % self.osxBundleIdentifier)
        if self.runtimeTempDir:
            args.append("--runtime-tmpdir \"%s\"" % self.runtimeTempDir)
        if self.bootloaderIgnoreSignals:
            args.append("--bootloader-ignore-signals")
        args.append(" \"%s\"" % self.join_path(self.mainFolder, self.mainFile))

        return args

    @staticmethod
    def parse_arg_list(args_list):
        """
        Parses a list of arguments into a string
        :param args_list:
        :return:
        """
        args = args_list[0]

        if len(args_list) > 1:
            for arg in args_list:
                args += " " + arg

        return args
