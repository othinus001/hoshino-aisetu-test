import os
import traceback
import hoshino
from . import db
from .packedfiles import default_config
from hoshino.typing import CQEvent
import re
import json
from hoshino import Service, priv
from io import BytesIO
from . import magic

sv_help = '''
注：+ 号不用输入
【主要功能】
[ai绘图/生成涩图+tag] 关键词仅支持英文，用逗号隔开
[以图绘图/以图生图+tag+图片] 注意图片尽量长宽都在765像素以下，不然会被狠狠地压缩
[清晰术/图片超分+图片] 图片超分(默认2倍放大3级降噪)
[清晰术+2倍/3倍/4倍放大+不/保守/强力降噪] 图片放大倍率与降噪倍率选项
[二次元化/动漫化+图片] 照片二次元化
[上传pic/上传图片] 务必携带seed/scale/tags等参数
[查看配方/查看tag+图片ID] 查看已上传图片的配方
[快捷绘图+图片ID] 使用已上传图片的配方进行快捷绘图
[查看个人pic/查看个人图片+页码] 查看个人已上传的图片
[查看本群pic/查看本群图片+页码] 查看本群已上传的图片
[查看全部pic/查看全部图片+页码] 查看全部群已上传的图片
[点赞pic/点赞图片+图片ID] 对已上传图片进行点赞
[删除pic/删除图片+图片ID] 删除对应图片和配方(仅限维护组使用)
[本群/个人XP排行] 本群/个人的tag使用频率
[本群/个人XP缝合] 缝合tags进行绘图
[图片鉴赏/生成tag+图片] 根据上传的图片生成tags
[回复消息+以图绘图/上传图片/图片鉴赏/清晰术/二次元化] 回复消息使用上述功能
[元素法典 xxx] xxx可以是多种魔咒，空格分离
[元素法典咏唱/吟唱 xxx] 发动黑暗法典，多种魔咒用空格分离

【元素法典目录】
['水魔法', '空间法', '冰魔法', '核爆法', '风魔法', '流沙法', '白骨法', '星空法', '机凯种', 
'森林冰', '幻之时', '雷男法', '圣光法', '苇名法', '自然法', '冰系改', '融合法', '虹彩法', 
'暗锁法', '星冰乐', '火烧云', '城堡法', '雪月法', '结晶法', '黄昏法', '森林法', '泡泡法', 
'蔷薇法', '月亮法', '森火法', '废土法', '机娘水', '黄金法', '死灵法', '水晶法', '水森法', 
'冰火法', '龙骑士', '坠落法', '水下法', '秘境法', '摄影法', '望穿水', '天选术', '摩登法', 
'血魔法', '绚丽术', '唤龙术', '龙机法', '战姬法', '炼银术', '星源法', '学院法', '浮世绘', 
'星霞海', '冬雪法', '刻刻帝', '万物熔炉', '暗鸦法', '花 火法基础', '星之彩', '沉入星海', 
'百溺法', '百溺法plus', '辉煌阳光法', '星鬓法', '森罗法', '星天使', '黄金律', '机凯姬 改', 
'人鱼法', '末日', '碎梦', '幻碎梦', '血法改', '留影术', '西幻术', '星语术', '金石法', 
'飘花法', '冰霜龙息plus', '冰霜龙息']

【以下为维护组使用(空格不能漏)】
[绘图 状态 <群号>] 查看本群或指定群的模块开启状态
[绘图 设置 撤回时间 0~999 <群号>] 设置本群或指定群撤回时间(单位秒)，0为不撤回
[绘图 设置 tags整理/数据录入/中英翻译/违禁词过滤 启用/关闭 <群号>] 启用或关闭对应模块
[绘图 黑/白名单 新增/添加/移除/删除 群号] 修改黑白名单
[黑名单列表/白名单列表] 查询黑白名单列表

【参数使用说明】
加{}代表增加权重,可以加很多个
可选参数：
&ntags=xxx 负面tags输入
&shape=Portrait/Landscape/Square 默认Portrait竖图。Landscape(横图)，Square(方图)
&scale=11 默认11，赋予AI自由度的参数，越高表示越遵守tags，一般保持11左右不变
&seed=1111111 随机种子。在其他条件不变的情况下，相同的种子代表生成相同的图
输入例：
ai绘图 {{miku}},long hair&ntags=lowres,bad hands&shape=Portrait&scale=24&seed=150502
'''.strip()
ysfd=['水魔法', '空间法', '冰魔法', '核爆法', '风魔法', '流沙法', '白骨法', '星空法', '机凯种', 
'森林冰', '幻之时', '雷男法', '圣光法', '苇名法', '自然法', '冰系改', '融合法', '虹彩法', 
'暗锁法', '星冰乐', '火烧云', '城堡法', '雪月法', '结晶法', '黄昏法', '森林法', '泡泡法', 
'蔷薇法', '月亮法', '森火法', '废土法', '机娘水', '黄金法', '死灵法', '水晶法', '水森法', 
'冰火法', '龙骑士', '坠落法', '水下法', '秘境法', '摄影法', '望穿水', '天选术', '摩登法', 
'血魔法', '绚丽术', '唤龙术', '龙机法', '战姬法', '炼银术', '星源法', '学院法', '浮世绘', 
'星霞海', '冬雪法', '刻刻帝', '万物熔炉', '暗鸦法', '花 火法基础', '星之彩', '沉入星海', 
'百溺法', '百溺法plus', '辉煌阳光法', '星鬓法', '森罗法', '星天使', '黄金律', '机凯姬 改', 
'人鱼法', '末日', '碎梦', '幻碎梦', '血法改', '留影术', '西幻术', '星语术', '金石法', 
'飘花法', '冰霜龙息plus', '冰霜龙息']
sv = Service(
    name="ai绘图",  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle="娱乐",  # 分组归类
    help_=sv_help  # 帮助说明
)

