import random
from ..models import Member, System
from PIL import Image, ImageDraw, ImageFont
import os, datetime

def isGradeclassFieldEmpty(_user_id):

    member = Member.objects.get(user_id=_user_id)

    if member.grade_class == "":
        return True
    else:
        return False


def isNameFieldEmpty(_user_id):

    member = Member.objects.get(user_id=_user_id)
    
    if member.name == "":
        return True
    else:
        return False
    
def MakeGroups(_num_groups):
    
    """
    メンバを均等にグループ分けする
    :param members: 出席予定のメンバリスト
    :param num_groups: 作成するグループ数
    :return: グループ分けされた辞書
    """
    system = System.objects.get(id=0)
    gradeIndex = system.grade_index

    gradeIndex_first = gradeIndex % 3 + 1
    gradeIndex_second = (gradeIndex + 1) % 3 + 1

    group1 = list(Member.objects.filter(absent_reason="", grade_class="GradeClass" + str(gradeIndex_first)))
    group2 = list(Member.objects.filter(absent_reason="", grade_class="GradeClass" + str(gradeIndex_second)))
    group3 = list(Member.objects.filter(absent_reason="", grade_class="GradeClass" + str(gradeIndex)))

    random.shuffle(group1)
    random.shuffle(group2)
    random.shuffle(group3)

    groups = [[] for _ in range(_num_groups)]

    # ラウンドロビン方式で各グループにメンバを分配
    idx = 0
    for member in group1:
        groups[idx % _num_groups].append(member)
        idx += 1
        
    for member in group2:
        groups[idx % _num_groups].append(member)
        idx += 1

    for member in group3:
        groups[idx % _num_groups].append(member)
        idx += 1


    return groups


def GenerateGroupImage(_num_groups, _groups):
    """
    グループ分けの結果を画像として生成
    """
    # 画像のサイズ設定
    col_width = 170
    row_height = 45
    header_height = 40
    width = max(col_width * _num_groups + 50, col_width * 2 + 100)
    max_rows = max(len(group) for group in _groups)
    height = header_height + max_rows * row_height + 70

    # 画像の作成
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # フォントの設定（環境に応じてパスを変更）
    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"  # Linux環境
    font = ImageFont.truetype(font_path, 24)

    # 表の描画
    y_start = 10
    y = y_start
    x_start = 20
    x = x_start

    dt = datetime.datetime.now()
    draw.text((x, y), f"グループ一覧 (ver.{dt.year}-{dt.month}-{dt.day}-{dt.hour}-{dt.minute})", fill="black", font=font)
    y += header_height

    # 罫線の色
    line_color = "gray"

    for idx, group in enumerate(_groups):
        group_name = f"グループ{idx + 1}"
        draw.text((x + 30, y + 5), group_name, fill="blue", font=font)
        y += row_height

        for member in group:
            draw.text((x + 10, y + 5), member.name, fill="black", font=font)
            y += row_height

        # 縦線の描画（グループの区切り）
        draw.line([(x, y_start + header_height), (x, y_start + header_height + (max_rows + 1) * row_height)], fill=line_color, width=2)
        x += col_width
        y = y_start + header_height

    # 最終の縦線
    draw.line([(x, y_start + header_height), (x, height - 15)], fill=line_color, width=2)

    # 横線の描画（各行の区切り）
    for i in range(max_rows + 2):  # グループ名行 + メンバー行
        y_line = y_start + header_height + i * row_height
        draw.line([(x_start, y_line), (width - 30, y_line)], fill=line_color, width=2)

    # 画像保存
    image_path = "group_table.png"
    img.save(image_path)
    return image_path