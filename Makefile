.PHONY: install run clean

install:
	uv pip install -e .

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/

run:
	python -m gpu_monitor.app