config_default = default_config.config_default
group_list_default = default_config.group_list_default
groupconfig_default = default_config.groupconfig_default

# Check config if exist
pathcfg = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(pathcfg):
	try:
		with open(pathcfg, 'w') as cfgf:
			json.dump(config_default, cfgf, ensure_ascii=False, indent=4)
			hoshino.logger.error('[WARNING]未找到配置文件，已根据默认配置模板创建，请打开插件目录内config.json查看和修改。')
	except:
		hoshino.logger.error('[ERROR]创建配置文件失败，请检查插件目录的读写权限及是否存在config.json。')
		traceback.print_exc()

# check group list if exist
glpath = os.path.join(os.path.dirname(__file__), 'grouplist.json')
if not os.path.exists(glpath):
	try:
		with open(glpath, 'w') as cfggl:
			json.dump(group_list_default, cfggl, ensure_ascii=False, indent=4)
			hoshino.logger.error('[WARNING]未找到黑白名单文件，已根据默认黑白名单模板创建。')
	except:
		hoshino.logger.error('[ERROR]创建黑白名单文件失败，请检查插件目录的读写权限。')
		traceback.print_exc()

# check group config if exist
gpcfgpath = os.path.join(os.path.dirname(__file__), 'groupconfig.json')
if not os.path.exists(gpcfgpath):
	try:
		with open(gpcfgpath, 'w') as gpcfg:
			json.dump(groupconfig_default, gpcfg, ensure_ascii=False, indent=4)
			hoshino.logger.error('[WARNING]未找到群个体设置文件，已创建。')
	except:
		hoshino.logger.error('[ERROR]创建群个体设置文件失败，请检查插件目录的读写权限。')
		traceback.print_exc()


# 生成配置文件后再进行读取配置文件的操作，否则会报错
from .config import get_config, get_group_config, get_group_info, set_group_config, group_list_check, set_group_list, get_grouplist
from .process import process_tags
from .message import SendMessageProcess
from . import utils


