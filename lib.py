"""
@contact Qboi123#5895 on discord.
@since Jan. 24th 2022
@license GNU General Public License v3
@copyright Licensed under GPLv3.
@version 1.0.0
@organization: Ultreon Team
@author: Qboi123
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

from typing import List, Optional, Dict, ValuesView


class Project:
    """
    @author: Qboi123
    """

    def __init__(self, name: str, exclude: Optional[List[str]] = None, hidden_imports=None, hide_console=True,
                 one_file=False, exe_name: Optional[str] = None):
        """
        Project initializer.

        @param name: name of the project.
        @param exclude: excluded files in the project source.
        @param hidden_imports: hidden imports to include.
        @param hide_console: hide the console in the built exe.
        @param one_file: make the exe in one file instead of with files next to it.
        @author: Qboi123
        """

        if exe_name is None:
            exe_name = name
        self.exeName = exe_name
        self.oneFile = one_file
        self.hideConsole = hide_console
        if hidden_imports is None:
            hidden_imports = []
        self.hidden_imports = hidden_imports
        if exclude is None:
            exclude = []
        self.exclude = exclude
        self.name = name

    def get_source_dir(self) -> str:
        """
        @author: Qboi123
        @return: the project source code path.
        """

        import os
        return os.path.join(self.name, "src/")


class Projects:
    """
    @author: Qboi123
    """

    def __init__(self):
        """
        @author Qboi123
        """

        self.__projects: Dict[str, Project] = {}

    def register(self, project: Project):
        """
        Register a project in the build system.

        @raise NameError if project with that name already exists
        @param project: project to register.
        @author: Qboi123
        @return:
        """

        if project.name in self.__projects:
            raise NameError(f"Project with that name already exists: {project.name}")

        self.__projects[project.name] = project

    def all(self) -> ValuesView[Project]:
        return self.__projects.values()

    def get_by_name(self, name: str) -> Project:
        return self.__projects[name]


projects: Projects = Projects()
