#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from test.helper import with_service
import sys
import os
import signal
from gi.repository import GLib

from pass_secret_service import pass_secret_service


class TestCollection(unittest.TestCase):
    @patch('pass_secret_service.pass_secret_service.Service')
    @patch('pass_secret_service.pass_secret_service.GLib.MainLoop')
    @patch('pass_secret_service.pass_secret_service.GLib.unix_signal_add')
    @patch('sys.exit')
    @patch('sys.argv', ['pass_secret_service', '--path', os.environ['PASSWORD_STORE_DIR']])
    def test_command_line(self,
                          _exit,
                          _unix_signal_add,
                          _MainLoop,
                          _Service,
                          ):
        mainloop = Mock()
        _MainLoop.return_value = mainloop
        pass_secret_service.main()
        pass_secret_service.sigterm(mainloop)
        mainloop.quit.assert_called_once_with()
        # _Service.assert_called_once_with()
        _MainLoop.assert_called_once_with()
        _unix_signal_add.assert_called_once_with(GLib.PRIORITY_HIGH, signal.SIGTERM, pass_secret_service.sigterm, mainloop)
        _exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
