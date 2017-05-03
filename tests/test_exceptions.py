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

"""Test exceptions module."""

from selenol_python.exceptions import (SelenolException,
                                       SelenolInvalidArgumentException,
                                       SelenolMissingArgumentException,
                                       SelenolMissingSessionArgumentException)


def test_selenol_exception_message():
    """Test the message returned from the exception."""
    message = "This is an example message."
    exception = SelenolException(message)
    assert message == str(exception)


def test_selenol_missing_argument_exception_message():
    """Test the message returned from the exception."""
    argument = 'foo'
    exception = SelenolMissingArgumentException(argument)
    assert argument in str(exception)


def test_selenol_missing_session_argument_exception_message():
    """Test the message returned from the exception."""
    argument = 'foo'
    exception = SelenolMissingSessionArgumentException(argument)
    assert argument in str(exception)


def test_selenol_invalid_argument_exception_message():
    """Test the message returned from the exception."""
    argument = 'foo'
    value = 'bar'
    exception = SelenolInvalidArgumentException(argument, value)
    assert argument in str(exception)
    assert value in str(exception)
