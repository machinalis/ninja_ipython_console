# -*- coding: UTF-8 -*-
"""
    Copyright 2013 Machinalis <info@machinalis.com>

    This file is part of ninja ipython plugin.

    ninja ipython plugin is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ninja ipython plugin is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ninja ipython plugin.  If not, see <http://www.gnu.org/licenses/>.
"""


from ninja_ide.core import plugin

import atexit

from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager

from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.main_panel import itab_item
from ninja_ide.resources import IMAGES
from PyQt4.QtGui import QWidget


class INinjaConsole(plugin.Plugin):
    def initialize(self):
        # Init your plugin
        self.misc_s = self.locator.get_service('misc')
        explorer_container = self.locator.get_service('explorer')
        tree = explorer_container.get_tree_projects()


        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel = kernel_manager.kernel
        kernel.gui = 'qt4'

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()

        self.ipython_console = RichIPythonWidget()
        self.ipython_console.kernel_manager = kernel_manager
        self.ipython_console.kernel_client = kernel_client
        self.ipython_console.exit_requested.connect(stop)
        self.ipython_console.show()


        self.misc_s.add_widget(self.ipython_console, IMAGES["console"],
                                "IPython console")
        addp = SIGNAL("addProjectToConsole(QString)")
        delp = SIGNAL("removeProjectFromConsole(QString)")
        self.connect(tree, addp, self._add_project)
        self.connect(tree, delp, self._del_project)

    def _add_project(self, project_path):
        self.ipython_console.execute("import sys; sys.path += ['%s']" %
                                    project_path)

    def _del_project(self, project_path):
        """This is ugly, but I was in a hurry and copied form console
        widget"""
        self.ipython_console.execute("import sys; "
            "sys.path = [path for path in sys.path "
            "if path != '%s']" % project_path)

    def finish(self):
        # Shutdown your plugin
        pass

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        pass
