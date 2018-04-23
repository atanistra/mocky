export WORKSPACE_DIR:=$(shell pwd)
export IMAGE_TAG?=dev

PACKER?=packer.io

ifeq ($(IMAGE_TAG), master)
export IMAGE_TAG=latest
endif

docker-build-mocky:
	$(PACKER) build ops/mocky_packer.json