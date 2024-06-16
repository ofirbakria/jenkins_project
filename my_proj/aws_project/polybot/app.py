import flask
from flask import request
import os
from bot import ObjectDetectionBot, Bot
import boto3
from botocore.exceptions import ClientError
import json
from loguru import logger

app = flask.Flask(__name__)

def get_secret():

    secret_name = "oferbakria_telebot"
    region_name = "eu-west-1"
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    
    secret = get_secret_value_response['SecretString']
    # Parse the JSON string
    secret_data = json.loads(secret)
    
    # Access the value associated with the 'teleBot' key
    telebot_value = secret_data['teleBot']
    
    return telebot_value


def getSummrize(data):
    # Initialize a dictionary to store counts of each class
    class_counts = {}
    # Iterate through the labels and count occurrences of each class
    for item in data:
        class_name = item['class']
        if class_name in class_counts:
            class_counts[class_name] += 1
        else:
            class_counts[class_name] = 1


    class_counts_string = ""
    for class_name, count in class_counts.items():
        class_counts_string += f"{class_name}: {count}\n"
        
    # TODO send results to the Telegram end-user
    return f'Your photo contains : \n{class_counts_string}'

TELEGRAM_TOKEN = get_secret()
TELEGRAM_APP_URL = os.environ['LOAD_BALANCER']
  
@app.route('/', methods=['GET'])
def index():
    return 'Ok Bro'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'

@app.route(f'/results/', methods=['GET'])
def results():
    prediction_id = request.args.get('predictionId')

    # TODO use the prediction_id to retrieve results from DynamoDB and send to the end-user
    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb',region_name='eu-west-1')

    # Specify the name of the DynamoDB table
    table_name = 'oferbakria_awsproject'

    # Retrieve the item from the DynamoDB table
    response = dynamodb.get_item(
        TableName=table_name,
        Key={
            'prediction_id': {'S': prediction_id}
        }
    )

    # Check if the item was found
    if 'Item' in response:
        item = response['Item']
        chat_id=int(item['chat_id'].get('S'))
        text_results=json.loads(item['description'].get('S'))
    else:
        print(f"No item found with prediction_id: {prediction_id}")

    bot.send_text(chat_id, getSummrize(text_results))
    return prediction_id


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'
    
if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
