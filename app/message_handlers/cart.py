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

from statefun import kinesis_egress_record

from protobuf.shopping_cart_pb2 import AddToCart, AddToCartResult, ItemsInCart
from protobuf.inventory_pb2 import RequestItem, ItemReserved, ItemUnavailable

import constants

def send_inventory_request(context, event):
    add_to_cart = AddToCart()
    event.Unpack(add_to_cart)

    item_request = RequestItem()
    item_request.quantity = add_to_cart.quantity
    context.pack_and_send(
        constants.INVENTORY_FUNCTION_TYPE,
        add_to_cart.item_id,
        item_request
    )


def add_to_cart_success(context, event):
    reserved_item = ItemReserved()
    event.Unpack(reserved_item)

    user_cart = __get_user_cart_state(context)
    user_cart.items[reserved_item.id] = reserved_item.quantity
    __update_user_cart_state(context, user_cart)

    __send_result_to_egress(
        context,
        AddToCartResult.SUCCESS,
        reserved_item.id,
        reserved_item.quantity
    )


def add_to_cart_fail(context, event):
    unavailable_item = ItemUnavailable()
    event.Unpack(unavailable_item)

    __send_result_to_egress(
        context,
        AddToCartResult.FAIL,
        unavailable_item.id,
        unavailable_item.quantity
    )


def __get_user_cart_state(context):
    user_cart = context.state("cart-items").unpack(ItemsInCart)
    if not user_cart:
        user_cart = ItemsInCart()
    return user_cart


def __update_user_cart_state(context, new_user_cart):
    context.state("cart-items").pack(new_user_cart)


def __send_result_to_egress(context, type, item_id, quantity):
    result = AddToCartResult()
    result.type = type
    result.item_id = item_id
    result.quantity = quantity
    context.pack_and_send_egress(
        constants.RESULTS_EGRESS_ID,
        kinesis_egress_record(
            stream="cart_results",
            partition_key=context.address.identity,
            value=result
        )
    )