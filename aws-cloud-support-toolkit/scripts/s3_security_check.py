import boto3

# Initialize S3 client
s3 = boto3.client("s3")

def list_s3_buckets():
    response = s3.list_buckets()
    buckets = [bucket["Name"] for bucket in response["Buckets"]]
    return buckets

def check_bucket_public_access(bucket_name):
    try: 
        acl = s3.get_bucket_acl(Bucket=bucket_name)
        for grant in acl["Grants"]:
            grantee = grant.get("Grantee",{})
            if grantee.get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers":
                return True
    except Exception as e:
        print(f"Error checking ACL for {bucket_name}: {e}")
    return False

def check_bucket_encryption(bucket_name):
    try: 
        s3.get_bucket_encryption(Bucket=bucket_name)
        return True # Encryption Enabled
    except s3.exceptions.ClientError:
        return False # No Ecryption
    
def secure_bucket(bucket_name):
    try:
        # Block public access
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
        print(f"Secured bucket: {bucket_name}")

        #Enable defailt encryption (AES256)
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
            },
        )
        print(f"Encryption enabled for {bucket_name}")
    except Exception as e:
        print(f"Error securing bucket {bucket_name}: {e}")

def scan_s3_buckets():
    buckets = list_s3_buckets()
    for bucket in buckets:
        public = check_bucket_public_access(bucket)
        encrypted = check_bucket_encryption(bucket)

        print(f"Bucket: {bucket}")
        print(f"    -Public: {'Yes' if public else 'No'}")
        print(f"    -Encrypted: {'Yes' if encrypted else 'No'}")

        if public or not encrypted:
            print(f"Security Issue Detected in {bucket}! Fixing now...")
if __name__ == "__main__":
    scan_s3_buckets()


        