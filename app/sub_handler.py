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

import time

from asyncua import Node
from asyncua.common.subscription import DataChangeNotif
from asyncua.ua import MonitoredItemNotification
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

        value = self.backend.object_to_dict(value)

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
