# Omni Andromeda Infra (Terraform)
# Infrastructure Layer: GPU cluster for ultra-long sequence processing.
# Ref: kyegomez/Andromeda — 100K+ token LLM.
provider "aws" { region = "us-west-2" }
resource "aws_instance" "omni_andromeda_gpu" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "p4d.24xlarge"
  tags = { Name = "Omni-Andromeda-100K", Layer = "Compute", Framework = "OMNI" }
}
