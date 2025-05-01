# aws_inventory.py - Wibix Consulting Internship Assessment Script
# This script connects to AWS using a CloudFormation stack and retrieves resource inventory

import boto3
import argparse
import sys
import time
from botocore.exceptions import ClientError

def parse_arguments():
    """Parse command line arguments to get the stack name or URL."""
    parser = argparse.ArgumentParser(description='Fetch AWS resource inventory using CloudFormation stack')
    parser.add_argument('stack_identifier', help='CloudFormation stack name or URL')
    return parser.parse_args()

def extract_stack_name(stack_identifier):
    """Extract stack name from either a stack name string or a Launch Stack URL."""
    # If it's a URL, extract the stackName parameter
    if stack_identifier.startswith('https://'):
        # Parse the URL to extract stack name
        try:
            # Find stackName in the URL parameters
            if 'stackName=' in stack_identifier:
                parts = stack_identifier.split('stackName=')[1]
                stack_name = parts.split('&')[0]
                return stack_name
        except Exception:
            pass
    
    # Otherwise, assume it's directly the stack name
    return stack_identifier

def wait_for_stack_completion(cf_client, stack_name):
    """Wait for the CloudFormation stack to complete creation."""
    print(f"Waiting for stack {stack_name} to complete creation...")
    
    # List of states that indicate the stack creation is still in progress
    in_progress_states = ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']
    
    while True:
        try:
            # Get the stack details
            response = cf_client.describe_stacks(StackName=stack_name)
            stack_status = response['Stacks'][0]['StackStatus']
            
            if stack_status in in_progress_states:
                print(f"Stack status: {stack_status}. Still waiting...")
                time.sleep(10)  # Wait for 10 seconds before checking again
            elif stack_status == 'CREATE_COMPLETE' or stack_status == 'UPDATE_COMPLETE':
                print(f"Stack creation completed with status: {stack_status}")
                return True
            else:
                print(f"Stack creation failed with status: {stack_status}")
                return False
        except ClientError as e:
            print(f"Error waiting for stack: {e}")
            return False

def get_stack_outputs(cf_client, stack_name):
    """Get the outputs from the CloudFormation stack."""
    try:
        response = cf_client.describe_stacks(StackName=stack_name)
        if 'Outputs' in response['Stacks'][0]:
            # Convert list of outputs to a dictionary for easier access
            outputs = {output['OutputKey']: output['OutputValue'] for output in response['Stacks'][0]['Outputs']}
            return outputs
        else:
            print("Stack has no outputs defined.")
            return {}
    except ClientError as e:
        print(f"Error getting stack outputs: {e}")
        return {}

def fetch_ec2_inventory(ec2_client):
    """Fetch inventory of EC2 instances."""
    print("\n=== EC2 Instance Inventory ===")
    try:
        response = ec2_client.describe_instances()
        instances = []
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                state = instance['State']['Name']
                
                # Get the Name tag if it exists
                name = "N/A"
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                
                print(f"Instance ID: {instance_id}, Name: {name}, Type: {instance_type}, State: {state}")
                instances.append({
                    'InstanceId': instance_id,
                    'Name': name,
                    'Type': instance_type,
                    'State': state
                })
        
        if not instances:
            print("No EC2 instances found.")
        
        return instances
    except ClientError as e:
        print(f"Error fetching EC2 inventory: {e}")
        return []

def fetch_s3_inventory(s3_client):
    """Fetch inventory of S3 buckets."""
    print("\n=== S3 Bucket Inventory ===")
    try:
        response = s3_client.list_buckets()
        buckets = []
        
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            creation_date = bucket['CreationDate']
            
            # Get the region of the bucket
            try:
                location = s3_client.get_bucket_location(Bucket=bucket_name)
                region = location['LocationConstraint'] or 'us-east-1'  # None is returned for us-east-1
            except ClientError:
                region = "Access Denied"
            
            print(f"Bucket: {bucket_name}, Region: {region}, Created: {creation_date}")
            buckets.append({
                'Name': bucket_name,
                'Region': region,
                'CreationDate': str(creation_date)
            })
        
        if not buckets:
            print("No S3 buckets found.")
        
        return buckets
    except ClientError as e:
        print(f"Error fetching S3 inventory: {e}")
        return []

