import logging
from aiocqhttp import MessageSegment
from matplotlib.pyplot import text
from .utils import *
from io import BytesIO
import os
from PIL import Image
import hoshino
from hoshino import log,aiorequests, Service,priv
import base64, time,  json
import re
import requests
from urllib.parse import urlencode
from . import db
from PIL import Image, ImageDraw, ImageFont
from .process import  process_img
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
fy_URL = "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1"
API_KEY=''#百度云翻译api
SECRET_KEY=''

logger = log.new_logger('aip', hoshino.config.DEBUG)
ai_save = True
dir_path = os.path.join(os.path.dirname(__file__))
save_image_path = "D:/good/"
targetsize = 768*768
thumbSize=(768,768)


TranslateAPI = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
got_image = "http://ip/got_image"
got_image2image = "http://ip/got_image2image"

my_token = ""#

sv_help = "ai标签（标签用空格隔开）合成+空格+"
sv = Service(
    name = 'aip',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )


def clean_tags(tags):
    if 'seed=' in tags or 'Seed='in tags or 'seed:'in tags or 'Seed:'in tags :
           seed=re.findall('(?<=[sS]eed[=:])\s?(\d{1,12})', f"{tags}")[0]
           print(seed)
    else: seed = 0

    if 'scale=' in tags or 'Scale=' in tags or 'scale:' in tags or 'Scale:' in tags:
       scale=re.findall('(?<=[sS]cale[=:])\s?(\d{1,2})', f"{tags}")[0]
    else: scale = 11


    if 'strength=' in tags or 'strength:' in tags or 'Strength=' in tags or 'Strength:' in tags:
       strength=re.findall('(?<=[sS]trength[=:])\s?(0\.\d{1,2})', f"{tags}")[0]
    else: strength = 0.65
    if 'noise=' in tags or 'noise:' in tags or 'Noise=' in tags or 'Noise:' in tags:
       noise=re.findall('(?<=[nN]oise[=:])\s?(0\.\d{1,2})', f"{tags}")[0]
    else: noise = 0.15
    tags =re.sub('，',',',tags)
    tags =re.sub('\n','',tags)
    tags =re.sub("[方横长竖]图", '',tags)
    tags =re.sub("超分", '',tags)
    tags = re.sub("&?(seed|r18|scale)(=|:|：)\s?(\d*)",'', tags)
    tags = re.sub("&?(strength|noise)(=|:|：)\s?(0\.\d{1,2})",'', tags)  
    if 'ntags=' in tags:
        tags=tags.split("Steps:", 1)[0]
        ntags=tags.split("ntags=", 1)[1]
        tags=tags.split("ntags=", 1)[0]
    elif 'ntags:' in tags:
        tags=tags.split("Steps:", 1)[0]
        ntags=tags.split("ntags:", 1)[1]
        tags=tags.split("ntags:", 1)[0]
    elif 'Negative prompt:'in  tags:
        tags=tags.split("Steps:", 1)[0]
        ntags=tags.split("Negative prompt:", 1)[1]
        tags=tags.split("Negative prompt:", 1)[0]
    else:
        ntags='lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry'
    tags=tags.strip()  
    return tags,seed,scale,strength,noise,ntags
#
@sv.on_fullmatch(('tag网站'))
async def list_help(bot, ev):
    msg_list=['tag在线生成\n http://wolfchen.top/tag/ \nhttp://tomxlysplay.com.cn/#/\nhttps://aitag.top/',\
'元素法典\n https://docs.qq.com/doc/DWHl3am5Zb05QbGVs',\
'部分tag文档 https://www.yuque.com/longyuye/lmgcwy/nhnwrz\nhttps://docs.qq.com/doc/DQ05STUdCcnFXWWpH',\
'论坛 \n http://bbs.cgkit.cn/',\
'novelai大汇总https://docs.google.com/spreadsheets/d/e/2PACX-1vRa2HjzocajlsPLH1e5QsJumnEShfooDdeHqcAuxjPKBIVVTHbOYWASAQyfmrQhUtoZAKPri2s_tGxx/pubhtml#']
    forward_msg = render_forward_msg(msg_list)
    try:
        await hoshino.get_bot().send_group_forward_msg(group_id=ev.group_id, messages=forward_msg)
    except:
        hoshino.logger.error('[ERROR]图片发送失败')
        await hoshino.get_bot().send(ev, f'涩图太涩,发不出去力...')