# 设置limiter
tlmt = hoshino.util.DailyNumberLimiter(get_config('base', 'daily_max'))
flmt = hoshino.util.FreqLimiter(get_config('base', 'freq_limit'))

# 获取默认tag
default_tags = get_config('default_tags', 'tags')

def check_lmt(uid, num, gid):
    if uid in hoshino.config.SUPERUSERS:
        return 0, ''
    if group_list_check(gid) != 0:
        if group_list_check(gid) == 1:
            return 1, f'此功能启用了白名单模式,本群未在白名单中,请联系维护组解决'
        else:
            return 1, f'此功能已在本群禁用,可能因为人数超限或之前有滥用行为,请联系维护组解决'
    if not tlmt.check(uid):
        return 1, f"您今天已经冲过{get_config('base', 'daily_max')}次了,请明天再来~"
    if num > 1 and (get_config('base', 'daily_max') - tlmt.get_num(uid)) < num:
        return 1, f"您今天的剩余次数为{get_config('base', 'daily_max') - tlmt.get_num(uid)}次,已不足{num}次,请少冲点(恼)!"
    if not flmt.check(uid):
        return 1, f'您冲的太快了,{round(flmt.left_time(uid))}秒后再来吧~'
    tlmt.increase(uid, num)
    flmt.start_cd(uid)
    return 0, ''


@sv.on_keyword(('图片鉴赏', '鉴赏图片', '生成tag', '生成tags'))
async def generate_tags(bot, ev):
    # uid = ev['user_id']
    # gid = ev['group_id']
    #
    # num = 1
    # result, msg = check_lmt(uid, num, gid)  # 检查群权限与个人次数
    # if result != 0:
    #     await bot.send(ev, msg)
    #     return
    try:
        msg_list = []
        image, _, _ = await utils.get_image_and_msg(bot, ev)
        if not image:
            await bot.send(ev, '请输入需要分析的图片', at_sender=True)
            return
        await bot.send(ev, f"正在生成tags，请稍后...")
        result_msg,error_msg = await utils.get_tags(image)
        if error_msg:
            await bot.send(ev, "鉴赏失败，服务器未返回图片数据", at_sender=True)
            traceback.print_exc()
            return
        else:
            msg_list.append("图片鉴赏结果为如下")
            msg_list.append(result_msg)
            await SendMessageProcess(bot, ev, msg_list, withdraw=False) # 发送消息过程
    except Exception as e:
        await bot.send(ev, f"鉴赏失败：{type(e)}", at_sender=True)
        traceback.print_exc()

@sv.on_keyword(('二次元化', '动漫化'))
async def animize(bot, ev):
    try:
        msg_list = []
        image, _, _ = await utils.get_image_and_msg(bot, ev)
        if not image:
            await bot.send(ev, '请输入需要分析的图片', at_sender=True)
            return
        await bot.send(ev, f"正在进入二次元，请稍后...")

        img_msg = await utils.cartoonization(image)
        if img_msg:
            msg_list.append(img_msg)
            await SendMessageProcess(bot, ev, msg_list) # 发送消息过程
        else:
            await bot.send(ev, '生成失败，图片被创死了！', at_sender=True)
            traceback.print_exc()
    except Exception as e:
        await bot.send(ev, f"已报错：{type(e)}", at_sender=True)
        traceback.print_exc()



