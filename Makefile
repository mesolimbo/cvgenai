IMAGE ?= cvgenai-test

.PHONY: test docker-build clean

test: docker-build
	docker run --rm $(IMAGE)

docker-build:
	docker build -t $(IMAGE) .

clean:
	-docker image rm $(IMAGE)
