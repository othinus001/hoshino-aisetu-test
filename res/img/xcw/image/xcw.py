import os
import random


from nonebot.exceptions import CQHttpError
from nonebot import MessageSegment


from hoshino import R, Service, priv


sv = Service('xcw语音', visible= True, enable_on_default= True, bundle='xcw语音', help_='''
- [@bot 骂我] xcw就会真的骂你
'''.strip())
xcw_folder_mawo = R.get('img/xcw/record/mawo/').path
xcw_folder_pa = R.get('img/xcw/image/pa/').path
xcw_folder_huhuhu = R.get('img/xcw/image/huhuhu/').path
xcw_folder_kkp = R.get('img/xcw/record/kkp/').path
xcw_folder_biantai = R.get('img/xcw/record/biantai/').path

def get_xcw_mawo():
    files = os.listdir(xcw_folder_mawo)
    filename = random.choice(files)
    rec = R.get('img/xcw/record/mawo/', filename)
    return rec

def get_xcw_pa():
    files = os.listdir(xcw_folder_pa)
    filename = random.choice(files)
    rec = R.get('img/xcw/image/pa', filename)
    return rec

def get_xcw_huhuhu():
    files = os.listdir(xcw_folder_huhuhu)
    filename = random.choice(files)
    rec = R.get('img/xcw/image/huhuhu', filename)
    return rec

@sv.on_fullmatch('骂我', only_to_me=True)
async def xcw_mawo(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_xcw_mawo()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_fullmatch('娇喘', only_to_me=True)
async def xcw_jiaochuan(bot, ev) -> MessageSegment:
    filename = '喘息声.mp3'
    file = R.get('img/xcw/record', filename)
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")
       
@sv.on_keyword('爬', only_to_me=False)
async def xcw_pa(bot, ev) -> MessageSegment:
    file = get_xcw_pa()
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_keyword('呼呼呼', only_to_me=False)
async def xcw_huhuhu(bot, ev) -> MessageSegment:
    file = get_xcw_huhuhu()
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")
        
@sv.on_keyword(('0爆','0暴','零爆','零暴'))
async def xcw_huhuhu(bot, ev) -> MessageSegment:
    filename = '0爆.jpg'
    file = R.get('img/xcw/image', filename)
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")
        
dongdong = f'''洞洞还小你们不要~
{R.img(f"xcw/image/脸红.png").cqcode}
'''.strip()

@sv.on_keyword(('洞洞'))
async def dongdong(bot, ev):
    if random.random() < 0.2:
        await bot.send(ev, dongdong)
        
@sv.on_fullmatch('啊这', only_to_me=False)
async def az(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, R.img('xcw/image/成熟点.jpg').cqcode)

        
@sv.on_keyword(('厉害了','666','斯国一'))
async def shigyi(bot, ev):
    if random.random() < 0.2:
        filename = '斯国一斯国一.mp3'
        file = R.get('img/xcw/record', filename)
        try:
            rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")

@sv.on_keyword(('kkp'))
async def kkp(bot, ev):
    file = xcw_folder_kkp()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_keyword('变态', only_to_me=True)
async def biantai(bot, ev):
    file = xcw_folder_biantai()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")