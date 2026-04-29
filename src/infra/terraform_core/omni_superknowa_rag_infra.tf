# Omni SuperKnowa RAG Infra (Terraform)
# Ref: ibm-self-serve-assets/SuperKnowa
resource "aws_opensearch_domain" "omni_rag_index" {
  domain_name           = "omni-superknowa-rag"
  engine_version        = "OpenSearch_2.11"
  cluster_config {
    instance_type  = "r6g.large.search"
    instance_count = 2
  }
  ebs_options {
    ebs_enabled = true
    volume_size = 100
    volume_type = "gp3"
  }
  tags = { Project = "OMNI", Batch = "21", Engine = "SuperKnowa" }
}
resource "aws_s3_bucket" "omni_rag_docs" {
  bucket = "omni-superknowa-documents"
  tags   = { Project = "OMNI", Purpose = "RAG-Document-Store" }
}
