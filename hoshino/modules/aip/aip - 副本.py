@sv.on_fullmatch(('生成帮助'))
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
    draw.text((87,1440),  text4, font=font3, fill="#d46b08") 
    draw.text((87,1540),  text5, font=font2, fill="#00474f") 
    draw.text((87,2050),  text6, font=font3, fill="#00474f") 
    draw.text((87,2300),  text7, font=font3, fill="#007175") 
    image.save(os.path.join(os.path.dirname(__file__),f"list2.png"))
    list2=os.path.join(os.path.dirname(__file__),f"list2.png")
    await bot.send(ev, MessageSegment.image(f'file:///{list2}'))
