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

"""Test persistences module."""

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from selenol_python.persistences import get_engine, session_creator


def test_get_engine():
    """Test the creation of the ORM engine."""
    connection = 'sqlite://'  # In memory DB for testing.
    engine = get_engine(connection)
    assert isinstance(engine, Engine)
    assert engine.url.drivername == 'sqlite'


def test_session_creator():
    """Test the creation of a database session."""
    connection = 'sqlite://'  # In memory DB for testing.
    session = session_creator(connection)
    assert isinstance(session, Session)
    assert session.bind.url.drivername == 'sqlite'
