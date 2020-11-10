// https://stackoverflow.com/questions/51648534/unable-to-pip-install-in-docker-image-as-agent-through-jenkins-declarative-pipel?noredirect=1#comment90322558_51648534

pipeline {
    agent { docker {
        image 'python:3.8.5-slim'
        args '--volume /var/jenkins_dist/vocabulary-lib/main:/dist_persistent'
    } }
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
                    dir('tests') {
                        sh 'python -m unittest'
                    }
                }
            }
        }
        stage('Packaging') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    sh 'id'
                    sh 'pip install --upgrade setuptools wheel'
                    sh 'python setup.py sdist bdist_wheel'
                }
            }
        }
        stage('Saving package') {
            steps {
                sh 'mkdir -p /dist_output/$GIT_BRANCH'
                sh 'rm -f /dist_output/$GIT_BRANCH/*'
                sh 'cp dist/*.whl /dist_output/$GIT_BRANCH/'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}