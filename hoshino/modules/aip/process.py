from base64 import b64encode
import base64
from io import BytesIO
import json
from pathlib import Path
import re
import traceback
from PIL import Image, ImageDraw,ImageFont
import os

path_ = Path(__file__).parent # 获取文件所在目录的绝对路径
font_path = str(path_ / 'fonts' / 'SourceHanSansCN-Medium.otf') # 字体路径。Path是路径对象，必须转为str之后ImageFont才能读取



def process_img(data):
    error_msg ="" #报错信息
    msg = ""
    imgmes = ""
    try:
        msgdata = json.loads(re.findall('{"steps".+?}',str(data))[0])
        msg = f'\nseed={msgdata["seed"]}\nscale={msgdata["scale"]}'
    except Exception as e:
        error_msg = "无法获取seed,请检测token是否失效"
        traceback.print_exc()
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        buffer = BytesIO()  # 创建缓存
        img.save(buffer, format="png")
        imgmes = 'base64://' + b64encode(buffer.getvalue()).decode()
    except Exception as e:
        error_msg = "处理图像失败"
        traceback.print_exc()
    return msg,imgmes,error_msg

def img_make(msglist,page = 1):
    target = Image.new('RGB', (1920,1080),(255,255,255))
    i=0
    page = page - 1
    idlist,imglist,thumblist = [],[],[]
    for (a,b,c) in msglist:
        idlist.append(a)
        imglist.append(b)
        thumblist.append(c)
    for index in range(0+(page*8),8+(page*8)):
        try:
            id = f"ID: {idlist[index]}" #图片ID
            thumb = f"点赞: {thumblist[index]}" #点赞数
            image_path= str(imglist[index]) #图片路径
        except:
            break
        region = Image.open(image_path)
        region = region.convert("RGB")
        region = region.resize((int(region.width/2),int(region.height/2)))
        font = ImageFont.truetype(os.path.join(os.path.dirname(__file__),f"093.ttf"), 40)
        draw = ImageDraw.Draw(target)
        if i<4:
            target.paste(region,(80*(i+1)+384*i,50))
            draw.text((80*(i+1)+384*i+int(region.width/2)-130,80+region.height),id,font=font,fill = (0, 0, 0))
            draw.text((80*(i+1)+384*i+int(region.width/2)+10,80+region.height),thumb,font=font,fill = (0, 0, 0))
        if i>=4:
            target.paste(region,(80*(i-3)+384*(i-4),150+384))
            draw.text((80*(i-3)+384*(i-4)+int(region.width/2)-130,180+384+region.height),id,font=font,fill = (0, 0, 0))
            draw.text((80*(i-3)+384*(i-4)+int(region.width/2)+10,180+384+region.height),thumb,font=font,fill = (0, 0, 0))
        i+=1
    result_buffer = BytesIO()
    target.save(result_buffer, format='JPEG', quality=100) #质量影响图片大小
    imgmes = 'base64://' + base64.b64encode(result_buffer.getvalue()).decode()
    resultmes = f"[CQ:image,file={imgmes}]"
    return resultmes