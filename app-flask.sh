# Python/Flask example
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=app-flask.py
pip install -r requirements_apps.txt --user
python -m flask run --host=0.0.0.0 --port=8888
