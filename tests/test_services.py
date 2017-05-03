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

"""Test services module."""

from pytest import raises

from selenol_python.exceptions import (SelenolException,
                                       SelenolWebSocketClosedException)
from selenol_python.services import SelenolClient, SelenolService


def test_selenol_client_default(mock_connection, mock_session):
    """Test the lifecycle of the connection with the default client."""
    mock_connection.to_be_sent.append('test')
    selenol_client = SelenolClient(mock_connection, mock_session)
    with raises(NotImplementedError):
        selenol_client.run()


def test_selenol_client_custom(mock_connection, mock_session):
    """Test the lifecycle of the connection with a custom client."""
    executed = []

    class SelenolClientImplementation(SelenolClient):
        """mock implemantation to test execution."""

        def on_open(self):
            """On open log `open` message."""
            executed.append('open')

        def on_closed(self, code, reason):
            """On close log `close` message."""
            executed.append('closed')

        def on_message(self, message):
            """On message log `request` message."""
            executed.append('message')
            return "test"

    mock_connection.to_be_sent.append('test')
    selenol_client = SelenolClientImplementation(mock_connection, mock_session)

    try:
        selenol_client.run()
        assert False, "The connection has to be closed."
    except SelenolWebSocketClosedException:
        assert 'open' in executed
        assert 'closed' in executed
        assert 'message' in executed
        assert len(mock_connection.received) == 1
        assert mock_connection.received[0] == 'test'


def test_selenol_client_send(mock_connection, mock_session):
    """Test the send method of a client."""
    selenol_client = SelenolClient(mock_connection, mock_session)

    reason = ['test', 'reason']
    content = {'keyc': 'valuec'}
    selenol_client.send(reason, content)

    assert len(mock_connection.received) == 1
    assert mock_connection.received[0]['reason'] == reason
    assert mock_connection.received[0]['content'] == content


def test_selenol_client_notify(mock_connection, mock_session):
    """Test the notify method of a client."""
    selenol_client = SelenolClient(mock_connection, mock_session)

    topic = ['test', 'topic']
    content = {'keyc': 'valuec'}
    selenol_client.notify(topic, content)

    assert len(mock_connection.received) == 1
    assert mock_connection.received[0]['reason'] == ['request', 'notification']
    assert mock_connection.received[0]['content']['topic'] == topic
    assert mock_connection.received[0]['content']['content'] == content


def test_selenol_service_default(mock_connection, mock_session,
                                 mock_message):
    """Test the lifecycle of the connection with the default service."""
    message = mock_message
    message['reason'] = ['selenol', 'request']
    mock_connection.to_be_sent.append(message)
    selenol_service = SelenolService(['reason', 'a'], mock_connection,
                                     mock_session)
    with raises(SelenolWebSocketClosedException):
        selenol_service.run()


def test_selenol_service_custom(mock_connection, mock_session, mock_message):
    """Test the lifecycle of the connection with a custom service."""
    executed = []

    class SelenolServiceImplementation(SelenolService):
        """mock implemantation to test execution."""

        def on_open(self):
            """On open log `open` message."""
            executed.append('open')

        def on_closed(self, code, reason):
            """On close log `close` message."""
            executed.append('closed')

        def on_request(self, message):
            """On message log `request` message."""
            executed.append('request')
            return "test"

    message = mock_message
    message['reason'] = ['selenol', 'request']
    mock_connection.to_be_sent.append(message)
    selenol_service = SelenolServiceImplementation(['reason', 'a'],
                                                   mock_connection,
                                                   mock_session)

    try:
        selenol_service.run()
        assert False, "The connection has to be closed."
    except SelenolWebSocketClosedException:
        assert 'open' in executed
        assert 'closed' in executed
        assert 'request' in executed
        assert len(mock_connection.received) == 2
        assert mock_connection.received[1]['reason'] == ['request', 'result']
        assert mock_connection.received[1]['content']['content'] == 'test'


