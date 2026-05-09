resource "aws_instance" "deepfake_inference" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "g5.4xlarge"

  tags = {
    Name = "OMNI-Deepfake-Inference-Node"
  }
}
