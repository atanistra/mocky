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
        MOCK_VERSION = "${env.BRANCH_NAME}.b${env.BUILD_NUMBER}.${GIT_COMMIT[0..6]}"
        AWS_ACCESS_KEY_ID = credentials('AAMDEV_AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AAMDEV_AWS_SECRET_ACCESS_KEY')
        AWS_PROFILE = "aamdevelopment"
        AWS_DEFAULT_REGION="eu-west-1"
        DOCKER_REGISTRY = "${env.KDMTS_REGISTRY}"
        IMAGE_TAG = "${env.BRANCH_NAME}"
    }
    stages {
        stage('Build docker image') {
            steps {
                sh 'make docker-build-mocky'
            }
        }
    }
}