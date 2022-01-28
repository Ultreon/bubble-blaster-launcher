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

import click
import lib

from compiler import Compiler

main_folder = os.getcwd()


@click.command()
@click.option('--project', default="*", help='Project to build.')
def build(project: str):
    """Simple program that greets NAME for a total of COUNT times."""

    # noinspection PyUnresolvedReferences
    import buildscript

    if project == "*":
        for project in lib.projects.all():
            os.chdir(main_folder)
            # os.chdir(os.path.join(main_folder, project.get_source_dir()))
            # Compiler class
            compiler = Compiler(
                exclude=project.exclude,
                hidden_imports=project.hidden_imports,
                icon=os.path.join(main_folder, "icon.ico"), main_folder=project.get_source_dir(),
                main_file="main.py".format(os.sep),
                log_level="INFO", app_name=project.exeName, clean=True, hide_console=project.hideConsole, one_file=project.oneFile,
                require_admin=False)
            compiler.automatic()
    else:
        project = lib.projects.get_by_name(project)

        os.chdir(main_folder)
        # os.chdir(os.path.join(main_folder, project.get_source_dir()))

        # Compiler class
        compiler = Compiler(
            exclude=project.exclude,
            hidden_imports=project.hidden_imports,
            icon=os.path.join(main_folder, "icon.ico"), main_folder=project.get_source_dir(),
            main_file="main.py".format(os.sep),
            log_level="INFO", app_name=project.exeName, clean=True, hide_console=project.hideConsole,
            one_file=project.oneFile,
            require_admin=False)
        compiler.automatic()


if __name__ == '__main__':
    build()

    # # Get main folder
    # main_folder_ = os.getcwd()
    #
    # # Compiler class
    # compiler = Compiler(
    #     exclude=[
    #         ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", "icon.png", ".git", "compiler.py",
    #         "dll", "game", "downloads", "out.png", "account.json", "launcher_profiles.json", "args.txt", "src-old",
    #         "requirements.txt", "main.py"
    #     ],
    #     hidden_imports=[
    #         "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    #         "pkg_resources.py2_warn"
    #     ],
    #     icon=os.path.join(os.getcwd(), "icon.ico"), main_folder=os.path.join(os.getcwd(), "srcJava"), main_file="main.py".format(os.sep),
    #     log_level="INFO", app_name="Launcher", clean=True, hide_console=False, one_file=True,
    #     uac_admin=False)
    #
    # compiler.reindex()
    #
    # # Get argument and command
    # args = compiler.get_args()
    # command = compiler.get_command(args)
    #
    # # Compile workspace
    # compiler.compile(command)

    # # Compiler class
    # compiler = Compiler(
    #     exclude=[
    #         ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", "icon.png", ".git", "compiler.py",
    #         "dll", "game", "downloads", "out.png", "account.json", "launcher_profiles.json", "args.txt", "src-old",
    #         "Icons", "requirements.txt", "main.py"
    #     ],
    #     hidden_imports=[
    #         "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    #         "pkg_resources.py2_warn"
    #     ],
    #     icon=os.path.join(os.getcwd(), "icon.ico"), main_folder=os.path.join(os.getcwd(), "srcJava"), main_file="main.py",
    #     log_level="INFO", app_name="Bubble Blaster Updater", clean=True, hide_console=False, one_file=False, uac_admin=False, )
    #
    # compiler.reindex()
    #
    # # Get argument and command
    # args = compiler.get_args()
    # command = compiler.get_command(args)
    #
    # # Compile workspace
    # compiler.compile(command)

    # for file in os.listdir("bin/updater"):
    #     if os.path.exists("bin/qbubbles/" + file):
    #         if os.path.isdir("bin/updater/" + file):
    #             shutil.rmtree("bin/updater/" + file)
    #         elif os.path.isfile("bin/updater/" + file):
    #             os.remove("bin/updater/" + file)
    #     else:
    #         os.renames("bin/updater/" + file, "bin/qbubbles/" + file)
    #
    # shutil.rmtree("bin/updater/")
