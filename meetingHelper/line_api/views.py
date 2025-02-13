from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import random, json, urllib.request
from .util.message_handle_supporter import *
from .models import Member, System
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

def index(request):

    return HttpResponse("index")

REPLY_ENDPOINT_URL = "https://api.line.me/v2/bot/message/reply"
PUSH_ENDPOINT_URL = "https://api.line.me/v2/bot/message/push"
HEADER = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + str(settings.LINE_CHANNEL_ACCESS_TOKEN)
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

        print(body)
        req = urllib.request.Request(REPLY_ENDPOINT_URL, json.dumps(body).encode(), HEADER)

        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err)
        except urllib.error.URLError as err:
            print(err.reason)

def send_auth_info(request):

    sending_times = System.objects.get(id=0).auth_info_times

    if sending_times >= 2:

        messages.error(request, 'リクエスト回数が１日の上限に達しました')
        return redirect('/meeting_helper_access_site/login/')
    
    System.objects.all().update(auth_info_times=sending_times + 1)

    chief_id = System.objects.get(id=0).chief_id

    access_id = settings.USER_NAME
    access_password = settings.USER_PASSWORD

    body = {
        "to": chief_id,
        "messages": [
            {
                "type": "text",
                "text": f"部会ヘルパーのアクセスサイトからIDとパスワードの送信要求がありました. 身に覚えがない場合は無視してください.\n\n[認証情報]\nID : {access_id}\nPassword : {access_password}"
            }
        ]
    }

    req = urllib.request.Request(PUSH_ENDPOINT_URL, json.dumps(body).encode(), HEADER)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
    except urllib.error.HTTPError as err:
        print(err)
    except urllib.error.URLError as err:
        print(err.reason)

    messages.error(request, '委員長のLINEに認証情報を送信しました')
    return redirect("/meeting_helper_access_site/login/")

