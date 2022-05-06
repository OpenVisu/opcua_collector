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
import json
import time

from opcua import Node
from opcua.common.subscription import DataChangeNotif
from opcua.ua import MonitoredItemNotification
import sentry_sdk

from backend import Backend

sentry_sdk.init(traces_sample_rate=1)


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    This class is just a sample class. Whatever class having these methods can be used
    https://python-opcua.readthedocs.io/en/latest/_modules/opcua/common/subscription.html
    """

    def __init__(self, server_id: int, backend: Backend):
        self.backend = backend
        self.server_id = server_id

    def datachange_notification(self, node: Node, value, data: DataChangeNotif):
        """
        called for every datachange notification from server
        """
        monitored_item_notification: MonitoredItemNotification = data.monitored_item

        if value is None:
            return

        value = self._object_to_dict(value)
        try:
            value = json.dumps(value)
        except TypeError as error:
            print('could not convert to json')
            print(error)
            print(value)
            return

        st = monitored_item_notification.Value.ServerTimestamp
        response = self.backend.influx_store(
            self.server_id,
            node.nodeid.to_string(),
            round(st.timestamp()) if st is not None else round(time.time()),
            value
        )
        if response.status_code != 200:
            print('could not store data:')
            print(data)
            print(response.text)

    def _object_to_dict(self, value):
        """
        helper method to convert the value to json
        """

        if type(value) in [str, int, float, list, dict, set, tuple]:
            return value
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, datetime.datetime):
            return str(round(value.timestamp()))

        value = value.__dict__
        values = {}
        for key in value.keys():
            values[key] = self._object_to_dict(value[key])
        return values
