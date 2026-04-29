# Omni InstructRAG Infra (Terraform)
# Infrastructure Layer: RAG service deployment.
# Ref: weizhepei/InstructRAG — ICLR 2025
provider "aws" { region = "us-east-1" }
resource "aws_instance" "omni_instructrag" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "g5.2xlarge"
  tags = { Name = "Omni-InstructRAG", Layer = "Compute", Framework = "OMNI" }
}