@sv.on_fullmatch(('生成2'))
async def list_help(bot, ev):
    gid = ev.group_id
    image = Image.open(os.path.join(os.path.dirname(__file__),f"help.jpg")).convert('RGB')
    draw= ImageDraw.Draw(image) #建立一个绘图的对象
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__),f"093.ttf"), 30)
    font3 = ImageFont.truetype(os.path.join(os.path.dirname(__file__),f"093.ttf"), 40)
    text1='[aip 后面接英文tag或语句,如果附图即为以图生图] \n\
[tag网站]   提供一些生成tag的网页,手把手教你学会\n\
[我的XP/本群xp]   看看xp排行\n\
[我的XP缝合/本群xp缝合]   看看xp融合图\n\
[清晰术 附图片] 图片超分(默认2倍放大3级降噪)\n\
[清晰术+2倍/3倍/4倍放大+不/保守/强力降噪] 图片放大倍率与降噪倍率选项\n\
[二次元化/动漫化+图片] 照片二次元化\n\
[上传配方] 务必携带seed/scale/tags等参数\n\
[我的/本群/所有配方] 查看已上传图片的配方\n\
[使用配方+图片ID] 使用已上传图片的配方进行快捷绘图\n\
[点赞配方+图片ID] 对已上传图片进行点赞\n\
[删除配方+图片ID] 删除对应图片和配方(仅限维护组使用)\n\
[图片鉴赏/生成tag+图片] 根据上传的图片生成tags\n\
[元素法典 xxx] xxx可以是多种魔咒，空格分离\n\
[元素法典咏唱/吟唱 xxx] 发动黑暗法典，多种魔咒用空格分离\n\
感谢穿越电线大佬，部分功能基于他的项目魔改'

    text2='默认长图，可选添加"横图"/"方图"切换，可不添\n\
可选添加"seed="   生成该seed类似的图\n\
可选添加"scale="  生成质量不同的图'
    text3='可以在aip指令后附图，会根据图生成类似的图\n\
以下是以图生图的参数，只有在附图时才有用，没图就没用\n\
可选添加"strength="    可生成ai参与度不同的图,越大ai参与度越大\n\
可选添加"noise="       可生成噪点不同的图，稍微加一点增加细节\n\n\
已启动自动超分，可能会多10秒用于超分辨率，模型为real cugan2倍1级去噪\n\
已支持直接识别从webui导出的信息(当然前面还是要加aip)\n\
已支持任意形式任意顺序的参数填写,不管你带不带&，用的是=还是:都行'
    text4='以图生图可调整strength范围限制在0.4(微调)-0.54(大调),默认0.4\n\
请使用准确英文tag以修改图中内容'
    text5='seed是啥？\n\
世界线，在这条线上如果参数没变，那么影响不大\n\
随机生成就不要添加seed，如果你想获得此图类似的风格，再加上\n\
scale是啥？\n\
实际表现上来看，低(6-8)饱和度低，偏线稿，线条偏杂乱\n\
高(18-20),再高一点就容易过曝，默认11\n\
strength是啥？\n\
强度，可以理解为ai参与度，建议0.6-0.99，默认0.65\n\
noise是啥？\n\
噪点增加细节，建议0-0.15，再多不好看，默认0.15'
    text6='举例：aip 方图loli,sitting on bed,{{kafuu chino}} seed=12345678 scale=7\n\
逗号分隔tag,加{}代表增加权重,可以加多个,写句子的可以不用管这些\n\
屏蔽词不用加了，我已经加了非常多了，如果你想自定义可使用参数ntags=\n\
指令虽然支持中文翻译但是是百度翻译所以质量不高\n\
但最有效果最准确的是图站Danbooru的英文tag\n\
其次是英文语句（会分析语义），最不准的是中文\n\
可注册登录https://novelai.net/image测试tag是否准确\n'
    text7='如何找tag?如何做个大魔法师？\n\
1.b站微博知乎贴吧推特，已经泛滥了，抄就对了\n\
2.tag表找些群会有的\n\
3.最简单的风格约束：\n\
在图站Danbooru里找张自己喜欢的图，把这张图所有tag复制下来'
    draw.text((87,360),  text1, font=font2, fill="#434343") 
    draw.text((87,1007),  text2, font=font3, fill="#434343")
    draw.text((87,1150),  text3, font=font3, fill="#434343")
    if gid in [485741609,114933726,1055292327,471335862,979253424,466245333]:
       draw.text((87,1440),  text4, font=font3, fill="#d46b08") 
    draw.text((87,1540),  text5, font=font2, fill="#00474f") 
    draw.text((87,2050),  text6, font=font3, fill="#00474f") 
    draw.text((87,2300),  text7, font=font3, fill="#007175") 
    image.save(os.path.join(os.path.dirname(__file__),f"list2.png"))
    list2=os.path.join(os.path.dirname(__file__),f"list2.png")
    await bot.send(ev, MessageSegment.image(f'file:///{list2}'))

