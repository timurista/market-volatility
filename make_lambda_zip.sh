cd src
pipenv lock -r > requirements.txt
pipenv run pip install -r requirements.txt -t python 
cd ..
zip -vr infra/bundle.zip src/