pipeline {
    agent { docker { image 'python:3.8.5-slim'  } }
    stages {
        stage('installing the library') {
            steps {
                sh 'python --version'
                sh 'pip install --user --editable .'
            }
        }
        stage('unit tests') {
            steps {
                sh 'cd tests'
                sh 'python -m unittest'
            }
        }
    }
}