def pic2b64(pic: Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return base64_str

async def get_img(image_url):
    image = Image.open(BytesIO(await (await aiorequests.get(image_url, stream=True)).content))
    width, height = image.size
    size = width * height
    if (width/height>1.2):   image_shape = "Landscape"
    elif (0.83<width/height<1.2): image_shape = "Square"
    else:
        image_shape = "Portrait"
    if size <= targetsize:
        return image, image_shape
    image.thumbnail(thumbSize, resample=Image.ANTIALIAS)              
    return image, image_shape


async def download_ai(tags, seed, shape_old, r18, scale,ntags=None,paid=None,strength=None,noise=None,image_url=None):
    para = ""
    if tags != "":
        para += f"?tags={tags}"+f"&token={my_token}"
    if seed != 0:
        para += f"&seed={seed}"
    try:
        if image_url == None:
            url = got_image + para +f"&shape={shape_old}"+f'&ntags={ntags}'
            print(url)
            rsp = await aiorequests.get(url, stream=True, timeout=60)
        else:
            img_old , shape = await get_img(image_url)
            if '方图'==shape_old:shape='Square'
            elif '横图'==shape_old:shape='Landscape'
            url = got_image2image + para +f"&shape={shape}" +f"&strength={strength}" +f"&noise={noise}"+f'&ntags={ntags}' 
            if paid!=None:
                if strength==0.65:
                   url = got_image2image + para +f"&shape={shape}" +f"&strength=0.4" +f"&noise={noise}"+f'&ntags={ntags}' f'&paid=50'
                else: url = got_image2image + para +f"&shape={shape}" +f"&strength={strength}" +f"&noise={noise}"+f'&ntags={ntags}' f'&paid=50'
            rsp = await aiorequests.post(url,timeout=60,data=pic2b64(img_old))
    except Exception as e:
        logger.error(f'Failed to download ')
        logger.exception(e)
    if 200 == rsp.status_code:
        load_data = json.loads(re.findall('{"steps".+?}', str(await rsp.content))[0])
        try:
           json_data = img_encode_to_json(await rsp.content)  # 先获取图片并进行编码
           result = await get_result(json_data,url='http://134.175.32.157:9999/api/predict')  # 然后进行超分辨率重建
           if result is None:
              logger.error(f'这张图没能被正确解析，可能网络连接失败或者是由于远程服务器免费额度耗尽')
           img = img_decode_from_json(result)  # 获取重建后图片并进行解码发送'''
           img = Image.open(BytesIO(img))
        except Exception as e:
           print('错误类型是', e)
           img = Image.open(BytesIO(await rsp.content))
        if ai_save:
            if len(tags.encode())>230:      
               tags = tags.encode()[0:230] # 此处截取bytes长度900
               tags = tags.decode('utf-8', errors='ignore') 
            save_path = 'C:/image/'+ str(f'{tags}-{load_data["seed"]}.png')
            img.save(save_path)
            logger.info(f'Saved to {tags}-{load_data["seed"]}.png')
        return  'base64://' + pic2b64(img), load_data
    else:
        logger.error(f'Failed to download {url}. HTTP {rsp.status_code}')
        return 0        # error

def check_ch(tag):
    for _char in tag:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

@sv.on_prefix(('aip'))
async def ai_picture(bot,ev):
    tags = ev.message.extract_plain_text()
    preid: str = ev.prefix[:-3]
    uid = ev.user_id
    gid = ev.group_id
    if  gid in [485741609,114933726,1055292327,471335862,979253424,466245333]:
        paid=50
    else:paid=None
    if '方图' in tags: shape='方图'
    elif '横图' in tags: shape='横图'
    else: shape = 'Portrait'
    r18=0
    tags,seed,scale,strength,noise,ntags = clean_tags(tags)
    if tags=='':
       await bot.send(ev, '请仔细阅读【生成帮助】的内容，在后面接上tag或语句')
       return
    if check_ch(tags):
       tags = await translate(tags)
    try:
        taglist = re.split(',|，',tags)
        while "" in taglist:
            taglist.remove("")#去除空元素
        for tag in taglist:
                db.add_xp_num(gid,uid,tag)
    except Exception as e:
            logger.info(f"录入数据库失败{e}")
    ret = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    if not ret:
        img ,load_data= await download_ai(tags,seed, shape,r18,scale,ntags)
    else:
        image_url = ret.group(2)
        file = ret.group(1)
        if 'c2cpicdw.qpic.cn/offpic_new/' in image_url:
            md5 = file[:-6].upper()
            image_url = f"http://gchat.qpic.cn/gchatpic_new/0/0-0-{md5}/0?term=2"
        img , load_data= await download_ai(tags,seed,shape,r18,scale,ntags,paid,strength,noise,image_url)
    msg = f"[CQ:image,file={img}]\n"
    msg += f'seed={load_data["seed"]}'
    msg += f' scale={scale}'
    await bot.send(ev, msg,at_sender=True)







async def fetch_token():
    params = {
        'grant_type': 'client_credentials',
        'client_id': API_KEY,
        'client_secret': SECRET_KEY 
    }
    post_data = urlencode(params).encode('utf-8')
    req = await aiorequests.post(TOKEN_URL, post_data, timeout=10)
    result = json.loads(await req.text)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            raise Exception('please ensure has check the ability')
        return result['access_token']
    else:
        raise Exception('please overwrite the correct API_KEY and SECRET_KEY')

async def translate(text):
    token = await fetch_token()
    fy_url = fy_URL + "?access_token=" + token
    try:
      headers = {'Content-Type': 'application/json'}
      payload = {'q': text, 'from': 'zh', 'to': 'en', 'termIds' : ''}
      r = requests.post(fy_url, params=payload, headers=headers)
      result = r.json()
    except:
       return text
    text=result.get('result').get('trans_result')[0].get('dst')
    return text


    
@sv.on_fullmatch(('本群XP', '本群xp'))
async def get_group_xp(bot, ev):
    gid = ev.group_id
    xp_list = db.get_xp_list_group(gid)
    msg = '本群的XP排行榜为：\n'
    if len(xp_list)>0:
        for xpinfo in xp_list:
            keyword, num = xpinfo
            msg += f'关键词：{keyword}；次数：{num}\n'
    else:
        msg += '暂无本群的XP信息'
    await bot.send(ev, msg)

@sv.on_fullmatch(('我的xp','我的XP'))
async def get_personal_xp(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    xp_list = db.get_xp_list_personal(gid,uid)
    msg = '你的XP排行榜为：\n'
    if len(xp_list)>0:
        for xpinfo in xp_list:
            keyword, num = xpinfo
            msg += f'关键词：{keyword}；次数：{num}\n'
    else:
        msg += '暂无你在本群的XP信息'
    await bot.send(ev, msg)

@sv.on_fullmatch(('本群XP缝合', '本群xp缝合'))
async def get_group_xp_pic(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    xp_list = db.get_xp_list_kwd_group(gid)
    msg = []
    if len(xp_list)>0:
        await bot.send(ev, f"正在缝合，请稍后...", at_sender=True)
        for xpinfo in xp_list:
            keyword = xpinfo
            msg.append(keyword)
        xp_tags = (',').join(str(x) for x in msg)
        tags = (',').join(str(x) for x in (re.findall(r"'(.+?)'",xp_tags)))
        if not len(tags):
            tags = 'loli,masterpiece'
            await bot.send(ev, f"没有数据，将使用默认tag：{'loli,masterpiece'}", at_sender=True)
        try:
            url = got_image+'?tags='+tags
            response = await aiorequests.get(url, timeout = 30)
            data = await response.content
        except Exception as e:
            await bot.finish(ev, f"请求超时~", at_sender=True)
        msg,imgmes,error_msg = process_img(data)
        if len(error_msg):
            await bot.finish(ev, f"已报错：{error_msg}", at_sender=True)
        resultmes = f"[CQ:image,file={imgmes}]"
        resultmes += msg
        resultmes += f"\n tags:{tags}"
        await bot.send(ev, resultmes, at_sender=True)
    else:
        msg += '暂无本群的XP信息'

@sv.on_fullmatch(('我的XP缝合', '我的xp缝合'))
async def get_personal_xp_pic(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    
    xp_list = db.get_xp_list_kwd_personal(gid,uid)
    msg = []
    if len(xp_list)>0:
        await bot.send(ev, f"正在缝合，请稍后...", at_sender=True)
        for xpinfo in xp_list:
            keyword = xpinfo
            msg.append(keyword)
        xp_tags = (',').join(str(x) for x in msg)
        tags = (',').join(str(x) for x in (re.findall(r"'(.+?)'",xp_tags)))
        if not len(tags):
            tags = 'loli,masterpiece'
            await bot.send(ev, f"没有数据，将使用默认tag：{'loli,masterpiece'}", at_sender=True)
        try:
            url = got_image+'?tags='+tags
            response = await aiorequests.get(url, timeout = 30)
            data = await response.content
        except Exception as e:
            await bot.finish(ev, f"请求超时~", at_sender=True)
        msg,imgmes,error_msg = process_img(data)
        if len(error_msg):
            await bot.finish(ev, f"已报错：{error_msg}", at_sender=True)
        resultmes = f"[CQ:image,file={imgmes}]"
        resultmes += msg
        resultmes += f"\n tags:{tags}"
        await bot.send(ev, resultmes, at_sender=True)
    else:
        msg += '暂无你在本群的XP信息'

def render_forward_msg(msg_list: list, uid=2854196306, name='会画画的小冰'):
    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
			"type": "node",
			"data": {
				"name": str(name),
				"uin": str(uid),
				"content": msg
			}
		})
    return forward_msg