@sv.on_keyword(('上传配方'))
async def upload_header(bot, ev):
    try:
        image, pic_hash, msg = await utils.get_image_and_msg(bot, ev) # 获取图片过程
        if not image:
            await bot.send(ev, "请输入要上传的图片", at_sender=True)
            return
        pic_dir,error_msg = await utils.save_pic(image, pic_hash)
        if len(error_msg):
            await bot.send(ev, f"已报错：{error_msg}", at_sender=True)
            return
        try:
            tags,seed,scale,strength,noise,ntags=clean_tags(msg)
            pic_msg = tags + f"&seed={seed}" + f"&scale={scale}"
            print(pic_msg)
        except:
            await bot.send(ev, '格式出错', at_sender=True)
            return
        try:
            resultmes = db.add_pic(ev.group_id, ev.user_id, pic_hash, str(pic_dir), pic_msg) # pic_dir是Path路径对象，必须转为str后数据库才能正常录入
            await bot.send(ev, resultmes, at_sender=True)
        except Exception as e:
            traceback.print_exc()
            await bot.send(ev, f"报错:{type(e)}",at_sender=True)
    except Exception as e:
        await bot.send(ev, f"已报错：{type(e)}", at_sender=True)
        traceback.print_exc()

@sv.on_rex((r'^(本群|个人|我的|全部|所有)配方+(\s?([0-9]\d*))?'))
async def check_pic(bot, ev):
    try:
        msg_list = []
        gid = ev.group_id
        uid = ev.user_id
        match = ev['match']
        msg = match.group(1)
        try:
            page = int(match.group(2).lstrip())
        except:
            page = 1
        resultmes,error_msg = await utils.check_pic_(gid,uid,msg,page)
        if len(error_msg):
            await bot.send(ev, f"已报错：{error_msg}", at_sender=True)
            return
            
        msg_list.append(resultmes)
        await SendMessageProcess(bot, ev, msg_list, withdraw=False) # 发送消息过程
    except Exception as e:
        await bot.send(ev, f"已报错：{type(e)}", at_sender=True)
        traceback.print_exc()

@sv.on_prefix(("点赞配方"))
async def img_thumb(bot, ev):
    try:
        id = ev.message.extract_plain_text().strip()
        if not id.isdigit() and '*' not in id:
            await bot.send(ev, '图片ID呢???')
            return
        msg = db.add_pic_thumb(id)
        await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, f"已报错：{type(e)}", at_sender=True)
        traceback.print_exc()

@sv.on_prefix(("删除配方"))
async def del_img(bot, ev):
    try:
        gid = ev.group_id
        uid = ev.user_id
        if not priv.check_priv(ev,priv.SUPERUSER):
            msg = "只有超管才能删除"
            await bot.send(ev, msg, at_sender=True)
            return
        id = ev.message.extract_plain_text().strip()
        if not id.isdigit() and '*' not in id:
            await bot.send(ev, '图片ID呢???')
            return
        db.del_pic(id)
        msg = f"已成功删除【{id}】号图片"
        await bot.send(ev, msg, at_sender=True)
    except ValueError as e:
        await bot.send(ev, f"已报错：【{id}】号图片不存在！",at_sender=True)
        traceback.print_exc()
        return
    except Exception as e:
        await bot.send(ev, f"报错:{type(e)}",at_sender=True)
        traceback.print_exc()

@sv.on_rex((r'^使用配方\s?([0-9]\d*)\s?(.*)'))
async def quick_img(bot, ev):
    try:
        msg_list = []

        gid = ev.group_id
        uid = ev.user_id
        match = ev['match']
        id = match.group(1)
        tags = match.group(2)
        msg = db.get_pic_data_id(id)
        (a,b) = msg
        msg = re.sub("&seed=[0-9]\d*", "", b, count=0, flags=0)
        tags +=f",{msg}"
        
        num = 1
        result, msg_ = check_lmt(uid, num, gid) # 检查群权限与个人次数
        if result != 0:
            await bot.send(ev, msg_)
            return
        await bot.send(ev, f"正在使用【{id}】号图片的配方进行绘图，请稍后...", at_sender=True)

        tags,error_msg,tags_guolv = await process_tags(gid,uid,tags) #tags处理过程
        if len(error_msg):
            msg_list.append(f"已报错：{error_msg}")
        if len(tags_guolv):
            msg_list.append(f"已过滤：{tags_guolv}")
        
        resultmes,error_msg = await utils.get_imgdata(tags)
        if len(error_msg):
            await bot.send(ev, f"已报错：{error_msg}", at_sender=True)
            return

        msg_list.append(resultmes)
        await SendMessageProcess(bot, ev, msg_list)
    except ValueError as e:
        await bot.send(ev, f"已报错：【{id}】号图片不存在！",at_sender=True)
        traceback.print_exc()
        return
    except Exception as e:
        await bot.send(ev, f"报错:{type(e)}",at_sender=True)
        traceback.print_exc()

