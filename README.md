# Wibix Consulting Internship Assessment

## AWS CloudFormation Read-Only Inventory Solution

---

## Overview

This project automates the creation of a read-only IAM role using AWS CloudFormation and provides a Python script (`aws_inventory.py`) to inventory AWS resources (EC2, S3, RDS, etc.) using the created stack.  
The solution adheres to AWS best practices for security, modularity, and maintainability.

---

## Contents

- `cloud-formation.yaml` - CloudFormation template to provision a read-only IAM role and instance profile.
- `aws_inventory.py` - Python script to fetch AWS resource inventory using the stack.
- This `README.md` - Documentation and usage guide.

---

## Prerequisites

- **AWS Account** with permissions to create IAM roles and CloudFormation stacks.
- **Python 3.x** installed.
- **boto3** library installed (`pip install boto3`).
- **AWS credentials** configured (via `aws configure`, environment variables, or EC2 instance profile).
- The CloudFormation stack must be created and in `CREATE_COMPLETE` state.

---

## How to Use

### 1. Deploy the CloudFormation Stack

- **Upload the template** (`cloud-formation.yaml`) to an S3 bucket.
- **Generate the Launch Stack URL:**  
Which will look something like this: 
[https://console.aws.amazon.com/cloudformation/home?region=ap-south-1#/stacks/create/review?templateURL=https://wibix-cf-templates-shivanshkumar.s3.ap-south-1.amazonaws.com/cloud-formation.yaml&stackName=WibixReadOnlyStack](https://console.aws.amazon.com/cloudformation/home?region=ap-south-1#/stacks/create/review?templateURL=https://wibix-cf-templates-shivanshkumar.s3.ap-south-1.amazonaws.com/cloud-formation.yaml&stackName=WibixReadOnlyStack)
(This is my CloudFormation Launch Stack URL)

- **Open the URL** in your browser (while logged into AWS).
- **Follow the prompts** to create the stack.

### 2. Configure AWS Credentials

- **If running locally:**  
Run `aws configure` and enter your Access Key ID, Secret Access Key, and default region.
- **If running on EC2:**  
Attach the created instance profile to your EC2 instance.
- **If using CloudShell:**  
No extra configuration needed.

### 3. Run the Inventory Script
python3 aws_inventory.py WibixReadOnlyStack
or, using the Launch Stack URL:
python3 aws_inventory.py "https://console.aws.amazon.com/cloudformation/home?region=ap-south-1#/stacks/create/review?templateURL=https://wibix-cf-templates-shivanshkumar.s3.ap-south-1.amazonaws.com/cloud-formation.yaml&stackName=WibixReadOnlyStack"


- The script will:
  - Wait for the stack to be created (if not already).
  - Fetch and print inventory for EC2 instances, S3 buckets, and RDS databases.
  - Summarize the resource counts.

---

## Script Features

- **No explicit credentials:** Uses the default AWS credential provider chain (environment variables, config files, or instance role).
- **Stack-aware:** Accepts either a stack name or a CloudFormation Launch Stack URL.
- **Waits for stack creation:** Polls the stack status and waits for creation to complete.
- **Fetches inventory:** Lists EC2 instances, S3 buckets, and RDS databases with details.
- **Modular and extensible:** Easy to add more AWS resource fetchers.

