h: help

.PHONY: all clean format help image test tests f h i t

help:
	@echo "Options:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

f: format
t: test
i: image
image: local ## Make a docker image that only supports the architecture we're running on for quick testing

MODULE_VERSION=$(shell grep '^version = ' pyproject.toml | cut -d= -f2 | awk '{print $1}' | sed s/\"//g | sed 's/ //g')
IMAGE_NAME=unixorn/ha-franklin

format:
	black .

tests: test ## Run nose tests
test:
	poetry run pytest --cov

verbose-test: verbose_tests
verbose-tests:
	poetry run pytest --cov --durations 5 -vv

wheel: clean format requirements.txt ## Make a wheel file
	poetry build

local: wheel
	docker buildx build --load -t ${IMAGE_NAME} --build-arg application_version=${MODULE_VERSION} .

multiimage: wheel ## Make a multi-architecture docker image
	docker buildx build --platform linux/arm64,linux/amd64 --push -t ${IMAGE_NAME}:${MODULE_VERSION} --build-arg application_version=${MODULE_VERSION} .
	make local

clean: ## Clean up our checkout
	rm -fv dist/*
	./.hook-scripts/clean-up-pyc-and-pyo-files

multi:
	make multiimage

requirements.txt: poetry.lock Makefile
	poetry export -o requirements.txt
