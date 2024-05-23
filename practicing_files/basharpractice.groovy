pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = "eu-west-1"
        IMAGE_PREFIX = "bashar_jenk"
        ECR_REGISTRY = "933060838752.dkr.ecr.eu-west-1.amazonaws.com" // Your ECR registry URL
        REPOSITORY_NAME = "bashar_ecr"
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    // Define the folders you want to check out
                    def sparseCheckoutPaths = [[path: 'aws_project']]

                    // Perform sparse checkout
                    checkout([$class: 'GitSCM',
                              branches: [[name: 'bashar']],  // Branch name
                              doGenerateSubmoduleConfigurations: false,
                              extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: sparseCheckoutPaths]],
                              userRemoteConfigs: [[url: 'https://github.com/ofirbakria/jenkins_project.git']]])
                }
            }
        }

        stage('Create ECR Repository') {
            steps {
                script {
                    withAWS(region: "${AWS_DEFAULT_REGION}", credentials: 'aws-cred') {
                        // Check if the repository exists
                        def repoExists = sh(script: "aws ecr describe-repositories --repository-names ${REPOSITORY_NAME}", returnStatus: true)

                        // Create the repository if it doesn't exist
                        if (repoExists != 0) {
                            sh "aws ecr create-repository --repository-name ${REPOSITORY_NAME}"
                        } else {
                            echo "Repository ${REPOSITORY_NAME} already exists."
                        }
                    }
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    withAWS(region: "${AWS_DEFAULT_REGION}", credentials: 'aws-cred') {
                        // Login to ECR
                        sh "aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    }

                    // List directories in aws_project folder
                    def directories = sh(script: 'find aws_project -mindepth 1 -maxdepth 1 -type d -printf "%f\n"', returnStdout: true).trim().split('\n')

                    // Filter directories
                    def filteredDirectories = directories.findAll { it in ['polybot', 'yolo5', 'metricStreamer'] }

                    // Loop through each directory
                    filteredDirectories.each { directory ->
                        echo "Building Docker image in ${directory}..."

                        // Change directory to the directory containing the Dockerfile
                        dir("aws_project/${directory}") {
                            // List files to debug
                            sh "ls -la"

                            // Build Docker image
                            def imageTag = "${IMAGE_PREFIX}_${directory.toLowerCase()}"  // Prepend image name with IMAGE_PREFIX
                            sh "docker build -t ${imageTag} ."

                            // Tag Docker image for ECR
                            def ecrImageTag = "${ECR_REGISTRY}/${REPOSITORY_NAME}:${directory.toLowerCase()}"
                            sh "docker tag ${imageTag} ${ecrImageTag}"

                            // Push Docker image to ECR
                            sh "docker push ${ecrImageTag}"
                        }
                    }
                }
            }
        }
    }
}
