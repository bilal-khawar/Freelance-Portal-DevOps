output "instance_public_ip" {
  value = aws_instance.django_server.public_ip
}
