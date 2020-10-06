#!/bin/bash

set -e

TMP_PACKAGE_DIR="aws_lambda_package"
PACKAGE_NAME="shopping_cart_lambda_function.zip";

rm -rf ${TMP_PACKAGE_DIR}
mkdir -p ${TMP_PACKAGE_DIR}
cd ${TMP_PACKAGE_DIR}

mkdir -p dependencies

pip3 install --target ./dependencies apache-flink-statefun==2.2.0
pip3 install --target ./dependencies protobuf==3.7.1

cd dependencies

zip -r9 ../${PACKAGE_NAME} .

cd ../
rm -rf dependencies

cd ../app/

zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} shopping_cart.py
zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} aws_lambda_utils.py
zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} constants.py
zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} protobuf/inventory_pb2.py
zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} protobuf/shopping_cart_pb2.py
zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} message_handlers/cart.py
zip -g ../${TMP_PACKAGE_DIR}/${PACKAGE_NAME} message_handlers/inventory.py

echo ""
echo "Successfully created AWS Lambda package for the functions, at ${TMP_PACKAGE_DIR}/${PACKAGE_NAME}."
echo "Upload this package to AWS Lambda and service it using AWS API Gateway."
