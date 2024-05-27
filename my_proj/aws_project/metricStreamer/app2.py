import boto3 
import time


sqs_client = boto3.resource('sqs', region_name='eu-west-1')
asg_client = boto3.client('autoscaling', region_name='eu-west-1')

AUTOSCALING_GROUP_NAME = 'oferbakria_awsproject'
QUEUE_NAME = 'oferbakria_aws_sqs'
THRESHOLD_MESSAGES_PER_INSTANCE=10
def calculate():


    queue = sqs_client.get_queue_by_name(QueueName=QUEUE_NAME)
    msgs_in_queue = int(queue.attributes.get('ApproximateNumberOfMessages'))
    asg_groups = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[AUTOSCALING_GROUP_NAME])['AutoScalingGroups']

    if not asg_groups:
        raise RuntimeError('Autoscaling group not found')
    else:
        asg_size = asg_groups[0]['DesiredCapacity']
        if asg_size > 0 :
            backlog_per_instance = msgs_in_queue / asg_size
        else:
            backlog_per_instance = 0

        print(f' {msgs_in_queue} | {asg_size} | {backlog_per_instance}')

    # if (THRESHOLD_MESSAGES_PER_INSTANCE * asg_size) - msgs_in_queue < 0:
    #     scale_up(AUTOSCALING_GROUP_NAME,asg_size)

    # elif ((THRESHOLD_MESSAGES_PER_INSTANCE * asg_size) - msgs_in_queue ) > THRESHOLD_MESSAGES_PER_INSTANCE:
    #     scale_down(AUTOSCALING_GROUP_NAME,asg_size)

    # elif msgs_in_queue == 0 and asg_size>0 :
    #     scale_down(AUTOSCALING_GROUP_NAME,asg_size)

        
    # TODO send backlog_per_instance to cloudwatch...

def scale_up(auto_scaling_group_name,asg_size):
    print('Scaling up...')
    asg_client.set_desired_capacity(
        AutoScalingGroupName=auto_scaling_group_name,
        DesiredCapacity=asg_size + 1
    )

def scale_down(auto_scaling_group_name,asg_size):
    if(asg_size>0):
        print('Scaling down...')
        asg_client.set_desired_capacity(
            AutoScalingGroupName=auto_scaling_group_name,
            DesiredCapacity=asg_size - 1
        )

if __name__ == "__main__":
    while True:
        calculate()
        time.sleep(30)
