#!/bin/bash
set -e

docker build -t test-runner -f tests/Dockerfile.test .
docker run -it --rm --init --ipc=host --network=gestaolegal_default test-runner
