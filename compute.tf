terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Data processing cluster - scaling up for new workload
resource "aws_instance" "data_processor" {
  count         = 10
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "c5.4xlarge"

  tags = {
    Name        = "data-processor-${count.index}"
    Team        = "data-platform"
    Environment = "production"
    Service     = "batch-processing"
  }

  monitoring = true

  root_block_device {
    volume_size = 100
    volume_type = "gp3"
  }
}

# Auto Scaling Group for web tier
resource "aws_launch_template" "web_tier" {
  name_prefix   = "web-tier-"
  image_id      = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "web-tier"
      Team        = "platform"
      Environment = "production"
    }
  }
}

resource "aws_autoscaling_group" "web_tier" {
  name                = "web-tier-asg"
  vpc_zone_identifier = ["subnet-12345", "subnet-67890"]
  desired_capacity    = 10
  max_size            = 20
  min_size            = 5

  launch_template {
    id      = aws_launch_template.web_tier.id
    version = "$Latest"
  }

  tag {
    key                 = "Environment"
    value               = "production"
    propagate_at_launch = true
  }
}
