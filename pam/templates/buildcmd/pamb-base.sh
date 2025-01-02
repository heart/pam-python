#!/bin/bash

function commit_version() {
    local IMAGE=$1
    local VERSION=$2
    echo "docker push image : 3dsinteractive/$IMAGE:$VERSION"
    docker login -u $DOCKER_USER -p $DOCKER_PASS
    docker push 3dsinteractive/$IMAGE:$VERSION
}

function prepare_project() {
    git config --global url.ssh://git@bitbucket.org/.insteadOf https://bitbucket.org/
}

function build_plugin() {
    prepare_project

    docker build -f Dockerfile -t 3dsinteractive/$IMAGE:$APP_VERSION .
    commit_version $IMAGE $APP_VERSION
}