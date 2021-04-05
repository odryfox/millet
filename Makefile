docs_up:
	mkdocs serve

docs_deploy:
	mkdocs  gh-deploy

isort:
	PYTHONPATH=src/ isort src/ -m=3
