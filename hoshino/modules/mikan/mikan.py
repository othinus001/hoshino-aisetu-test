def img_safe_coin(paid=28):
       if not is_number(paid):#如果strength不是数字
          paid=0.4
       paid=float(paid)
       if paid >0.54:         #控制strength在0.4-0.54之间，高了用不起
          paid=0.54
       if paid <0.4:
          paid=0.4
       print(paid)

def is_number(s):       #判断是否是数字
    try:                # 如果能运行float(s)语句，返回True（字符串s是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情
    try:
        import unicodedata  # 处理ASCii码的包
        unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
    return False
img_safe_coin(paid='pppp')

