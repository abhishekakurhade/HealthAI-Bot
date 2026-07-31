pipeline{
    agent {label "jenkins-worker"}
    
    stages{
        stage ("clone the code"){
            steps{
                git url: "https://github.com/abhishekakurhade/HealthAI-Bot.git", branch: "main"
            }
            
        }
        stage ("build the code"){
            steps{
                echo "build image of portfolio"
                sh "docker build -t abhishekakurhade/healthai:05 ."
            }
        }
        stage ("push image"){
            steps{
                 withCredentials([usernamePassword(
            credentialsId: 'docker-login',       
            usernameVariable: 'DOCKER_USER', 
            passwordVariable: 'DOCKER_PASS'  
        )]){
            
            echo "Logging into Docker Hub..."
            // 2. Log in securely using the variables
            sh "echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin"
            
            echo "Pushing the image..."
            // 3. Push your image to your repository
            sh "docker push abhishekakurhade/healthai:05"
            
            echo "Logging out..."
            // 4. Clean up the session
            sh "docker logout"
        }
            }
    }
}
}
