from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os, json, urllib.request
from .util.message_handle_supporter import *
from .models import Member

def index(request):

    return HttpResponse("index")

REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + str(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
}

class LineMessage():
    
    def __init__(self, messages):

        self.messages = messages

    def reply(self, replyToken):

        body = {
            'replyToken': replyToken,
            'messages': [

                self.messages,
            ]
        }

        print(body)
        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)

@csrf_exempt
def message_handler(request):

    
    if request.method == 'POST':
        request = json.loads(request.body.decode('utf-8'))
        event = request['events'][0]
        event_type = event['type']
        line_id = event['source']['userId']
        replyToken = event['replyToken']

        reply_messages = "unknown message"

        #line_message = LineMessage(message)
        #line_message.reply(line_message)

        if event_type == 'follow':

            """
            友達追加されたときの処理

            データベース上にLINEIDの重複がないか確かめてから
            LINEIDをデータベースに追加する

            データベースの欠損値によってデータを受け付けてデータベースに追加する
            """

            try:
                member = Member.objects.get(user_id=line_id)
            except:
                new_member = Member(user_id=line_id)
                new_member.save()
                member = new_member

            reply_messages = {

                "type": "template",
                "altText": "学年確認",
                "template":{
                    "type": "confirm",
                    "text": "あなたの学年を教えてください",
                    "actions":[
                        {
                            "type": "message",
                            "label": "1年生",
                            "text": "学年区分" #+ gradeIndex_first
                        },
                        {
                            "type": "message",
                            "label": "2年生",
                            "text": "学年区分" #+ gradeIdex_second
                        }
                    ]
                }
            }
            line_message = LineMessage(reply_messages)
            line_message.reply(replyToken)

        if event_type == 'message':
            """
            メッセージが送信されたときの処理

            内容によって処理を分岐する
            ・学年区分が0のとき、受信したメッセージが学年区分の正規表現に一致するなら学年区分してデータベースに設定
            ・名前が空欄なら、受信したメッセージを名前として処理
            """

            message_type = event['message']['type']

            if message_type == 'text': #受信したのがテキストメッセージだった時

                message_text = event['message']['text']
                if "GradeClass" in message_text and isGradeclassFieldEmpty():

                    updated_member = Member(user_id=member.user_id, grade_class=message_text)
                    updated_member.save()

                    reply_messages = "学年区分を設定しました\n次に氏名を教えてください"
                
                if isNameFieldEmpty() and not isGradeclassFieldEmpty():

                    updated_member = Member(user_id=member.user_id, grade_class=member.grade_class, name=message_text)
                    updated_member.save()

                    reply_messages = " さんで登録しました"
                
                line_message = LineMessage(reply_messages)
                line_message.reply()


    return HttpResponse(status=200)


