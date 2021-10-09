docs_up:
	mkdocs serve

docs_deploy:
	mkdocs  gh-deploy

isort:
	isort . -m=3

test:
	python -m pytest examples -s && pytest --cov=millet -s

build:
	python setup.py sdist

deploy:
	twine upload dist/*