@sv.on_prefix(('查看配方', '查看tag', '查看tags'))
async def get_img_peifang(bot, ev: CQEvent):
    try:
        msg_list = []
        id = ev.message.extract_plain_text().strip()
        if not id.isdigit() and '*' not in id:
            await bot.send(ev, '图片ID呢???没ID怎么查???')
            return
        msg = db.get_pic_data_id(id)
        (a,b) = msg
        msg = re.sub("&seed=[0-9]\d*", "", b, count=0, flags=0)
        tags = ""
        tags +=f"{msg}"
        msg_list.append(f"【{id}】号图片的配方如下")
        msg_list.append(tags)
        await SendMessageProcess(bot, ev, msg_list, withdraw=False)
    except ValueError as e:
        await bot.send(ev, f"已报错：【{id}】号图片不存在！",at_sender=True)
        traceback.print_exc()
    except Exception as e:
        await bot.send(ev, f"报错:{type(e)}",at_sender=True)
        traceback.print_exc()

@sv.on_keyword(('清晰术'))
async def image4x(bot, ev):
    if get_config("image4x", "Real-CUGAN"):
        await img_Real_CUGAN(bot, ev)
    elif get_config("image4x", "Real-ESRGAN"):
        await img_Real_ESRGAN(bot, ev)
    else:
        await bot.send(ev, "已报错：Real-CUGAN与Real-ESRGAN超分模型均未开启！", at_sender=True)

async def img_Real_CUGAN(bot, ev):
    try:
        msg_list = []
        image, _, _ = await utils.get_image_and_msg(bot, ev)
        if not image:
            await bot.send(ev, '请输入需要超分的图片', at_sender=True)
            return
        ix=image.size[0] # 获取图片宽度
        iy=image.size[1] # 获取图片高度
        if ix * iy > 1500000: # 图片像素大于150万像素的，会对其进行缩放
            image.thumbnail(size=(1300, 1300)) # 图片等比例缩放
            await bot.send(ev, f"图片尺寸超过150万像素，将对其进行缩放", at_sender=True)
        msg = ev.message.extract_plain_text().strip()
        try:
            if "二倍放大" in msg or "2倍放大" in msg:
                scale = 2
            elif "三倍放大" in msg or "3倍放大" in msg:
                scale = 3
            elif "四倍放大" in msg or "4倍放大" in msg:
                scale = 4
            else:
                scale = 2 # 如不指定放大倍数，则默认放大2倍

            if "保守降噪" in msg:
                con = "conservative"
                con_cn = "保守"
            elif "强力降噪" in msg or "三级降噪" in msg or "3级降噪" in msg:
                con = "denoise3x"
                con_cn = "3级"
            elif "不降噪" in msg:
                con = "no-denoise"
                con_cn = "不降噪"
            else:
                con = "denoise3x" # 如不指定降噪等级，默认3倍降噪
                con_cn = "3级"
            modelname = f"up{scale}x-latest-{con}.pth"
            await bot.send(ev, f"放大倍率：{scale}倍    降噪等级：{con_cn}\n正在进行图片超分，请稍后...")
        except Exception as e:
            await bot.send(bot, ev, f"超分参数输入错误：{type(e)}")
            return
        img_msg = await utils.get_Real_CUGAN(image, modelname)

        if img_msg:
            msg_list.append(f"放大倍率：{scale}倍\n降噪等级：{con_cn}\n使用模型：Real_CUGAN")
            msg_list.append(img_msg)
            await SendMessageProcess(bot, ev, msg_list) # 发送消息过程
        else:
            await bot.send(ev, "清晰术失败，服务器未返回图片数据", at_sender=True)
            traceback.print_exc()
    except Exception as e:
        await bot.send(ev, f"清晰术失败：{type(e)}", at_sender=True)
        traceback.print_exc()