def test_selenol_service_selenol_exception(mock_connection, mock_session,
                                           mock_message, mock_logging):
    """Test the behavior during a SelenolException of a service."""
    exception_message = 'This is the test message for the exception'

    class SelenolServiceImplementation(SelenolService):
        """mock implemantation to test execution."""

        def on_request(self, message):
            """On message log `request` message."""
            raise SelenolException(exception_message)

    message = mock_message
    message['reason'] = ['selenol', 'request']
    mock_connection.to_be_sent.append(message)
    selenol_service = SelenolServiceImplementation(['reason', 'a'],
                                                   mock_connection,
                                                   mock_session)
    assert len(mock_logging.records) == 0
    try:
        selenol_service.run()
        assert False, "The connection has to be closed."
    except SelenolWebSocketClosedException:
        assert len(mock_connection.received) == 2
        assert mock_connection.received[1][
            'reason'] == ['request', 'exception']
        assert mock_connection.received[1][
            'content']['message'] == exception_message
        assert len(mock_logging.records) == 1


def test_selenol_service_generic_exception(mock_connection, mock_session,
                                           mock_message, mock_logging):
    """Test the behavior during a generic exception of a service."""
    class SelenolServiceImplementation(SelenolService):
        """mock implemantation to test execution."""

        def on_request(self, message):
            """On message log `request` message."""
            raise ArithmeticError()

    message = mock_message
    message['reason'] = ['selenol', 'request']
    mock_connection.to_be_sent.append(message)
    selenol_service = SelenolServiceImplementation(['reason', 'a'],
                                                   mock_connection,
                                                   mock_session)
    assert len(mock_logging.records) == 0
    try:
        selenol_service.run()
        assert False, "The connection has to be closed."
    except SelenolWebSocketClosedException:
        assert len(mock_connection.received) == 2
        assert mock_connection.received[1][
            'reason'] == ['request', 'exception']
        assert mock_connection.received[1][
            'content']['message'] == 'Not a Selenol exception'
        assert len(mock_logging.records) == 1


def test_selenol_service_metadata(mock_connection, mock_session):
    """Test the metadata method of a service."""
    selenol_service = SelenolService(['reason', 'a'], mock_connection,
                                     mock_session)

    assert len(mock_connection.received) == 1

    request_id = 7
    metadata = {
        'keym': 'valuem',
    }
    selenol_service.metadata(request_id, metadata)

    assert len(mock_connection.received) == 2
    assert mock_connection.received[1]['reason'] == ['request', 'metadata']
    assert mock_connection.received[1]['request_id'] == request_id
    assert mock_connection.received[1]['content'] == metadata


def test_selenol_service_event(mock_connection, mock_session):
    """Test the metadata method of a service."""
    selenol_service = SelenolService(['reason', 'a'], mock_connection,
                                     mock_session)

    assert len(mock_connection.received) == 1

    request_id = 7
    trigger = 'disconnection'
    event = ['test', 'event']
    message = {
        'keye': 'valuee',
    }
    selenol_service.event(request_id, trigger, event, message)

    assert len(mock_connection.received) == 2
    assert mock_connection.received[1]['reason'] == ['request', 'event']
    assert mock_connection.received[1]['request_id'] == request_id
    assert mock_connection.received[1]['content']['trigger'] == trigger
    assert mock_connection.received[1]['content']['message']['reason'] == event
    assert mock_connection.received[1][
        'content']['message']['content'] == message


def test_selenol_service_send(mock_connection, mock_session):
    """Test the send method of a service."""
    selenol_service = SelenolService(['reason', 'a'], mock_connection,
                                     mock_session)

    assert len(mock_connection.received) == 1

    reason = ['test', 'reason']
    content = {'keyc': 'valuec'}
    selenol_service.send(reason, content)

    assert len(mock_connection.received) == 2
    assert 'request_id' in mock_connection.received[1]['content']
    assert mock_connection.received[1]['reason'] == ['request', 'send']
    assert mock_connection.received[1]['content']['content'] == content
