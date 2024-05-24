import json
import requests
import telebot
from loguru import logger
import os
import time
import boto3
from telebot.types import InputFile
from botocore.exceptions import ClientError

class Bot:

    def __init__(self, token, telegram_chat_url):
        print(telegram_chat_url)
        print(token)

        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
       # with open('b-z-new-280415815.pem', 'r') as file:
       #   pem_contents = file.read()
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name="eu-west-1"
        )
        pem_contents = client.get_secret_value(
            SecretId="bashar_certificate"
        )

        print(pem_contents)
        # set the webhook URL
        #self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', certificate=pem_contents)
        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')
        
    

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)
    
    def send_text_result(self, chat_id, desc_json):
        class_counts = {}
        for item in desc_json:
            class_name = item.get("class")
            if class_name:
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
        message = ""
        for class_name, count in class_counts.items():
            message += f"{class_name}: {count}\n"
        
        self.telegram_bot_client.send_message(chat_id, message)
      
        
    
    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)
        

    @staticmethod
    def is_current_msg_photo(msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(chat_id,InputFile(img_path))

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        if 'text' in msg:
            self.send_text(msg['chat']['id'], f'3 :Your original message: {msg["text"]}')
        else:
            self.send_text(msg['chat']['id'], "Sorry, I couldn't process your message.")


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        if self.is_current_msg_photo(msg):
            # Download the user photo
            photo_path = self.download_user_photo(msg)
            photo_key = os.path.basename(photo_path)

            # Upload the photo to S3
            s3 = boto3.client('s3')
            s3.upload_file(photo_path, "basharziv", photo_key)
            logger.info(f"Photo uploaded successfully to S3 bucket: 'basharziv' with key: {photo_key}")

            # Send a message to SQS for processing
            message = {
                'image': photo_key,
                'chat_id': msg['chat']['id']
            }
            self.send_message_to_sqs(json.dumps(message))
        elif self.custom_startswith(msg["text"], "pixabay:"):
            # Handle Pixabay API request
            obj = msg["text"][len("pixabay:"):]
            url2 = f"http://pixabay:8082/getImage?imgName={obj}"
            data2 = requests.get(url2).content
            self.send_text(msg['chat']['id'], f'Your Photo from Pixabay API: {data2} \n')
        else:
            # Handle other messages
            super().handle_message(msg)

    def custom_startswith(self, s, prefix):
        return s.startswith(prefix)

    def send_message_to_sqs(self, message_json):
        try:
            # Deserialize the JSON string to a dictionary
            message = json.loads(message_json)

            # Create an SQS client
            sqs = boto3.client('sqs', region_name="eu-west-1")
            # SQS queue URL
            queue_url = 'https://sqs.eu-west-1.amazonaws.com/933060838752/bashar_z_sqs'

            # Add MessageGroupId parameter
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_json,  # Send the original JSON string as message body                  
            )

            logger.info("Message successfully sent to SQS: %s", response['MessageId'])
            # Send a success message back to the user
            #self.send_text(message['chat_id'], 'Message successfully sent to SQS \n')
        except (ClientError, json.JSONDecodeError) as e:
            logger.error("Error sending message to SQS: %s", e)
            # Send an error message back to the user
            #self.send_text(message['chat_id'], f'Error sending message to SQS: {str(e)} \n')





