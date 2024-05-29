
# Define AWS provider
provider "aws" {
  region = "eu-west-1"
}


# Create a polybot-ec2 
resource "aws_instance" "polybot-ec2" {
  ami           = "ami-0776c814353b4814d"
  instance_type = "t2.micro"
  subnet_id     = "subnet-0ab427895c5315e17"
  key_name      = "oferbakria-jenkins"
  associate_public_ip_address = true
  vpc_security_group_ids      = ["sg-01dfcb524956905ff"]

  user_data = file("user_data.sh")
  tags = {
    Name = "polybot-ec2"
  }
}

resource "aws_lb_target_group_attachment" "tg_attachment" {
  target_group_arn = "arn:aws:elasticloadbalancing:eu-west-1:933060838752:targetgroup/oferbakria-polybots-http/6c0f1c0753188d8c"
  target_id        = aws_instance.polybot-ec2.id
  port             = 8443
}





# Create a ec2 instance
resource "aws_instance" "metricstreamer-ec2" {
  ami           = "ami-0776c814353b4814d"
  instance_type = "t2.micro"
  subnet_id     = "subnet-0ab427895c5315e17"
  key_name      = "oferbakria-jenkins"
  associate_public_ip_address = true
  vpc_security_group_ids      = ["sg-01dfcb524956905ff"]

  user_data = file("user_data.sh")
  tags = {
    Name = "metricstreamer-ec2"
  }
}