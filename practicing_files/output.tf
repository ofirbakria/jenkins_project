# ##############################################################################
# # Outputs File
# #
# # Here is where we store the output values for all the variables used in our
# # Terraform code. If you create a variable with no default, the user will be
# # prompted to enter it (or define it via config file or command line flags.)
# 
# 
# 

output "ec2-public_ip" {
  description = "The public IP of the ec2."
  value       = aws_instance.ofer_practice.public_ip
}



# If yo want to see the output to json of the terraform code, you can run the following command: "terraform output -json > output.json"