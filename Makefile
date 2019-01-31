export WORKSPACE_DIR:=$(shell pwd)
export IMAGE_TAG?=dev
export MOCK_VERSION?=unversioned
export DOCKER_REGISTRY?=local

PACKER?=packer.io

ifeq ($(IMAGE_TAG), master)
export IMAGE_TAG=latest
endif

ifdef AWS_PROFILE
export AWS_PROFILE_ARGS=--profile $(AWS_PROFILE)
endif

docker-login-aws-ecr:
	@$(shell aws ecr get-login --no-include-email --region eu-west-1 $(AWS_PROFILE_ARGS))

docker-build-mocky: docker-login-aws-ecr
	$(PACKER) build ops/mocky_packer.json