docs_up:
	mkdocs serve

docs_deploy:
	mkdocs  gh-deploy

isort:
	PYTHONPATH=src/ isort src/ -m=3 && PYTHONPATH=examples/ isort examples/ -m=3

test:
	python -m pytest examples && pytest --cov=millet

build:
	python setup.py sdist

deploy:
	twine upload dist/*
