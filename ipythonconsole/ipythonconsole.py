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

try:
    from IPython.zmq.ipkernel import IPKernelApp
except ImportError:
    from IPython.kernel.zmq.kernelapp import IPKernelApp
from IPython.lib.kernel import find_connection_file
from IPython.frontend.qt.kernelmanager import QtKernelManager
from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.utils.traitlets import TraitError
from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.main_panel import itab_item
from ninja_ide.resources import IMAGES
from PyQt4.QtGui import QWidget


class IPythonWidget(QWidget, itab_item.ITabItem):

    def __init__(self):
        super(IPythonWidget, self).__init__()


def event_loop(kernel):
    kernel.timer = QtCore.QTimer()
    kernel.timer.timeout.connect(kernel.do_one_iteration)
    kernel.timer.start(1000 * kernel._poll_interval)


def default_kernel_app():
    app = IPKernelApp.instance()
    app.initialize(['python', '--pylab=qt'])
    app.kernel.eventloop = event_loop
    return app


def default_manager(kernel):
    connection_file = find_connection_file(kernel.connection_file)
    manager = QtKernelManager(connection_file=connection_file)
    manager.load_connection_file()
    manager.start_channels()
    atexit.register(manager.cleanup_connection_file)
    return manager


def console_widget(manager):
    try:  # Ipython v0.13
        widget = RichIPythonWidget(gui_completion='droplist')
    except TraitError:  # IPython v0.12
        widget = RichIPythonWidget(gui_completion=True)
    widget.kernel_manager = manager
    return widget


def terminal_widget(**kwargs):
    kernel_app = default_kernel_app()
    manager = default_manager(kernel_app)
    widget = console_widget(manager)

    #update namespace
    kernel_app.shell.user_ns.update(kwargs)

    kernel_app.start()
    return widget


class INinjaConsole(plugin.Plugin):
    def initialize(self):
        # Init your plugin
        self.misc_s = self.locator.get_service('misc')
        explorer_container = self.locator.get_service('explorer')
        tree = explorer_container.get_tree_projects()
        self.ipython_console = terminal_widget()
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
