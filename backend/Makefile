install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

tests:
	pytest test/

format:
	autopep8 --in-place --recursive .
	black .

lint:
	pylint --disable=R,C *.py **/*.py

all: install lint format