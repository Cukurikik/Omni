# Omni Me-LLaMA Infra (Terraform)
# Infrastructure Layer: GPU cluster for medical LLM inference.
# Ref: BIDS-Xu-Lab/Me-LLaMA

provider "aws" { region = "us-east-1" }

resource "aws_instance" "omni_mellama_gpu" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "p3.2xlarge"
  tags = { Name = "Omni-MeLLaMA-Inference", Layer = "Compute" }
}
