#
# # Define the VPC ID
# variable "vpc_id" {
#   default = "vpc-027487d507d13cc06"
# }
#
# # Define the availability zone for the new subnet
# variable "availability_zone" {
#   default = "eu-west-1a"
# }
#
# # Define the CIDR block for the new subnet
# variable "new_subnet_cidr" {
#   default = "10.1.0.0/23"
# }
#
# # Define the tags for the new subnet
# variable "subnet_tags" {
#   default = {
#     Name = "bashar_z_sub_new"
#   }
# }
#
# # Create the new subnet
# resource "aws_subnet" "new_subnet" {
#   vpc_id            = var.vpc_id
#   cidr_block        = var.new_subnet_cidr
#   availability_zone = var.availability_zone
#
#   tags = var.subnet_tags
# }
#
#
#
# # Add any other resources that need to be created or updated (e.g., route table associations, network ACLs, etc.)
#
#
#
# resource "aws_security_group" "lb_sg" {
#   vpc_id = "vpc-027487d507d13cc06"
#
#   ingress {
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#
#   tags = {
#     Name = "load-balancer-sg"
#   }
# }
#
# resource "aws_lb" "main" {
#   name               = "main-lb"
#   internal           = false
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.lb_sg.id]
#   subnets            = ["subnet-053778fada95789fc", "subnet-0429729bb01abd3ca"]
#
#   tags = {
#     Name = "main-lb"
#   }
# }
#
# resource "aws_lb_listener" "https_listener" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = "443"
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-2016-08"
#   certificate_arn   = "arn:aws:acm:eu-west-1:933060838752:certificate/25f99f85-3d49-4abc-8740-0b8c4bd3c0d1"
#
#   default_action {
#     type             = "forward"
#     target_group_arn = "arn:aws:elasticloadbalancing:eu-west-1:933060838752:targetgroup/bashar-z-3-4/aa9076d19e8eda36"
#   }
# }
