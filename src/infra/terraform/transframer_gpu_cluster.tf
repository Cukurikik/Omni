resource "aws_instance" "transframer_gpu" {
  ami           = "ami-0abcdef1234567890" # Custom OMNI Deep Learning AMI
  instance_type = "p4d.24xlarge"

  tags = {
    Name = "OMNI-Transframer-Cluster"
  }
}
