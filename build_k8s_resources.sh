#!/bin/bash

set -e

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

function usage() {
    echo >&2 "usage: $0 -t <image-tag> -e <endpoint-url> --c <s3-checkpoint-dir>"
}

IMAGE_TAG=
AWS_LAMBDA_ENDPOINT=
S3_CHECKPOINT_DIR=

while getopts t:e:c:h arg; do
  case "$arg" in
    t)
      IMAGE_TAG=$OPTARG
      ;;
    e)
      AWS_LAMBDA_ENDPOINT=$OPTARG
      ;;
    c)
      S3_CHECKPOINT_DIR=$OPTARG
      ;;
    h)
      usage
      exit 0
      ;;
    \?)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$IMAGE_TAG" ]] || [[ -z "$AWS_LAMBDA_ENDPOINT" ]] || [[ -z "$S3_CHECKPOINT_DIR" ]]; then
    usage
    exit 1
fi

PARALLELISM=3
K8S_RESOURCES_YAML="statefun-k8s.yaml"

function generate_module_spec() {
    rm module.yaml

    sed \
        -e "s|%%AWS_LAMBDA_ENDPOINT%%|${AWS_LAMBDA_ENDPOINT}|" \
        "module.yaml.template" > "module.yaml"

    echo >&2 " Generated module.yaml specification."
}

# build the StateFun cluster image
generate_module_spec
docker build -f Dockerfile . -t ${IMAGE_TAG}

helm template k8s/ \
  --set checkpoint.dir=${S3_CHECKPOINT_DIR} \
  --set worker.replicas=${PARALLELISM} \
  --set worker.image=${IMAGE_TAG} \
  --set master.image=${IMAGE_TAG} > ${K8S_RESOURCES_YAML}


echo "Successfully created ${IMAGE_TAG} Docker image."
echo "Upload this Docker image to your docker registry that is accessible from K8S, and"
echo ""
echo "Use: kubectl create -f ${K8S_RESOURCES_YAML}"
