default: cloud

include ../common/Makefile.common

REGISTRY ?= quay.io
REGISTRY_ORG ?= ai-lab
IMAGE_TAG ?= latest

.PHONY: init
init:
	git clone https://gitlab.com/bootc-org/examples.git 2> /dev/null || true
	(cd examples; git pull origin main)

.PHONY: cloud
cloud: init
	"${CONTAINER_TOOL}" build \
		$(ARCH:%=--platform linux/%) \
		$(SOURCE_DATE_EPOCH:%=--timestamp=%) \
		--from="${BOOTC_IMAGE}" \
		--tag "${REGISTRY}/${REGISTRY_ORG}/${IMAGE_NAME}-cloud:${IMAGE_TAG}" \
		examples/cloud-init

.PHONY: push
push: push-amd push-nvidia
