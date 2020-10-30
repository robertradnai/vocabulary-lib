pipeline {
    agent { docker { image 'python:3.8.6-alpine3.12' } }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
            }
        }
    }
}