#!/bin/bash

echo "starting jitsi-slack image build"

if [ -z "$DOCKER_REPO_HOST" ]; then
    echo "Error: DOCKER_REPO_HOST must be defined"
    exit 1
fi

[ -z "$DOCKER_TAG" ] && DOCKER_TAG="$(git rev-parse --short HEAD)"

docker buildx create --name slackbuilder --driver docker-container --bootstrap --use

docker buildx build --no-cache --platform=linux/arm64,linux/amd64 --push --pull --progress=plain \
                    --tag $DOCKER_REPO_HOST/jitsi-slack-bolt:$DOCKER_TAG \
                    --tag $DOCKER_REPO_HOST/jitsi-slack-bolt:latest .

docker buildx rm slackbuilder