async def img_Real_ESRGAN(bot, ev):
    try:
        msg_list = []
        image, _, _ = await utils.get_image_and_msg(bot, ev)
        if not image:
            await bot.send(ev, '请输入需要超分的图片', at_sender=True)
            return
        ix=image.size[0] # 获取图片宽度
        iy=image.size[1] # 获取图片高度
        if ix * iy > 1500000: # 图片像素大于150万像素的，会对其进行缩放
            image.thumbnail(size=(1300, 1300)) # 图片等比例缩放
            await bot.send(ev, f"图片尺寸超过150万像素，将对其进行缩放", at_sender=True)
        await bot.send(ev, f"正在使用Real-ESRGAN模型4倍超分图片，请稍后...")

        img_msg = await utils.get_Real_ESRGAN(image)
        if img_msg:
            msg_list.append("放大倍率：4倍\n使用模型：Real-ESRGAN")
            msg_list.append(img_msg)
            await SendMessageProcess(bot, ev, msg_list) # 发送消息过程
        else:
            await bot.send(ev, '清晰术失败，服务器未返回图片数据', at_sender=True)
            traceback.print_exc()
    except Exception as e:
        await bot.send(ev, f"清晰术失败：{type(e)}", at_sender=True)
        traceback.print_exc()

@sv.on_prefix("元素法典")
async def magic_book(bot, ev):
    try:
        uid = ev['user_id']
        gid = ev['group_id']
        msg_list = []
        msg = ev.message.extract_plain_text().strip()
        if msg=='':
            await bot.send(ev, f"请在指令后面输入想使用的魔法\n查看元素法典请使用‘元素法典目录’", at_sender=True)
            return
        print(msg)
        if msg=='目录':
            text='\n'
            for i in ysfd:
                text+=' '+i
            await bot.send(ev, f"{text}", at_sender=True)
            return
        tags, error_msg, node_msg, dark_msg = await magic.get_magic_book_(msg)
        if len(error_msg):
            await bot.send(ev, f"已报错：{error_msg}", at_sender=True)
            return

        num = 1
        result, msg = check_lmt(uid, num, gid) # 检查群权限与个人次数
        if result != 0:
            await bot.send(ev, msg)
            return
        if dark_msg:
            await bot.send(ev, f"{dark_msg}正在进行魔法绘图，请稍后...\n(今日剩余{get_config('base', 'daily_max') - tlmt.get_num(uid)}次)", at_sender=True)
        else:
            await bot.send(ev, f"元素法典已注入，正在进行魔法绘图，请稍后...\n(今日剩余{get_config('base', 'daily_max') - tlmt.get_num(uid)}次)", at_sender=True)

        result_msg,error_msg = await utils.get_imgdata_magic(tags)
        if len(error_msg):
            await bot.send(ev, f"已报错：{error_msg}", at_sender=True)
            return
        msg_list.append(result_msg)
        msg_list.append(node_msg)
        await SendMessageProcess(bot, ev, msg_list) # 发送消息过程
    except Exception as e:
        await bot.send(ev, f"已报错：{type(e)}", at_sender=True)
        traceback.print_exc()



