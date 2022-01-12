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

class Server:
    def __init__(self, data):
        self.id: int = data['id']
        self.created_at: int = data['created_at']
        self.updated_at: int = data['updated_at']
        self.created_by: int = data['created_by']
        self.updated_by: int = data['updated_by']

        self.sort: int = data['sort']
        self.name: str = data['name']
        self.url: str = data['url']
        self.description: str = data['description']
        self.checked_at: int = data['checked_at']
        self.scan_required: bool = data['scan_required']
        self.has_connection_error: bool = data['has_connection_error']
        self.connection_error: str = data['connection_error']
        self.root_node: str = data['root_node']
