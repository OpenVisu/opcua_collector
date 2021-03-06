# Copyright (C) 2022 Robin Jespersen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sub_handler import SubHandler
from backend import Backend
import unittest


class TestSubHandler(unittest.TestCase):
    backend: Backend
    sub_handler: SubHandler

    def setUp(self):
        self.backend = Backend('http://test-server', 'test-token')
        self.sub_handler = SubHandler(0, self.backend)

    def test_object_to_dict(self):
        class A:
            test_a = 1

            def __init__(self):
                self.test_b = 2

        actual = self.sub_handler._object_to_dict(A())
        self.assertEqual({'test_b': 2}, actual)

        actual = self.sub_handler._object_to_dict(A)
        print(actual)
        self.assertEqual({'test_a': 1}, actual)


if __name__ == '__main__':
    unittest.main()