@sv.scheduled_job('cron', hour='2', minute='36')
async def set_ban_list():
    ban_list = []
    group_info = await get_group_info(info_type='member_count')
    for group in group_info:
        group_info[group] = int(group_info[group])
        if group_info[group] >= int(get_config('base', 'ban_if_group_num_over')):
            ban_list.append(group)
        else:
            pass
    set_group_list(ban_list, 1, 0)


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
    tags =re.sub("上传配方", '',tags)
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
        ntags='multiple breasts,(mutated hands and fingers:1.5),(long body:1.3),(mutation,poorly drawn:1.2),black-white,bad anatomy,liquid body,liquid tongue,disfigured,malformed,mutated,anatomical nonsense,text font ui,error,malformed hands,long neck,blurred,lowers,lowres,bad anatomy,bad proportions,bad shadow,uncoordinated body,unnatural body,fused breasts,bad breasts,huge breasts,poorly drawn breasts,extra breasts,liquid breasts,heavy breasts,missing breasts,huge haunch,huge thighs,huge calf,bad hands,fused hand,missing hand,disappearing arms,disappearing thigh,disappearing calf,disappearing legs, fused ears, bad ears, poorly drawn ears, extra ears, liquid ears, heavy ears, missing ears, fused animal ears, bad animal ears, poorly drawn animal ears, extra animal ears, liquid animal ears, heavy animal ears, missing animal ears, text, ui, error, missing fingers, missing limb, fused fingers, one hand with more than 5 fingers, one hand with less than 5 fingers, one hand with more than 5 digit, one hand with less than 5 digit, extra digit, fewer digits,fused digit,missing digit,bad digit,liquid digit,colorful tongue,black tongue,cropped,watermark,username,blurry,JPEG artifacts,signature,3D,3D game, 3D game scene,3D character,malformed feet,extra feet,bad feet,poorly drawn feet,fused feet,missing feet,extra shoes,bad shoes,fused shoes,more than two shoes,poorly drawn shoes,bad gloves,poorly drawn gloves,fused gloves,bad cum,poorly drawn cum,fused cum,bad hairs,poorly drawn hairs,fused hairs,big muscles,ugly,bad face,fused face,poorly drawn face,cloned face, big face, long face, bad eyes, fused eyes poorly drawn eyes, extra eyes, malformed limbs,more than 2 nipples,missing nipples,different nipples,fused nipples,bad nipples,poorly drawn nipples,black nipples,colorful nipples,short arm,(((missing arms))),missing thighs,missing calf,missing legs,mutation,duplicate,morbid,mutilated,poorly drawn hands,more than 1 left hand,more than 1 right hand,deformed,(blurry),disfigured,missing legs,extra arms,extra thighs,more than 2 thighs,extra calf,fused calf,extra legs,bad knee,extra knee,more than 2 legs,bad tails,bad mouth,fused mouth,poorly drawn mouth,bad tongue,tongue within mouth,too long tongue,black tongue, big mouth,cracked mouth,bad mouth,dirty face,dirty teeth,dirty pantie,fused pantie,poorly drawn pantie,fused cloth,poorly drawn cloth,bad pantie,yellow teeth,thick lips,bad cameltoe,colorful cameltoe,bad asshole,poorly drawn asshole,fused asshole,missing asshole,bad anus,bad pussy,bad crotch,bad crotch seam,fused anus,fused pussy,fused anus,fused crotch,poorly drawn crotch,fused seam,poorly drawn anus,poorly drawn pussy,poorly drawn crotch,poorly drawn crotch seam,bad thigh gap,missing thigh gap,fused thigh gap,liquid thigh gap,poorly drawn thigh gap,poorly drawn anus,bad collarbone,fused collarbone,missing collarbone,liquid collarbone,strong girl,obesity,worst quality,low quality,normal quality,liquid tentacles,bad tentacles,poorly drawn tentacles,split tentacles,fused tentacles,missing clit,bad clit,fused clit,colorful clit,black clit,liquid clit,QR code,bar code,censored,safety panties,safety knickers,beard,furry,pony,pubic hair,mosaic,excrement,faeces,shit,futa,testis'
    tags=tags.strip()  
    return tags,seed,scale,strength,noise,ntags