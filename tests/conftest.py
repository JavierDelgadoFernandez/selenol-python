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

"""Conftest module."""

import json
import logging
from threading import Thread

import pytest
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

from selenol_python.exceptions import SelenolWebSocketClosedException
from selenol_python.services import SelenolService


@pytest.fixture
def mock_connection():
    """Fixture for creating mock connections."""
    class MockConnection(object):
        """mock backend connection for logging messages."""

        def __init__(self):
            """Default constructor."""
            self.received = []
            self.to_be_sent = []
            self.closed = False

        def send(self, message):
            """Saves the message inside received array."""
            if self.closed:
                raise SelenolWebSocketClosedException()
            self.received.append(message)

        def recv(self):
            """Return an empty array."""
            if self.closed:
                raise SelenolWebSocketClosedException()
            try:
                return self.to_be_sent.pop()
            except IndexError:
                raise SelenolWebSocketClosedException()

        def close(self):
            """Simulate the connection close."""
            self.closed = True

    return MockConnection()


@pytest.fixture
def mock_session():
    """Fixture to create a mock session.

    Return the object passed to ident parameter inside the get function.
    """
    class MockSession(object):
        """mock session."""

        def query(self, entity):
            """Simulate the creation of a SQLAlchemhy query."""
            class Query(object):
                """Mock up for SQLAlchemy query."""
                def get(self, ident):
                    """Simulate the return of an object by id."""
                    return ident
            return Query()

    return MockSession()


@pytest.fixture
def mock_service(mock_connection, mock_session):
    """Fixture to create a mock SelenolService."""
    return SelenolService([], mock_connection, mock_session)


@pytest.yield_fixture
def ws_server():
    """WebSocket server creation fixture."""

    class WSHandler(tornado.websocket.WebSocketHandler):
        """Tornado WebSocket echo handler."""

        def open(self):
            """On connection open, send a simple message."""
            self.write_message(json.dumps({'test': 'open'}))

        def on_message(self, message):
            """On message, send back the same message."""
            self.write_message(message)

        def check_origin(self, origin):
            """Allow alternate origins."""
            return True

    application = tornado.web.Application([
        (r'/', WSHandler),
    ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(3000)

    yield Thread(target=tornado.ioloop.IOLoop.instance().start).start

    tornado.ioloop.IOLoop.instance().stop()
    http_server.stop()


@pytest.fixture
def mock_message():
    """Example of request coming from the backend."""
    return {
        'request_id': 1,
        'content': {
            'session': {
                'keys': 'values',
            },
            'content': {
                'keyc': 'valuec',
            },
        },
    }


@pytest.fixture
def mock_logging():
    """Create a mock logging for testing purposes."""
    class ListHandler(logging.Handler):
        """List handler for logging."""

        def __init__(self, log_level=logging.INFO):
            """Default constructor.

            :param log_level: Log level.
            """
            super(ListHandler, self).__init__()
            self.level = log_level
            self.records = []
            self.filters = []
            self.lock = None

        def emit(self, record):
            """Store an event inside the records list.

            :param record: Record to be stored.
            """
            self.records.append(record)

    list_handler = ListHandler()
    logging.getLogger().addHandler(list_handler)
    return list_handler
