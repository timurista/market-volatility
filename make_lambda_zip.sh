cd src/layers/v1
pipenv lock -r > requirements.txt
pipenv run pip install -r requirements.txt -t python
cd ..
zip -vr layer_bundle_01.zip v1/python -x "*__pycache__*"

cd v2
pipenv run pip install -r requirements.txt -t python
cd ..
zip -r layer_bundle_02.zip v2/python -x "*numpy*"

cd v3
pipenv run pip install -r requirements.txt -t python
cd ..
zip -r layer_bundle_03.zip v3/python -x "*numpy*"

cd ../..

zip -vr infra/bundle.zip src/ -x "*layers*"
cp src/layers/layer_bundle_01.zip infra/layer_bundle_01.zip
cp src/layers/layer_bundle_02.zip infra/layer_bundle_02.zip
cp src/layers/layer_bundle_03.zip infra/layer_bundle_03.zip

cd infra
ls -lash
cd ..