@csrf_exempt
def message_handler(request):


    system = System.objects.get(id=0)

    if request.method == 'POST':

        request = json.loads(request.body.decode('utf-8'))
        event = request['events'][0]
        event_type = event['type']
        line_id = event['source']['userId']

        reply_messages = [{"type": "text", "text": "何のことかわからないよぉ～？\n\nhttps://www.dropbox.com/scl/fi/zooivgoghggkyttqxnp4c/_.pdf?rlkey=mifunwp2dcqe8ert48l279mfd&st=z86lgu57&dl=0"}]

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
            
        try:
            Member.objects.get(user_id=line_id)
        except:
            
            reply_messages = [{"type": "text", "text": "あなたはメンバーから削除されています\n委員会から脱退又は引退している場合は、このアカウントを友達から削除してください"}]
            line_message = LineMessage(reply_messages)
            line_message.reply(event['replyToken'])

            return HttpResponse(status=200)


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

                
                #委員長権限機能
                if member.user_id == system.chief_id:

                    #世代交代フェーズ
                    if message_text == "世代交代":

                        if member.grade_class == "GradeClass" + str(system.grade_index):

                            reply_messages = [
                                {
                                    "type": "text", 
                                    "text": "あなたは最高学年の委員長であるので、この機能を実行できません\n次期委員長に委員長を交代してから次期委員長に実行させてください\n\n委員長交代の方法 : 現委員長が部会ヘルパーに「委員長交代」と送信する"
                                }
                            ]

                            line_message = LineMessage(reply_messages)
                            line_message.reply(event['replyToken'])

                            return HttpResponse(status=200)

                        updated_system = System(id=system.id, grade_index=system.grade_index, chief_id=system.chief_id ,flag_register="RG", meeting_DayOfWeek=system.meeting_DayOfWeek, auth_info_times=system.auth_info_times)
                        updated_system.save()

                        reply_messages = [
                            {
                                "type": "template",
                                "altText": "確認",
                                "template": {
                                    "type": "confirm",
                                    "text": f"世代を交代します\n世代を交代すると、現在の最高学年のメンバは削除されます\nよろしいですか？",
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
                            }
                        ]

                    #世代交代確定フェーズ
                    elif system.flag_register == "RG":

                        if message_text == "続行":

                            rotateGeneration()

                            reply_messages = [{"type": "text", "text": "世代交代が完了しました"}]

                        else:

                            updated_system = System(id=system.id, grade_index=system.grade_index, chief_id=system.chief_id ,flag_register="NULL", meeting_DayOfWeek=system.meeting_DayOfWeek, auth_info_times=system.auth_info_times)
                            updated_system.save()

                            reply_messages = [{"type": "text", "text": "世代交代をキャンセルしました"}]

                    #委員長交代フェーズ
                    if message_text == "委員長交代":
                        
                        access_code = random.randint(1000, 9999)

                        updated_system = System(id=system.id, grade_index=system.grade_index, chief_id=system.chief_id ,flag_register=str(access_code), meeting_DayOfWeek=system.meeting_DayOfWeek, auth_info_times=system.auth_info_times)
                        updated_system.save()

                        reply_messages = [{"type": "text", "text": f"委員長を交代するには以下の認証コードを次期委員長が部会ヘルパーに送信してください\n認証コードを(現委員長)->(次期委員長)->(部会ヘルパ)に送信します\n\n認証コード: {access_code}"}]

                else:

                    if message_text == "世代交代" or message_text == "委員長交代":

                        reply_messages = [{"type": "text", "text": "実行権限がありません\nこの機能は委員長のみに権限があります"}]


                #委員長交代承認フェーズ
                if message_text == system.flag_register and message_text.isdigit():

                    updated_system = System(id=system.id, grade_index=system.grade_index, chief_id=member.user_id ,flag_register="NULL", meeting_DayOfWeek=system.meeting_DayOfWeek, auth_info_times=system.auth_info_times)
                    updated_system.save()

                    reply_messages = [{"type": "text", "text": "委員長を交代しました\n前期委員長に交代が完了したことを伝えてください"}]

                #欠席連絡フェーズ
                if message_text == "欠席連絡":

                    if member.absent_reason == "":
                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=1, groupsep_flag=0, absent_reason=member.absent_reason)
                        updated_member.save()

                        reply_messages = [
                            {
                                "type": "text", 
                                "text": "欠席理由を教えてください\n理由の送信を以って欠席連絡が確定します",
                                "quickReply": {
                                    "items": [
                                        {
                                            "type": "action",
                                            #"imageUrl": image_url.shrine_icon_url,
                                            "action": {
                                                "type": "message",
                                                "label": "議長",
                                                "text": "議長のため"
                                            }
                                        },
                                        {
                                            "type": "action",
                                            #"imageUrl": image_url.restaurant_icon_url,
                                            "action": {
                                                "type": "message",
                                                "label": "書記",
                                                "text": "書記のため"
                                            }
                                        }
                                ]}
                            }
                        ]

                    else:

                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=2, groupsep_flag=0, absent_reason=member.absent_reason)
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

                #グループ作成依頼フェーズ
                if message_text == "グループ作成":

                    updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=1, absent_reason=member.absent_reason)
                    updated_member.save()

                    attendance_members = Member.objects.filter(absent_reason="").order_by("-grade_class")

                    pre_reply_messages = ""
                    member_count = len(attendance_members)
                    for member in attendance_members:
                        pre_reply_messages += f"{member.name}\n"

                    reply_messages = [
                        {
                            "type": "text", 
                            "text": f"{pre_reply_messages}\n以上の {member_count} 人が出席予定です\n何グループ作成しますか？"
                        }
                    ]

                #グループ数確認and作成フェーズ
                elif member.groupsep_flag == 1:

                    num_member = Member.objects.filter(absent_reason="").count()
                    if message_text.isdigit() and int(message_text) <= num_member and int(message_text) != 0: #入力値が出席可能なメンバ数以下の整数ならば

                        try:
                            #member_list = Member.objects.filter(absent_reason="")
                            num_groups = int(message_text)

                            groups = MakeGroups(num_groups)

                            #return_text = ""
                            #for i, group in enumerate(groups, 1):
                            #    return_text += f"グループ {i}: {[member.name for member in group]}" + "\n"

                            updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=0, absent_reason=member.absent_reason)
                            updated_member.save()
                            media_url = GenerateGroupImage(num_groups, groups)
                            #media_url = request_raw.build_absolute_uri('/media/group_table.png')
                            reply_messages = [
                                {
                                    "type": "text", 
                                    "text": "グループを作成しました"
                                },
                                {
                                    "type": "image",
                                    "originalContentUrl": media_url,
                                    "previewImageUrl": media_url
                                }
                            ]

                        except Exception as e:
                            reply_messages = [{"type": "text", "text": f"グループの作成に失敗しました\n{e}"}]
                            print(f"Error group making fail:{e}")

                    elif message_text == "キャンセル":

                        updated_member = Member(user_id=member.user_id, name=member.name, grade_class=member.grade_class, absent_flag=0, groupsep_flag=0, absent_reason=member.absent_reason)
                        updated_member.save()

                        reply_messages = [{"type": "text", "text": "グループ作成をキャンセルしました"}]


                    else:
                        reply_messages = [{"type": "text", "text": f"グループ数が無効な値です\n出席可能なメンバ数以下の自然数を入力してください\n(現在の出席可能なメンバ:{num_member}人)"}]


                if message_text == "説明書":

                    reply_messages = [{"type": "text", "text": "https://www.dropbox.com/scl/fi/zooivgoghggkyttqxnp4c/_.pdf?rlkey=mifunwp2dcqe8ert48l279mfd&st=z86lgu57&dl=0"}]

        line_message = LineMessage(reply_messages)
        line_message.reply(event['replyToken'])


    return HttpResponse(status=200)

