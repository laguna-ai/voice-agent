install:
	pip install --upgrade pip &&\
		pip install -r backend/requirements.txt

tests:
	pytest backend/test/

format:
	autopep8 --in-place --recursive backend
	black backend

lint:
	pylint --disable=R,C backend/*.py backend/**/*.py

all: install lint format