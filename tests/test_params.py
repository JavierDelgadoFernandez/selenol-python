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

"""Test params module."""

from pytest import raises

from selenol_python.data_structures import SelenolMessage
from selenol_python.exceptions import (SelenolInvalidArgumentException,
                                       SelenolMissingArgumentException,
                                       SelenolMissingSessionArgumentException)
from selenol_python.params import (_get_value, get_object_from_content,
                                   get_object_from_session, get_request_id,
                                   get_value_from_content,
                                   get_value_from_session, selenol_params)


def test_get_object_from_content(mock_service, mock_message):
    """Test get_object_from_content method."""
    selenol_message = SelenolMessage(mock_message)

    # Value exists.
    mock_message['content']['content']['foo'] = 43
    assert get_object_from_content(int, ['foo'])(
        mock_service, selenol_message) == 43

    # Value does not exist in the database
    try:
        mock_message['content']['content']['foo'] = False
        get_object_from_content(int, ['foo'])(mock_service, selenol_message)
        assert False, 'The object doesnt exist, it throw an exception'
    except SelenolInvalidArgumentException as ex:
        assert ex.argument == ['foo']
        assert not ex.value


def test_get_object_from_session(mock_service, mock_message):
    """Test get_object_from_content method."""
    selenol_message = SelenolMessage(mock_message)

    # Value exists.
    mock_message['content']['session']['foo'] = 43
    assert get_object_from_session(int, ['foo'])(
        mock_service, selenol_message) == 43

    # Value does not exist in the database
    try:
        mock_message['content']['session']['foo'] = False
        get_object_from_session(int, ['foo'])(mock_service, selenol_message)
        assert False, 'The object doesnt exist, it throw an exception'
    except SelenolInvalidArgumentException as ex:
        assert ex.argument == ['foo']
        assert not ex.value


def test_get_request_id(mock_service, mock_message):
    """Test get_request_id method."""
    # request_id does not exist.
    with raises(KeyError):
        del mock_message['request_id']
        selenol_message = SelenolMessage(mock_message)
        get_request_id()(mock_service, selenol_message)

    # request_id exists.
    request_id = 43
    mock_message['request_id'] = request_id
    selenol_message = SelenolMessage(mock_message)
    assert get_request_id()(mock_service, selenol_message) == request_id


def test_get_value(mock_message):
    """Test get_value method."""
    selenol_message = SelenolMessage(mock_message)

    # Value exists.
    assert _get_value(selenol_message.content, ['keyc']) == 'valuec'

    # Value does not exist.
    try:
        _get_value(selenol_message.content, ['no'])
        assert False, 'The value does not exist.'
    except SelenolMissingArgumentException as ex:
        assert ex.argument == 'no'

    # Empty path.
    with raises(KeyError):
        _get_value(selenol_message.content, [])

    # Complex path.
    mock_message['content']['content']['test'] = [{
        'b': 43
    }]
    assert _get_value(selenol_message.content, ['test', 0, 'b']) == 43


def test_get_value_from_content(mock_service, mock_message):
    """Test get_value_from_content function."""
    selenol_message = SelenolMessage(mock_message)

    # It has access to content.
    assert get_value_from_content(['keyc'])(
        mock_service, selenol_message) == 'valuec'

    # But it does not have access to session.
    try:
        assert get_value_from_content(['keys'])(
            mock_service, selenol_message) == 'values'
    except SelenolMissingArgumentException as ex:
        assert ex.argument == 'keys'


def test_get_value_from_session(mock_service, mock_message):
    """Test get_value_from_session function."""
    selenol_message = SelenolMessage(mock_message)

    # It has access to session.
    assert get_value_from_session(['keys'])(
        mock_service, selenol_message) == 'values'

    # But it does not have access to content.
    try:
        assert get_value_from_session(['keyc'])(
            mock_service, selenol_message) == 'valuec'
    except SelenolMissingSessionArgumentException as ex:
        assert ex.argument == 'keyc'


def test_selenol_params(mock_service, mock_message):
    """Test selenol_params decorator."""
    selenol_message = SelenolMessage(mock_message)

    def on_request_mock(service, four, three):
        """Function to test the defined parameters."""
        assert service == mock_service
        assert four == 4
        assert three == 3

    def four_function(service, message):
        """Test if the service and message are correct."""
        assert service == mock_service
        assert message == selenol_message
        return 4

    selenol_params(
        four=four_function,
        three=lambda service, message: 3
    )(on_request_mock)(mock_service, selenol_message)
