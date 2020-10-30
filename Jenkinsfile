// https://stackoverflow.com/questions/51648534/unable-to-pip-install-in-docker-image-as-agent-through-jenkins-declarative-pipel?noredirect=1#comment90322558_51648534

pipeline {
    agent { docker { image 'python:3.8.5-slim'  } }
    stages {
        stage('Installing the library') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'pip install --user --editable .'
                }

            }
        }
        stage('Unit tests') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    //sh 'cd tests'
                    sh 'pwd'
                    sh 'ls -R'
                    sh 'cd tests'
                    sh 'python -m unittest'
                }
            }
        }
    }
}