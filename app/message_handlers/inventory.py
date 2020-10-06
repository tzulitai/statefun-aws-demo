################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import sys

from protobuf.inventory_pb2 import RequestItem, ItemReserved, ItemUnavailable, Reserved, InStock

def check_and_reserve(context, event):
    item_request = RequestItem()
    event.Unpack(item_request)

    in_stock = __get_num_in_stock_state(context)
    if in_stock.quantity >= item_request.quantity:
        __reserve_and_update_state(context, item_request.quantity)
        item_reserved = ItemReserved()
        item_reserved.id = context.address.identity
        item_reserved.quantity = item_request.quantity
        context.pack_and_reply(item_reserved)
    else:
        item_unavailable = ItemUnavailable()
        item_unavailable.id = context.address.identity
        item_unavailable.quantity = item_request.quantity
        context.pack_and_reply(item_unavailable)


def __get_num_in_stock_state(context):
    in_stock = context.state("in-stock").unpack(InStock)
    if not in_stock:
        in_stock = InStock()
        # in this overly simplified example, we assume each inventory has MAX_SIZE items in stock to begin with;
        # in reality, one can imagine an ingress that supplies "re-stocks" for the inventory function
        in_stock.quantity = sys.maxsize
    return in_stock


def __reserve_and_update_state(context, quantity):
    in_stock = context.state("in-stock").unpack(InStock)
    in_stock.quantity -= quantity

    reserved = context.state("reserved").unpack(Reserved)
    reserved.quantity += quantity

    context.state("in-stock").pack(in_stock)
    context.state("reserved").pack(reserved)
