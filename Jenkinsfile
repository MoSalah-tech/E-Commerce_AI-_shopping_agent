pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'mosalah87'
        BACKEND_IMAGE = "${DOCKER_HUB_USER}/shopping-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USER}/shopping-frontend"
        TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh "kubectl --kubeconfig=${KUBECONFIG} set image deployment/backend backend=${BACKEND_IMAGE}:${TAG}"
                        sh "kubectl --kubeconfig=${KUBECONFIG} set image deployment/frontend frontend=${FRONTEND_IMAGE}:${TAG}"
                    }
                }
            }
        }
    }
}