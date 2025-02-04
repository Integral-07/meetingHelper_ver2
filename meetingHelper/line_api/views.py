from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os, json, urllib.request
from .util.message_handle_supporter import *
from .models import Member, System

def index(request):

    return HttpResponse("index")

REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + str(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
}

class LineMessage():
    
    def __init__(self, messages):

        if isinstance(messages, list):
            self.messages = messages
        else:
            self.messages = [messages]

    def reply(self, replyToken):

        body = {
            'replyToken': replyToken,
            'messages': self.messages
        }

        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
        print(body)
        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)

@csrf_exempt
def message_handler(request):

    system = System(id=0)
    if request.method == 'POST':

        request = json.loads(request.body.decode('utf-8'))
        event = request['events'][0]
        event_type = event['type']
        line_id = event['source']['userId']

        reply_messages = [{"type": "text", "text": "unknown message"}]

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


            gradeIndex = system.grade_index

            gradeIndex_first = gradeIndex % 3 + 1
            gradeIndex_second = (gradeIndex + 1) % 3 + 1

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
                            "text": "GradeClass" + str(gradeIndex_first)
                        },
                        {
                            "type": "message",
                            "label": "2年生",
                            "text": "GradeClass" + str(gradeIndex_second)
                        },
                    ]
                }
            }
            line_message = LineMessage(reply_messages)
            line_message.reply(event['replyToken'])

        if event_type == 'unfollow':
            """
            友達登録解除（ブロック）されたときの処理

            データベースから該当ユーザ情報を削除する
            """
            try:
                member = Member.objects.get(user_id=line_id)
                member.delete()
                print(f"Delete {line_id}, successfully")
                return HttpResponse(status=200)

            except:
                print("Unexpected error occured when delete member")
                return HttpResponse(status=500)


        if event_type == 'message':
            """
            メッセージが送信されたときの処理

            内容によって処理を分岐する
            ・学年区分が0のとき、受信したメッセージが学年区分の正規表現に一致するなら学年区分してデータベースに設定
            ・名前が空欄なら、受信したメッセージを名前として処理
            ・
            """

            message_type = event['message']['type']
            member = Member.objects.get(user_id=line_id)

            if message_type == 'text': #受信したのがテキストメッセージだった時

                member = Member.objects.get(user_id=line_id)
                message_text = event['message']['text']
                if "GradeClass" in message_text and isGradeclassFieldEmpty(line_id):

                    updated_member = Member(user_id=line_id, grade_class=message_text)
                    updated_member.save()

                    reply_messages = [{"type": "text", "text": "学年区分を設定しました\n次に氏名を教えてください"}]
                
                elif isNameFieldEmpty(line_id) and not isGradeclassFieldEmpty(line_id):

                    updated_member = Member(user_id=member.user_id, grade_class=member.grade_class, name=message_text)
                    updated_member.save()

                    reply_messages = [{"type": "text", "text": f"{message_text} さんで登録しました"}]

                if message_text == "欠席連絡":
                    #欠席連絡フェーズ

                    if member.absent_reason == "":
                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=1, groupsep_flag=0)
                        updated_member.save()

                        reply_messages = [{"type": "text", "text": "欠席理由を教えてください\n理由の送信を以って欠席連絡が確定します"}]

                    else:

                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=2, groupsep_flag=0)
                        updated_member.save()

                        reply_messages = [{
                            "type": "template",
                            "altText": "確認",
                            "template": {
                            "type": "confirm",
                            "text": f"既に欠席連絡が「{member.absent_reason}」で登録されています\n続行すると登録が削除されます",
                            "actions": [
                                {
                                    "type": "message",
                                    "label": "続行",
                                    "text": "続行"
                                },
                                {
                                    "type": "message",
                                    "label": "キャンセル",
                                    "text": "キャンセル"
                                }
                            ]
                            }
                        }]


                #欠席理由登録フェーズ
                elif member.absent_flag == 1:

                    if message_text == "キャンセル":
                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=0,absent_reason=member.absent_reason)
                        updated_member.save()

                        reply_messages = [{"type": "text", "text": "欠席連絡をキャンセルしました"}]

                    else:
                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=0,absent_reason=message_text)
                        updated_member.save()

                        reply_messages = [{"type": "text", "text": f"欠席理由を「{message_text}」で登録しました"}]
                
                #欠席理由更新フェーズ
                elif member.absent_flag == 2:

                    if message_text == "続行":
                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=0, absent_reason="")
                        updated_member.save()

                        reply_messages = [{"type": "text", "text": "欠席連絡を取り消しました"}]

                    elif message_text == "キャンセル":
                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=0, absent_reason=member.absent_reason)
                        updated_member.save()

                        reply_messages = [{"type": "text", "text": "欠席連絡は保持されました"}]

                #欠席状況確認フェーズ
                if message_text == "欠席状況確認":

                    absent_members = Member.objects.exclude(absent_reason="")

                    pre_reply_messages = ""
                    for member in absent_members:
                        pre_reply_messages += f"\n{member.name}: 「{member.absent_reason}」"

                    reply_messages = [
                            {
                                "type": "text", 
                                "text": "以下のメンバが欠席予定です\n" + pre_reply_messages
                            }
                        ]


        line_message = LineMessage(reply_messages)
        line_message.reply(event['replyToken'])


    return HttpResponse(status=200)

