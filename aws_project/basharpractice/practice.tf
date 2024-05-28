# Define the AWS provider
provider "aws" {
  region = "eu-west-1"
}

# Define the EC2 instance
resource "aws_instance" "example" {
  ami                    = "ami-0776c814353b4814d"   # Replace with your preferred Linux AMI
  instance_type          = "t2.micro"
  key_name               = "bashar_z_aws_new"        # Replace with your key pair
  vpc_security_group_ids = ["sg-0e560198198d80f77"]  # Reference to your existing security group
  subnet_id              = "subnet-0429729bb01abd3ca" # Specify the subnet ID

  # Request a public IP address for the instance
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash

              # Update the package list
              apt-get update -y

              # Install Python and pip
              apt-get install -y python3-dev python3-pip
              sudo apt install unzip

              curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
              unzip awscliv2.zip
              sudo ./aws/install



              # Install awscli using pipx
              pipx install awscli


              # Install Docker
              apt-get install -y docker.io

              # Start the Docker service
              systemctl start docker
              systemctl enable docker

              # Authenticate Docker to the ECR registry
              sudo aws ecr get-login-password --region eu-west-1 | sudo docker login --username AWS --password-stdin 933060838752.dkr.ecr.eu-west-1.amazonaws.com

              # Pull the Docker image from ECR
              sudo docker pull 933060838752.dkr.ecr.eu-west-1.amazonaws.com/bashar_ecr:polybot

              # Run the Docker container
              sudo docker run -d 933060838752.dkr.ecr.eu-west-1.amazonaws.com/bashar_ecr:polybot
              EOF

  iam_instance_profile = "iam_role_bashar_z"  # Specify the IAM role attached to the instance

  tags = {
    Name = "example-instance_bashar"
  }
}

# Output the public IP of the instance
output "instance_public_ip" {
  value = aws_instance.example.public_ip
}
