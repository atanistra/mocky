#!/usr/bin/env groovy

pipeline {
    agent {
        label {
            label 'docker'
        }
    }
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    environment {
        AWS_ACCESS_KEY_ID = credentials('AAMDEV_AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AAMDEV_AWS_SECRET_ACCESS_KEY')
        AWS_PROFILE = "aamdevelopment"
        DOCKER_REGISTRY = "${env.REPO_PREFIX}"
        IMAGE_TAG = "${env.BRANCH_NAME}
    }
    stages {
        stage('Build docker image') {
            steps {
                sh 'make docker-build-mocky'
            }
        }
    }
}