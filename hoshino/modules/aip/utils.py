from json import loads
from base64 import b64encode, b64decode
import aiohttp

######### 实现对图片的base64编码和从返回数据中解析出原始图片 #########


def img_encode_to_json(img: bytes) -> dict:
    '''
    对二进制格式的图片进行base64编码，并组织成json格式返回，用于request请求
    Args:
        img (bytes): 二进制格式图片
    Returns:
        dict: 返回的json数据
    '''
    base64_data = b64encode(img)
    base64_data = str(base64_data, 'utf-8')
    try:
        img={'data': ['data:image/png;base64,{}'.format(base64_data),'up2x-latest-denoise1x.pth',4]}
    except Exception as e:
           print('错误类型是', e)
    return img


def img_decode_from_json(response_str) -> bytes:
    ##########[0].split("base64,")[0][1]
    aaa_b64=''
    result = loads(str(response_str).replace("'", "\""))
    try:
        aaa_b64=result['data'][0].split("base64,")[1]
    except Exception as e:
           print('错误是', e)                  
    return b64decode(aaa_b64)


######### 网络请求部分 #########

async def get_result(json_data: dict,url) -> str:
    '''
    来构造请求并获取返回的重建后的图像
    Args:
        json_data (dict): 对图片编码后的数据
    Returns:
        str: 返回的json格式数据
    '''
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=json_data, timeout=120) as resp:
                result = await resp.text()
        if not result:
            return None
        return result
    except:
        return None
