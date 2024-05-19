
# Define AWS provider
provider "aws" {
  region = "eu-west-1"
}

# Create a ec2 instance
resource "aws_instance" "ofer_practice" {
  ami           = "ami-0776c814353b4814d"
  instance_type = "t2.micro"
  subnet_id     = "subnet-06228a074282dac6c"
  key_name      = "oferbakria-jenkins"
  associate_public_ip_address = true
  vpc_security_group_ids      = ["sg-01dfcb524956905ff"]

  user_data = file("user_data.sh")
  tags = {
    Name = "demo"
  }
}
