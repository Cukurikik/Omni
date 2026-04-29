# Omni BlaGPT Benchmark Infra (Terraform)
# Ref: erogol/BlaGPT
resource "aws_instance" "omni_blagpt_bench" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "g5.2xlarge"
  tags = { Name = "omni-blagpt-benchmark", Project = "OMNI", Batch = "22" }
  root_block_device { volume_size = 200; volume_type = "gp3" }
}
resource "aws_s3_bucket" "omni_blagpt_results" {
  bucket = "omni-blagpt-benchmark-results"
  tags = { Project = "OMNI", Engine = "BlaGPT" }
}
