export WORKSPACE_DIR:=$(shell pwd)

PACKER?=packer.io

docker-build-mocky:
	$(PACKER) build ops/mocky_packer.json