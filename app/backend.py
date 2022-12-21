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

import datetime
import time
from typing import List
import json
import requests

from models.node import Node
from models.server import Server


class Backend:
    API_URL: str
    ACCESS_TOKEN: str

    def __init__(self, api_url: str, access_token: str):
        self.API_URL = api_url
        self.ACCESS_TOKEN = access_token

    def available(self) -> bool:
        response = requests.get(f'{self.API_URL}/api/status/ping')
        return response.status_code == 200

    def server_index(self) -> List[Server]:
        response = requests.get(
            f'{self.API_URL}/api/server_manager/server/index',
            headers=self._get_headers(),
        )
        return [Server(d) for d in response.json()]

    def node_index_filtered(self) -> List[Node]:
        response = requests.get(
            f'{self.API_URL}/api/server_manager/node/index?filter[tracked]=1&filter[virtual]=0&pageSize=-1',
            headers=self._get_headers(),
        )
        return [Node(d) for d in response.json()]

    def node_index_requiring_update(self) -> List[Node]:
        # &filter[change_error][in][]=NULL
        # is used instead of
        # &filter[change_error][eq]=NULL
        # because eq maps to = and not IS and thus is not working
        response = requests.get(
            f'{self.API_URL}/api/server_manager/node/index?filter[tracked]=1&filter[virtual]=0&filter[change_value][neq]="NULL"&filter[change_error][in][]=NULL&pageSize=-1',
            headers=self._get_headers(),
        )
        return [Node(d) for d in response.json()]

    def node_value_writen(self, id: int):
        data = {
            'change_value': None,
            'change_error_at': None,
            'change_error': None,
        }
        self.node_update(id, data)

    def node_value_writing_error(self, id: int, error: str):
        data = {
            'change_error_at': round(time.time()),
            'change_error': error,
        }
        self.node_update(id, data)

    def node_update(self, id: int, data: map):
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        requests.patch(
            self.API_URL +
            '/api/server_manager/node/update?id=%s' % id,
            headers=headers,
            data=json.dumps(data),
        )

    def influx_store(self, server_id: int, node_identifier: str, timestamp: int, value):
        data = {
            "server_id": server_id,
            "node_id": node_identifier,
            "time": timestamp,
            "value": json.dumps(value),
        }
        response = requests.post(
            f'{self.API_URL}/api/server_manager/influx/store',
            headers=self._get_headers(),
            data=data
        )
        return response

    def server_update(self, server_id: int, connection_error: str = ''):
        checked_at: int = round(time.time() + 5)  # hack

        data = {
            'checked_at': checked_at,
        }
        if connection_error == '':
            data['has_connection_error'] = 0
            data['connection_error'] = ''
        else:
            data['has_connection_error'] = 1
            data['connection_error'] = connection_error

        requests.patch(
            f'{self.API_URL}/api/server_manager/server/update?id={server_id}',
            headers=self._get_headers(),
            data=data,
        )

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}

    def object_to_dict(self, value):
        """
        helper method to convert the value to json
        """
        if value is None:
            return value
        if type(value) in [str, int, float, list, dict, set, tuple]:
            return value
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, datetime.datetime):
            return str(round(value.timestamp()))

        value = value.__dict__
        values = {}
        for key in value.keys():
            if(key.startswith('__') and key.endswith('__')):
                continue
            values[key] = self.object_to_dict(value[key])
        return values
