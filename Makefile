docs_up:
	mkdocs serve

docs_deploy:
	mkdocs  gh-deploy

isort:
	isort . -m=3

test:
	python -m pytest examples && pytest --cov=millet

build:
	python setup.py sdist

deploy:
	twine upload dist/*
