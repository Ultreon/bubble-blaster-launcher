"""
@copyright: Licensed under GPLv3
@license: GNU General Public License v3.0
@organization: Ultreon Team
@author: Qboi123
@version: 1.0.4
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

from lib import *

debug: bool = False

projects.register(Project("launcher", exclude=[
    ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", ".git", "compiler.py",
    "requirements.txt"
], hidden_imports=[
    "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    "pkg_resources.py2_warn"
], hide_console=not debug, one_file=debug, exe_name="Launcher"))
projects.register(Project("updater", exclude=[
    ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", ".git", "compiler.py",
    "requirements.txt"
], hidden_imports=[
    "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    "pkg_resources.py2_warn", "wx._core"
], hide_console=not debug, one_file=True, exe_name="Updater"))
projects.register(Project("installer", exclude=[
    ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", ".git", "compiler.py",
    "requirements.txt"
], hidden_imports=[
    "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    "pkg_resources.py2_warn", "wx._core"
], hide_console=not debug, one_file=True, exe_name="Bubble Blaster Installer"))
projects.register(Project("legacy_launcher", exclude=[
    ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", ".git", "compiler.py",
    "requirements.txt"
], hidden_imports=[
    "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    "pkg_resources.py2_warn", "wx._core"
], hide_console=not debug, one_file=False, exe_name="Bubble Blaster Launcher"))
