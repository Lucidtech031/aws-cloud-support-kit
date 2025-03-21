import boto3
from datetime import datetime, timedelta

# AWS clients
ce = boto3.client("ce") #AWS Cost Explorer
ec2 = boto3.client("ec2")
s3 = boto3.client("s3")

# AWS Free Tier Limits
FREE_TIER_LIMITS = {
    "AmazonEC2": 750, # 750 hours/month
    "AmazonS3": 5, # 5GB free
    "AWSLambda": 1_000_000 # 1M free requests
}

def get_aws_cost(start_date, end_date):
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UsageQuantity"],
        GroupBy=[{"Type": "SERVICE", "Key": "SERVICE"}],
    )

    cost_date = {}
    for group in response["ResultsByTime"][0]["Groups"]:
        service = group["Keys"][0]
        usage = float(group["Metrics"]["UsageQuantity"]["Amount"])
        cost_data[service] = usage

    return cost_data

def check_free_tier_usage():
    start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.utcnow().strftime("%Y-%m-%d")

    cost_data = get_aws_cost(start_date, end_date)

    for service, usage in cost_data.items():
        limit = FREE_TIER_LIMITS.get(service)
        if limit and usage > limit:
            print(f"ALERT: {service} usage exceeded Free Tier Limit")
        else: 
            print(f"{service} useage: {usage} (Under Free Tier Limit)")

def find_underutilized_ec2():
    response = ec2.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]
            if state == "running":
                metrics = cloudwatch.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName="CPUUtilization",
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=datetime.utcnow() - timedelta(days=7),
                    EndTime=datetime.utcnow(),
                    Period=604800 # 1week
                    Statistics=["Average"]
                )
                avg_cpu = metrics["Datapoints"][0]["Average"] if metrics["Datapoints"] else 0
                if avg_cpu < 5: # Consider stopping if CPU usage is consistently low
                    print(f"ALERT: EC2 Instance {instance_id} is underutilized (Avg CPU: {avg_cpu}%). Consider stopping it.")

def find_old_s3_buckets():
    response = s3.list_buckets()
    for bucket in response["Buckets"]:
        bucket_name = bucket["Name"]
        try:
            last_modified = s3.list_objects_v2(Bucket=bucket_name)["Contents"][0]["LastModified"]
            days_old = (datetime.utcnow() - last_modified.replace(tzinfo=None)).days
            if days_old > 180:
                print(f"ALERT: S3 Bucket '{bucket_name}' has not been access in {days_old} days. Consider deleting it.")
        except Exception:
            print(f"ALERT: S3 Bucket '{bucket_name}' is empty or not accessed.")

def cost_optimization_audit():
    check_free_tier_usage()
    find_underutilized_ec2()
    find_old_s3_buckets()

if __name__ == "__main__":
    cost_optimization_audit()
