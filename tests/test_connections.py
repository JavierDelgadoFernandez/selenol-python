# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test connections module."""

from threading import Thread
from time import sleep

from pytest import raises

from selenol_python.connections import SelenolWSConnection
from selenol_python.exceptions import SelenolWebSocketClosedException


def test_ws_connection_server(ws_server):
    """Open the simplest connection to a WS server."""
    ws_server()
    selenol_connection = SelenolWSConnection('ws://localhost:3000')
    assert selenol_connection.recv() == {'test': 'open'}


def test_ws_connection_server_delay(ws_server):
    """Open a connection to a WS server that takes some time to start."""
    def sleeping_server():
        """Wait two seconds to start the WebSocket server."""
        sleep(2)
        ws_server()
    Thread(target=sleeping_server).start()

    selenol_connection = SelenolWSConnection('ws://localhost:3000')
    assert selenol_connection.recv() == {'test': 'open'}


def test_ws_receive_no_connection(ws_server):
    """Expected a defined exception when the connection has been closed."""
    ws_server()
    selenol_connection = SelenolWSConnection('ws://localhost:3000')
    selenol_connection.close()
    with raises(SelenolWebSocketClosedException):
        selenol_connection.recv()


def test_ws_connection_send_receive(ws_server):
    """Test send and receive typical execution."""
    ws_server()
    selenol_connection = SelenolWSConnection('ws://localhost:3000')
    assert selenol_connection.recv() == {'test': 'open'}
    document = {'doc': 'test'}
    selenol_connection.send(document)
    assert selenol_connection.recv() == document


def test_ws_send_no_connection(ws_server):
    """Expected a defined exception when sending on closed connection."""
    ws_server()
    selenol_connection = SelenolWSConnection('ws://localhost:3000')
    selenol_connection.close()
    with raises(SelenolWebSocketClosedException):
        selenol_connection.send({'doc': 'test'})
