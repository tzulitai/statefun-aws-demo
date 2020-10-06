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

from statefun import StatefulFunctions
from statefun import RequestReplyHandler

from protobuf.inventory_pb2 import RequestItem, ItemReserved, ItemUnavailable
from protobuf.shopping_cart_pb2 import AddToCart

from message_handlers.cart import send_inventory_request, add_to_cart_success, add_to_cart_fail
from message_handlers.inventory import check_and_reserve

from aws_lambda_utils import decode_request, build_response

import constants

functions = StatefulFunctions()

@functions.bind(constants.CART_FUNCTION_TYPE)
def cart(context, message):
    if message.Is(AddToCart.DESCRIPTOR):
        send_inventory_request(context, message)
    elif message.Is(ItemReserved.DESCRIPTOR):
        add_to_cart_success(context, message)
    elif message.Is(ItemUnavailable.DESCRIPTOR):
        add_to_cart_fail(context, message)

@functions.bind(constants.INVENTORY_FUNCTION_TYPE)
def inventory(context, request: RequestItem):
    check_and_reserve(context, request)

handler = RequestReplyHandler(functions)

def lambda_handler(request, context):
    message_bytes = decode_request(request)
    response_bytes = handler(message_bytes)
    return build_response(response_bytes)