#!/usr/local/bin/python3
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

import asyncio
import os
import time
import typing
from concurrent.futures import CancelledError

import sentry_sdk
from asyncua.ua import UaError

import asyncua
from asyncua import Node
from asyncua.ua import UaStatusCodeError
from asyncua.ua.uaerrors import BadMonitoredItemIdInvalid
from asyncua.common.subscription import Subscription

from models.server import Server
from models.node import Node as NodeModel
from sub_handler import SubHandler

from backend import Backend

if os.getenv('SENTRY_DSN') is not None:
    sentry_sdk.init(
        os.getenv('SENTRY_DSN'),
        traces_sample_rate=os.getenv('SENTRY_TRACES_SAMPLE_RATE', '1'),
    )


async def _connect_to_server(server: Server, backend: Backend) -> typing.Tuple[asyncua.Client, Subscription]:
    client = asyncua.Client(server.url, timeout=10)
    connected = False
    connection_error = ''
    subscription: Subscription
    try:
        await client.connect()
        await client.load_data_type_definitions()
        subscription = await client.create_subscription(1000, SubHandler(server.id, backend))

    except UaStatusCodeError as error:  # type: ignore
        connection_error = f"UaStatusCodeError({error.code})"
    except CancelledError:
        connection_error = 'CancelledError'
    except OSError:
        connection_error = 'OSError'
    except UaError:
        connection_error = 'UaError'
    if not connected or connection_error != '':
        backend.server_update(server.id, connection_error)
    return client, subscription


# write new data to opcua server
async def run_update(backend: Backend, clients: typing.Dict[int, asyncua.Client]):
    node_list: typing.List[NodeModel] = backend.node_index_requiring_update()
    print(node_list)
    for node in node_list:
        try:
            await clients[node.server_id].get_node(node.identifier).write_value(node.update_value)
            backend.node_value_writen(node.id)
        except Exception as exception:
            backend.node_value_writing_error(node.id, str(exception))


async def main():
    backend: Backend = Backend(
        os.getenv('API_URL', 'http://api/'),
        os.environ['ACCESS_TOKEN'],
    )
    clients: typing.Dict[int, asyncua.Client] = {}
    server_subscriptions: typing.Dict[int, Subscription] = {}
    node_subscriptions: typing.Dict[int, any] = {}

    try:
        while True:
            # get all servers
            check_time = int(time.time())
            filter_time = check_time - 5 * 60

            # filter servers to all that qualify
            server_list = []
            for s in backend.server_index():  # TODO filter on server side
                if s.checked_at >= s.updated_at and s.checked_at > filter_time:
                    server_list.append(s)

            # connect and subscribe to all servers if not already done
            server_ids = []
            for server in server_list:
                server_ids.append(server.id)
                if server.id not in clients or server.id not in server_subscriptions:
                    clients[server.id], server_subscriptions[server.id] = await _connect_to_server(
                        server, backend)

            # disconnect from all servers that no longer exist
            server_keys = clients.keys()
            for server_id in server_keys:
                if server_id not in server_ids:
                    if server_id in server_subscriptions:  # might not exist if init sequence fails for a server
                        del server_subscriptions[server_id]
                    await clients[server_id].disconnect()
                    del clients[server_id]

            node_list: typing.List[NodeModel] = backend.node_index_filtered()

            # temp list to make unsubscribing easier
            node_ids = []
            for n in node_list:
                node_ids.append(n.id)

                if n.id not in node_subscriptions \
                        and n.server_id in clients \
                        and n.server_id in server_subscriptions:
                    client = clients[n.server_id]
                    node: Node = client.get_node(n.identifier)
                    try:
                        node_subscriptions[n.id] = {
                            'server_id': n.server_id,
                            'subscription': await server_subscriptions[n.server_id].subscribe_data_change(node)
                        }
                    except UaStatusCodeError as error:  # type: ignore
                        print(f"UaStatusCodeError({error.code})")

            # unsubscribe nodes that are no long available / tracked
            node_subscriptions_keys = node_subscriptions.keys()
            for n.id in node_subscriptions_keys:
                if n.id not in node_ids:
                    try:
                        await server_subscriptions[node_subscriptions[n.id]['server_id']] \
                            .unsubscribe(node_subscriptions[n.id]['subscription'])
                    except BadMonitoredItemIdInvalid:  # type: ignore
                        pass
                    del node_subscriptions[n.id]

            for _ in range(round(60 / 5)):
                await run_update(backend, clients)
                await asyncio.sleep(5)

    finally:
        # try to close all remaining open connections
        for server in clients.values():
            try:
                await server.disconnect()
            except AttributeError:
                print('AttributeError while disconnecting')
            except UaStatusCodeError as error:  # type: ignore
                print(f"UaStatusCodeError({error.code})")
            except CancelledError:
                print('CancelledError while disconnecting')
            except OSError:
                print('OSError while disconnecting')
            except UaError:
                print('UaError while disconnecting')


if __name__ == '__main__':
    asyncio.run(main())
