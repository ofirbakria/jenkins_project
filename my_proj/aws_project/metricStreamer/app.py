import time
import boto3
from loguru import logger

autoscaling_client = boto3.client('autoscaling', region_name='eu-west-1')
cloudwatch_client = boto3.client('cloudwatch', region_name='eu-west-1')

AUTOSCALING_GROUP_NAME = 'oferbakria_awsproject'
QUEUE_NAME = 'oferbakria_aws_sqs'


# Function to get backlog per instance
def get_backlog_per_instance():
    sqs_client = boto3.resource('sqs', region_name='eu-west-1')
    queue = sqs_client.get_queue_by_name(QueueName=QUEUE_NAME)
    msgs_in_queue = int(queue.attributes.get('ApproximateNumberOfMessages'))

    asg_groups = autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=[AUTOSCALING_GROUP_NAME])[
        'AutoScalingGroups']
    if not asg_groups:
        raise RuntimeError('Autoscaling group not found')
    else:
        asg_size = asg_groups[0]['DesiredCapacity']

    if (asg_size == 0):
        asg_size = 1

    backlog_per_instance = msgs_in_queue / asg_size
    return backlog_per_instance


# Main function
def main():
    backlog_per_instance = get_backlog_per_instance()

    # Send custom metric to CloudWatch
    cloudwatch_client.put_metric_data(
        Namespace='CustomMetrics',
        MetricData=[
            {
                'MetricName': 'OferAwsProject',
                'Value': backlog_per_instance,
                'Unit': 'Count'
            }
        ]
    )

    logger.info(f'BacklogPerInstance metric sent to CloudWatch with value: {backlog_per_instance}')


if __name__ == '__main__':
    while True:
        main()
        time.sleep(30)