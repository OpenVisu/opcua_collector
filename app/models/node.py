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

class Node:
    def __init__(self, data):
        self.id: int = data['id']
        self.created_at: int = data['created_at']
        self.updated_at: int = data['updated_at']
        self.created_by: int = data['created_by']
        self.updated_by: int = data['updated_by']

        self.server_id: int = data['server_id']
        self.identifier: str = data['identifier']
        self.display_name: str = data['display_name']
        self.checked_at: int = data['checked_at']
        self.tracked: bool = data['tracked']
        self.path: str = data['path']
        self.data_type: str = data['data_type']
        self.readable: bool = data['readable']
        self.writable: bool = data['writable']
        self.virtual: bool = data['virtual']
        self.parent_identifier: int = data['parent_identifier']
        self.change_value: int = data['change_value']
        self.change_error_at: int = data['change_error_at']
        self.change_error: int = data['change_error']
