import requests
import os
import re


count = 0


def get_page(offset):
    """
    从目标URL获取json数据
    :param offset: 偏移量，从offset开始获取offset to offset+20的数据
    :return: 从目标URL获取到的json数据(dict类型)
    """
    params = {
        'aid': 24,
        'app_name': 'web_search',
        'autoload': 'true',
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'count': 20
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.86 Safari/537.36'
    }

    try:
        response = requests.get('https://www.toutiao.com/api/search/content/', headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_image_info(all_data):
    """
    从传入的数据中提取图片贴子的title和图片链接
    :param all_data: 从URL获取到的数据
    :return: 一个字典，包含title、image
    """
    results = []
    if all_data.get('data'):
        for item in all_data.get('data'):
            if item.get('abstract'):
                title = item.get('title')
                images = item.get('image_list')
                result = {'title': title, 'images': images}
                results.append(result)
    return results


def get_image(url):
    """
    获取图片
    :param url: 图片的url
    :return: 图片的二进制数据
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.86 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
    except requests.ConnectionError:
        print("error")
    return None


def save_images(results):
    """
    获取图片并保存在帖子标题的文件夹中
    :param results: 标题与图片链接的键值对
    :return: None
    """
    # 去除标题中的\|/符号和空格，以前10个字符作为文件夹的标题
    global count
    pattern = re.compile(r'\\|\||/')
    for result in results:
        dir_name = re.sub(pattern, "", result.get('title')[:20]).strip()

        if not os.path.exists(".\\"+dir_name):
            os.mkdir(".\\"+dir_name)
        for image_url in result.get('images'):
            image = get_image(image_url['url'])
            if image:
                with open(".\\"+dir_name+"\\"+str(hash(image))+".jpg", 'wb') as f:
                    f.write(image)
                    count += 1
                    print("已爬取{}张图片".format(count))


if __name__ == '__main__':
    # 调整此项大小来修改获取图片的组数
    groups = 20
    
    for offset in range(groups):
        page = get_page(offset*20)
        results = get_image_info(page)
        save_images(results)
