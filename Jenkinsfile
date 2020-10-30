pipeline {
    agent { docker { image 'python:3.8.6-alpine3.12' } }
    stages {
        stage('installing the library') {
            steps {
                sh 'python --version'
                sh 'pip install -e .'
            }
        }
        stage('unit tests') {
            sh 'cd tests'
            sh 'python -m unittest'
        }
    }
}