def fetch_rds_inventory(rds_client):
    """Fetch inventory of RDS instances."""
    print("\n=== RDS Database Inventory ===")
    try:
        response = rds_client.describe_db_instances()
        db_instances = []
        
        for db in response['DBInstances']:
            db_id = db['DBInstanceIdentifier']
            engine = db['Engine']
            status = db['DBInstanceStatus']
            
            print(f"DB Instance: {db_id}, Engine: {engine}, Status: {status}")
            db_instances.append({
                'DBInstanceIdentifier': db_id,
                'Engine': engine,
                'Status': status
            })
        
        if not db_instances:
            print("No RDS instances found.")
        
        return db_instances
    except ClientError as e:
        print(f"Error fetching RDS inventory: {e}")
        return []
    
def fetch_lambda_inventory(lambda_client):
    """Fetch inventory of Lambda functions."""
    print("\n=== Lambda Function Inventory ===")
    try:
        response = lambda_client.list_functions()
        functions = []
        for func in response['Functions']:
            name = func['FunctionName']
            runtime = func['Runtime']
            last_modified = func['LastModified']
            print(f"Lambda Function: {name}, Runtime: {runtime}, Last Modified: {last_modified}")
            functions.append({
                'FunctionName': name,
                'Runtime': runtime,
                'LastModified': last_modified
            })
        if not functions:
            print("No Lambda functions found.")
        return functions
    except ClientError as e:
        print(f"Error fetching Lambda inventory: {e}")
        return []

# def fetch_sns_inventory(sns_client):
#     """Fetch inventory of SNS topics."""
#     print("\n=== SNS Topics Inventory ===")
#     try:
#         response = sns_client.list_topics()
#         topics = []
#         for topic in response['Topics']:
#             arn = topic['TopicArn']
#             print(f"SNS Topic ARN: {arn}")
#             topics.append({'TopicArn': arn})
#         if not topics:
#             print("No SNS topics found.")
#         return topics
#     except ClientError as e:
#         print(f"Error fetching SNS inventory: {e}")
#         return []

# def fetch_ssm_inventory(ssm_client):
#     """Fetch inventory of SSM managed instances."""
#     print("\n=== SSM Managed Instances Inventory ===")
#     try:
#         response = ssm_client.describe_instance_information()
#         instances = []
#         for inst in response['InstanceInformationList']:
#             instance_id = inst['InstanceId']
#             platform = inst['PlatformType']
#             ping_status = inst['PingStatus']
#             print(f"SSM Managed Instance: {instance_id}, Platform: {platform}, PingStatus: {ping_status}")
#             instances.append({
#                 'InstanceId': instance_id,
#                 'PlatformType': platform,
#                 'PingStatus': ping_status
#             })
#         if not instances:
#             print("No SSM managed instances found.")
#         return instances
#     except ClientError as e:
#         print(f"Error fetching SSM inventory: {e}")
#         return []

def main():
    """Main function to orchestrate the AWS inventory collection."""
    args = parse_arguments()
    stack_name = extract_stack_name(args.stack_identifier)
    
    print(f"Using stack name: {stack_name}")
    
    # Create boto3 clients
    try:
        session = boto3.Session()
        cf_client = session.client('cloudformation')
        wait_for_stack_completion(cf_client, stack_name)
        outputs = get_stack_outputs(cf_client, stack_name)
        if outputs:
            print(f"Stack outputs: {outputs}")
        
        ec2_client = session.client('ec2')
        s3_client = session.client('s3')
        rds_client = session.client('rds')
        
        ec2_inventory = fetch_ec2_inventory(ec2_client)
        s3_inventory = fetch_s3_inventory(s3_client)
        rds_inventory = fetch_rds_inventory(rds_client)
        
        # Uncomment below to fetch Lambda functions
        # lambda_client = session.client('lambda')
        # lambda_inventory = fetch_lambda_inventory(lambda_client)
        
        # Uncomment below to fetch SNS topics
        # sns_client = session.client('sns')
        # sns_inventory = fetch_sns_inventory(sns_client)
        
        # Uncomment below to fetch SSM managed instances
        # ssm_client = session.client('ssm')
        # ssm_inventory = fetch_ssm_inventory(ssm_client)
        
        print("\n=== Inventory Summary ===")
        print(f"EC2 Instances: {len(ec2_inventory)}")
        print(f"S3 Buckets: {len(s3_inventory)}")
        print(f"RDS Instances: {len(rds_inventory)}")
        # print(f"Lambda Functions: {len(lambda_inventory)}")
        # print(f"SNS Topics: {len(sns_inventory)}")
        # print(f"SSM Managed Instances: {len(ssm_inventory)}")
        
        # You can add more resource fetchers following the same pattern as above.
        
    except ClientError as e:
        print(f"AWS API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Note: The script assumes that the AWS credentials are configured in the environment.