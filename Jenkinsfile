pipeline {
    agent any

    environment {
        IMAGE = "abhishekakurhade/healthai-bot"
        TAG   = "${BUILD_NUMBER}"
    }

    stages {
        stage('Clone code') {
            steps {
                echo 'Cloning code'
                git url: 'https://github.com/abhishekakurhade/HealthAI-Bot.git', branch: 'main'
            }
        }

        stage('Build image') {
            steps {
                echo 'Building the image'
                sh 'docker build -t $IMAGE:$TAG .'
            }
        }

        stage('Push image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker',
                                                  usernameVariable: 'docker_user',
                                                  passwordVariable: 'docker_pass')]) {
                    sh 'echo "$docker_pass" | docker login -u "$docker_user" --password-stdin'
                    sh 'docker push $IMAGE:$TAG'
                    sh 'docker logout'
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withKubeCredentials(kubectlCredentials: [[
                    caCertificate: '',
                    clusterName: 'cluster01',
                    contextName: '',
                    credentialsId: 'eks',
                    namespace: 'default',
                    serverUrl: 'https://F601B891B1084DEC253850223A551881.gr7.ap-south-1.eks.amazonaws.com'
                ]]) {
                    echo 'Applying k8s manifests'
                    sh 'sed -i "s|image: .*healthai-bot.*|image: $IMAGE:$TAG|" menifest/deployment.yml'
                    sh 'kubectl apply -f menifest/deployment.yml -n default'
                    sh 'kubectl apply -f menifest/service.yml -n default'
                    sh 'kubectl rollout status deployment -n default --timeout=120s'
                }
            }
        }
    }
}
