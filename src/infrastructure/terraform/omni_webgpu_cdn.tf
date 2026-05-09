# OMNI Framework - Terraform for WebGPU/WebAI CDN
# Provisions a CloudFront distribution for fast global delivery of WASM and tokenizers

resource "aws_s3_bucket" "omni_webai_assets" {
  bucket = "omni-webai-assets-prod"
}

resource "aws_s3_bucket_public_access_block" "omni_webai_assets_public" {
  bucket = aws_s3_bucket.omni_webai_assets.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_cloudfront_distribution" "webai_cdn" {
  origin {
    domain_name = aws_s3_bucket.omni_webai_assets.bucket_regional_domain_name
    origin_id   = "S3-omni-webai-assets-prod"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-omni-webai-assets-prod"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400    # 24 hours (cache WASM models aggressively)
    max_ttl                = 31536000 # 1 year
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}
