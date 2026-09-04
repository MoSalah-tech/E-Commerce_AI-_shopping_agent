pipeline {
    agent any
    environment {
        DOCKER_HUB_USER = 'mosalah87'
        BACKEND_IMAGE = "${DOCKER_HUB_USER}/shopping-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USER}/shopping-frontend"
        TAG = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Build Backend Image') {
            steps {
                script {
                    docker.build("${BACKEND_IMAGE}:${TAG}", "-f Dockerfile .")
                }
            }
        }
        stage('Build Frontend Image') {
            steps {
                script {
                    dir('shopping-agent-frontend') {
                        docker.build("${FRONTEND_IMAGE}:${TAG}", "--build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 .")
                    }
                }
            }
        }
        stage('Push Images to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('', 'docker-hub-credentials') {
                        docker.image("${BACKEND_IMAGE}:${TAG}").push()
                        docker.image("${FRONTEND_IMAGE}:${TAG}").push()
                    }
                }
            }
        }
    }
}