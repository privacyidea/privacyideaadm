info:
	@echo "pypi -- uplod to python package index"
pypi:
	python setup.py sdist upload
