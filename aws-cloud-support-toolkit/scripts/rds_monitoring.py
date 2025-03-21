import boto3
from datetime import datetime, timedelta

# AWS clients
rds = boto3.client("rds")
cloudwatch = boto3.client("cloudwatch")

#Thresholds
CPU_THRESHOLD = 70
STORAGE_THRESHOLD = 80

def list_rds_instances():
    response = rds.describe_db_instances()
    instances = [
        db["DBInstanceIdentifier"] for db in response["DBInstances"]
    ]
    return instances

def check_rds_cpu_usage(instance_id):
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": instance_id}],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=["Average"],
    )

    if response["Datapoints"]:
        avg_cpu = response["Datapoints"][0]["Average"]:
        print(f"Instance {instance_id} CPU Usage: {avg_cpu}%")
        if avg_cpu > CPU_THRESHOLD:
            print(f"ALERT: High CPU usage on {instance_id} - {avg_cpu}%!")

def check_rds_storage_usage(instance_id):
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/RDS",
        MetricName="FreeStorageSpace",
        Dimensions=[{"Name": "DBInstanceIdentifier", "Value": instance_id}],
        StartTime=datetime.utcnow() - timedelta(minutes=10),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=["Average"],
    )
    
    if response["Datapoints"]:
        free_space = response["Datapoints"][0]["Average"] / (1024**3) # Convert bytes to GB
        total_storage = 20 # Default to 20GB
        used_percentage = (1 - (free_space / total_storage)) * 100
        print(f"Instance {instance_id} Storage Usage: {used_percentage:.2f}% used")
        if used_percentage > STORAGE_THRESHOLD:
            print(f"ALERT: Low storage on {instance_id} - {used_percentage:.2f}% used!")

def monitor_rds_instances():
    instances = list_rds_instances()
    for instance in instances:
        check_rds_cpu_usage(instance)
        check_rds_storage_usage(instance)

if __name__ == "__main__":
    monitor_rds_instances()

    