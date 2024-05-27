PROP = [:]

PROP['git_cred'] = 'github'
PROP['branch'] = 'ofer'
PROP['docker_tag'] = 'latest'
// PROP['docker_file_path'] = 'flask/Dockerfile'
PROP['ecr_registry'] = '933060838752.dkr.ecr.eu-west-1.amazonaws.com/ofer'
PROP['aws_region'] = 'eu-west-1'
PROP['aws_cli_cred'] = 'aws_cred'
PROP['image_name'] = 'ofer-flask-image'
PROP['proj_url'] = 'https://github.com/ofirbakria/jenkins_project'

// PROP['email_recepients'] = "alexeymihaylovdev@gmail.com"

pipeline {
    agent { label 'jenkins_ec2' } // Use the label of your EC2 agent
    stages {
        stage('Git clone') {
            steps {
                script{
                    println("=====================================${STAGE_NAME}=====================================")
                    println("Cloning from branch ${PROP.branch} and using credentials ${PROP.git_cred}")
                    git branch: PROP.branch, credentialsId: PROP.git_cred, url: PROP.proj_url
                }
            }
        }


        stage('Create Docker Image') {
            steps {
                 script {
                 println("=====================================${STAGE_NAME}=====================================")
                  sh "docker build -t polybot:${PROP.docker_tag} ./my_proj/aws_project/polybot"
                  sh "docker build -t metricstreamer:${PROP.docker_tag} ./my_proj/aws_project/metricStreamer"
                 }
            }
        }
        
        stage('Upload to ECR AWS') {
            steps {
                script {
                println("=====================================${STAGE_NAME}=====================================")
                    withAWS(credentials: PROP.aws_cli_cred , region: PROP.aws_region ) { 
                    def login = ecrLogin()
                    sh "${login}"
                    sh" docker tag polybot:${PROP.docker_tag} ${PROP.ecr_registry}:polybot"
                    sh" docker push ${PROP.ecr_registry}:polybot"

                    sh" docker tag metricstreamer:${PROP.docker_tag} ${PROP.ecr_registry}:metricstreamer"
                    sh" docker push ${PROP.ecr_registry}:metricstreamer"
                    }
                }
            }
        }

        // stage('Run Terraform to create a new ec2 instance') {
        //     steps {
        //         script {
        //         println("=====================================${STAGE_NAME}=====================================")
        //         sh '''

        //         sudo apt-get update
        //         sudo apt-get install jq

        //         cd ./terraform &&
        //         sudo chmod +x user_data.sh &&
        //         terraform init &&
        //         terraform apply -auto-approve &&
        //         terraform output -json > file.json && 
        //         export public_url=$(cat file.json | jq -r '.["ec2-public_ip"].value')

        //         '''
        //         // sh "sudo apt get update"
        //         // sh "cd ./terraform && sudo chmod +x user_data.sh"
        //         // sh "cd ./terraform && terraform init && terraform apply -auto-approve"
        //         // sh "cd ./terraform && terraform output -json > file.json"
        //         // sh "sudo apt install jq"//cat file.json | jq -r '.["ec2-public_ip"].value'
        //         // sh "public_url=$(cat file.json | jq -r '.['ec2-public_ip'].value')"
        //         }
        //     }
        // }


        // stage('Build hosts file containing public ip') {
        //     steps {
        //         script {
        //         println("=====================================${STAGE_NAME}=====================================")
        //         sh '''
                
        //         export public_url=$(cat terraform/file.json | jq -r '.["ec2-public_ip"].value')

        //         cd ansible &&
        //         echo "[linux]" > hosts.ini &&
        //         echo "$public_url" >> hosts.ini &&
        //         echo "" >> hosts.ini &&
        //         echo "[linux:vars]" >> hosts.ini &&
        //         echo "ansible_ssh_user=ubuntu" >> hosts.ini &&
        //         echo "ansible_ssh_private_key_file=/home/ubuntu/key.pem" >> hosts.ini &&
        //         echo "ansible_ssh_extra_args='-o StrictHostKeyChecking=no'" >> hosts.ini

        //         '''
        //         }
        //     }
        // }
  }
}
// create hosts.ini file and add the public_url into the hosts file