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

"""Test data_structures module."""

import copy

from selenol_python.data_structures import (SelenolDictionary, SelenolList,
                                            SelenolMessage)


def test_selenol_dictionary():
    """Test SelenolDictionary class."""
    document = {
        'list': list(range(5)),
        'dictionary': {
            'test': 'test'
        },
        'empty': None,
        'zero': 0,
        'false': False,
    }
    selenol_dictionary = SelenolDictionary(document, AttributeError)

    assert isinstance(selenol_dictionary['list'], SelenolList)
    inner_selenol_list = selenol_dictionary['list']
    assert inner_selenol_list[0] == 0
    assert inner_selenol_list[4] == 4

    assert isinstance(selenol_dictionary['dictionary'], SelenolDictionary)
    inner_selenol_dictionary = selenol_dictionary['dictionary']
    assert inner_selenol_dictionary['test'] == 'test'

    assert selenol_dictionary['empty'] is None

    assert selenol_dictionary['zero'] == 0

    assert selenol_dictionary['false'] is False

    try:
        selenol_dictionary['no']
        assert False, 'Key does not exists'
    except AttributeError as ex:
        assert ex.args[0] == 'no'


def test_selenol_list():
    """Test SelenolList class."""
    document = [
        list(range(5)),  # 0
        {  # 1
            'test': 'test'
        },
        None,  # 2
        0,  # 3
        False,  # 4
    ]
    selenol_list = SelenolList(document, IndexError)

    assert isinstance(selenol_list[0], SelenolList)
    inner_selenol_list = selenol_list[0]
    assert inner_selenol_list[0] == 0
    assert inner_selenol_list[4] == 4

    assert isinstance(selenol_list[1], SelenolDictionary)
    inner_selenol_dictionary = selenol_list[1]
    assert inner_selenol_dictionary['test'] == 'test'

    assert selenol_list[2] is None

    assert selenol_list[3] == 0

    assert selenol_list[4] is False

    def position_tester(pos):
        """Test that pos is not reachable."""
        try:
            selenol_list[pos]
            assert False, 'Pos does not exists'
        except IndexError as ex:
            assert ex.args[0] == pos
    position_tester(-1)
    position_tester(len(document))
    position_tester(1.5)


def test_selenol_message(mock_message):
    """Test SelenolMessage class."""
    message_without_session = copy.deepcopy(mock_message)
    del message_without_session['content']['session']
    selenol_message_without_session = SelenolMessage(message_without_session)
    assert isinstance(
        selenol_message_without_session.session, SelenolDictionary)
    assert isinstance(
        selenol_message_without_session.session, SelenolDictionary)

    message_without_content = copy.deepcopy(mock_message)
    del message_without_content['content']['content']
    selenol_message_without_content = SelenolMessage(message_without_content)
    assert isinstance(
        selenol_message_without_content.content, SelenolDictionary)

    try:
        message_without_request_id = copy.deepcopy(mock_message)
        del message_without_request_id['request_id']
        SelenolMessage(message_without_request_id)
        assert False, "Request ID is a mandatory field"
    except KeyError as ex:
        assert ex.args[0] == 'request_id'
