build:
	./build_venv/bin/python -m build
push:
	./build_venv/bin/python -m twine upload --repository pypi dist/*
testpush:
	./build_venv/bin/python -m twine upload --repository testpypi dist/*

#testfetch:
#	python3 -m venv test_venv
#	./test_venv/bin/pip install --index-url https://test.pypi.org/simple --no-deps untext

#fetch:
#	python3 -m venv test_venv
#	./test_venv/bin/pip install --index-url https://test.pypi.org/simple untext
