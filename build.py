import os
import shutil

from compiler import Compiler

if __name__ == '__main__':
    # Get main folder
    main_folder_ = os.getcwd()

    # # Compiler class
    # compiler = Compiler(
    #     exclude=[".idea", ".gitattributes", ".gitignore", "build.py", "README.md",
    #              "obj", "icon.png", ".git", "compiler.py", "dll", "game", "downloads", "out.png", "account.json",
    #              "launcher_profiles.json", "args.txt", "src-old", "icons", "requirements.txt", "updater.py"],
    #     icon=None, main_folder=os.path.join(os.getcwd(), "src"), main_file="main.py".format(os.sep),
    #     hidden_imports=["os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    #                     "pkg_resources.py2_warn"],
    #     log_level="INFO", app_name="qbubbles", clean=True, hide_console=False, one_file=False, uac_admin=False)
    #
    # compiler.reindex()
    #
    # # Get argument and command
    # args = compiler.get_args()
    # command = compiler.get_command(args)
    #
    # # Compile workspace
    # compiler.compile(command)
    #
    # # Compiler class
    # compiler = Compiler(
    #     exclude=[".idea", ".gitattributes", ".gitignore", "build.py", "README.md",
    #              "obj", "icon.png", ".git", "compiler.py", "dll", "game", "downloads", "out.png", "account.json",
    #              "launcher_profiles.json", "args.txt", "src-old", "icons", "requirements.txt", "updater.py"],
    #     icon=None, main_folder=os.path.join(os.getcwd(), "src"), main_file="updater.py",
    #     hidden_imports=["os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    #                     "pkg_resources.py2_warn"],
    #     log_level="INFO", clean=True, hide_console=False, one_file=False, uac_admin=False, )
    #
    # compiler.reindex()
    #
    # # Get argument and command
    # args = compiler.get_args()
    # command = compiler.get_command(args)
    #
    # # Compile workspace
    # compiler.compile(command)

    # Compiler class
    compiler = Compiler(
        exclude=[
            ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", "icon.png", ".git", "compiler.py",
            "dll", "game", "downloads", "out.png", "account.json", "launcher_profiles.json", "args.txt", "src-old",
            "icons", "requirements.txt", "updater.py"
        ],
        hidden_imports=[
            "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
            "pkg_resources.py2_warn"
        ],
        icon=os.path.join(os.getcwd(), "icon.ico"), main_folder=os.path.join(os.getcwd(), "srcJava"), main_file="main.py".format(os.sep),
        log_level="INFO", app_name="Bubble Blaster Launcher", clean=True, hide_console=True, one_file=False,
        uac_admin=False)

    compiler.reindex()

    # Get argument and command
    args = compiler.get_args()
    command = compiler.get_command(args)

    # Compile workspace
    compiler.compile(command)

    # # Compiler class
    # compiler = Compiler(
    #     exclude=[
    #         ".idea", ".gitattributes", ".gitignore", "build.py", "README.md", "obj", "icon.png", ".git", "compiler.py",
    #         "dll", "game", "downloads", "out.png", "account.json", "launcher_profiles.json", "args.txt", "src-old",
    #         "icons", "requirements.txt", "updater.py"
    #     ],
    #     hidden_imports=[
    #         "os", "tkinter", "tkinter.tix", "_tkinter", "_tkinter.tix", "tkinter.filedialog", "_io",
    #         "pkg_resources.py2_warn"
    #     ],
    #     icon=os.path.join(os.getcwd(), "icon.ico"), main_folder=os.path.join(os.getcwd(), "srcJava"), main_file="updater.py",
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
