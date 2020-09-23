export PKG_DIR="py_layer/python"
rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}
docker run --rm -it -v $$PWD:/var/layer -w /var/layer lambci/lambda:build-python3.7 pip install -r requirements.txt --no-deps -t ${PKG_DIR}

export AWS_PROFILE=me
serverless deploy
