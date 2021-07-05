from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)



from linebot.models import *
import json
import tempfile, os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials



app = Flask(__name__)

secretFile = json.load(open("secretFile.txt",'r'))
channelAccessToken = secretFile['y5fns7lFbWJw/ytiO+sD1bwpOy+k00jaDx6CLndUG2JCb9HkbQIVcpJbIIimtUcaMGHir9Z5wNsRhYCEZbCZnBU4OpuBqfgGKSmMpUfriucIgA9OHmhtsjDnAqWE14QnXQdc6Gn1ug7ewqDCZn06TwdB04t89/1O/w1cDnyilFU=']
channelSecret = secretFile['ca73b245c073205927af5fd8f5d95783']

static_tmp_path = os.path.join( 'static', 'tmp')

line_bot_api = LineBotApi(channelAccessToken)
handler = WebhookHandler(channelSecret)


#  line框架


@app.route("callback/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#  接收圖片


@handler.add(MessageEvent, message=(ImageMessage, TextMessage))
def handle_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
        try:
  
            path = os.path.join('static', 'tmp', dist_name)
            print(path) 

        except:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text=' yoyo'),
                    TextSendMessage(text='請傳一張圖片給我')
                ])

#  圖片轉敘述api
        # Set API key.
        subscription_key = 'key'

        # Set endpoint.
        endpoint = 'endpoint'

        # Call API
        computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

        # 指定圖檔
        local_image_path = os.getcwd() + '/static/tmp/{}'.format(path.split('/')[-1])

        # 讀取圖片
        local_image = open(local_image_path, "rb")

        description_results = computervision_client.describe_image_in_stream(local_image)
        
#  回傳圖片描述
        for caption in description_results.captions:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(caption.text))




        

if __name__ == "__main__":
    app.run(host='0.0.0.0')
