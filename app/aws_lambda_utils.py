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

import base64

def build_response(response_bytes):
    response_base64 = base64.b64encode(response_bytes).decode('ascii')
    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": { "Content-Type": "application/octet-stream"},
        "multiValueHeaders": {},
        "body": response_base64
    }
    return response

def decode_request(request):
    return base64.b64decode(request["body"])