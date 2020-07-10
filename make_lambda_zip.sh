#!/bin/bash
cd src/layers/v1
pipenv lock -r > requirements.txt
pipenv run pip install -r requirements.txt -t python
zip -vr layer_bundle_01.zip python -x "*__pycache__*"
cd ..

cd v2
pipenv run pip install -r requirements.txt -t python
zip -r layer_bundle_02.zip python -x "*numpy*"
cd ..

cd v3
pipenv run pip install -r requirements.txt -t python
zip -r layer_bundle_03.zip python -x "*numpy*"
cd ..

cd ../..

zip -vr infra/bundle.zip src/ -x "*layers*"
mv -rf src/layers/layer_bundle_01.zip infra/v1/layer_bundle_01.zip
mv -rf src/layers/layer_bundle_02.zip infra/v2/layer_bundle_02.zip
mv -rf src/layers/layer_bundle_03.zip infra/v3/layer_bundle_03.zip

cd infra
ls -lash
cd ..