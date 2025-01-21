provider "aws" {
  region = "us-east-1"
}

# Simple security group
resource "aws_security_group" "app_sg" {
  name = "game-server-sg"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance
resource "aws_instance" "game_server" {
  ami           = "ami-0fc5d935ebf8bc3bc"  # Amazon Linux 2 in us-west-2
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              EOF

  tags = {
    Name = "game-server"
  }
}

# Output the public IP
output "server_ip" {
  value = aws_instance.game_server.public_ip
}
