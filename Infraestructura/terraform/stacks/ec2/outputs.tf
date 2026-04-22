output "instance_id" {
  description = "ID of the DEV EC2 instance."
  value       = aws_instance.dev_host.id
}

output "public_ip" {
  description = "Public IP address of the DEV EC2 instance."
  value       = aws_instance.dev_host.public_ip
}

output "public_dns" {
  description = "Public DNS name of the DEV EC2 instance."
  value       = aws_instance.dev_host.public_dns
}

output "security_group_id" {
  description = "Security group attached to the DEV EC2 instance."
  value       = aws_security_group.ec2_app.id
}
