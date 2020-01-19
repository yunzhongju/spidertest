import requests
import time
# 小红书
# 	爬取源：博主吴昕最新的5条笔记的全部内容
# 	需求字段：标题，发布时间，视频内容/文本内容，
# 		点赞，收藏和评论的用户信息（id，昵称），评论内容

headers = {
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MuMu Build/V417IR) Resolution/810*1440 Version/6.0.1 Build/6001002 Device/(Netease;MuMu) NetType/WiFi',
    'Host': 'www.xiaohongshu.com',
    'Authorization': 'session.1575956991298113170894',
    'device_id': 'ae9dd2b2-e1c2-374f-a21f-c2348cb27532',
    'shield': '977bccf2416424a9217b150c9f844a4f'
}

url = 'https://www.xiaohongshu.com/api/sns/v9/search/notes'
params = {
    'keyword': '吴昕',
    'filters': '[]',
    'sort': 'time_descending',
    'page': '1',
    'page_size': '20',
    'source': 'explore_feed',
    'search_id': 'D905519A5593513A3F6A4D38E151FF12@7FB3419624757027EFDB08B11A939F62',
    'api_extra': '',
    'page_pos': '0',
    'allow_rewrite': '1',
    'platform': 'android',
    'deviceId': 'ae9dd2b2-e1c2-374f-a21f-c2348cb27532',
    'device_fingerprint': '20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada',
    'device_fingerprint1': '20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada',
    'versionName': '6.0.1',
    'channel': 'YingYongBao',
    'sid': 'session.1575956991298113170894',
    'lang': 'zh-Hans',
    't': 1576041428,
    'fid': '',
    'sign': '100707c605069b616a76051cce599a41',
}
# 详情
header = {
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MuMu Build/V417IR) Resolution/810*1440 Version/6.0.1 Build/6001002 Device/(Netease;MuMu) NetType/WiFi',
    'Host': 'www.xiaohongshu.com',
    'Authorization': 'session.1575956991298113170894',
    'device_id': 'ae9dd2b2-e1c2-374f-a21f-c2348cb27532',
    'shield': '680a56953c36b35c3f55e38c77ea60bb'
}
# 评论
header2 = {
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MuMu Build/V417IR) Resolution/810*1440 Version/6.0.1 Build/6001002 Device/(Netease;MuMu) NetType/WiFi',
    'Host': 'www.xiaohongshu.com',
    'Authorization': 'session.1575956991298113170894',
    'device_id': 'ae9dd2b2-e1c2-374f-a21f-c2348cb27532',
    'shield': 'b7db5458ee8bbbe898c52baf9f00a077'
}
response = requests.get(url, headers=headers, verify=True, params=params)
html = response.json()
data = html['data']['notes']
for each in range(5):
    t_id = data[each]['id']
    text_type = data[each]['type']
    title = data[each]['title']
    if text_type == 'video':
        video_info = data[each]['video_info']['url']
        v_url = 'https://www.xiaohongshu.com/api/sns/v2/note/' + t_id + '/videofeed?page=1&num=5&fetch_mode=3&source=search&ads_track_id=&platform=android&deviceId=ae9dd2b2-e1c2-374f-a21f-c2348cb27532&device_fingerprint=20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada&device_fingerprint1=20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada&versionName=6.0.1&channel=YingYongBao&sid=session.1575956991298113170894&lang=zh-Hans&t=1576043489&fid=&sign=7270efb62c66e0cdf974cfd025c90e4c'
        v_response = requests.get(v_url, headers=header, verify=False)
        # print('detail:', v_response.text)
        detail_data = v_response.json()['data'][0]
        desc = detail_data['desc']
        liked_count = detail_data['liked_count']  # 点赞数
        collected_count = detail_data['collected_count']  # 收藏数
        comments_count = detail_data['comments_count']  # 评论数
        print('描述：', desc)
        print('点赞数：', liked_count)
        print('收藏数：', collected_count)
        print('评论数：', comments_count)
        print('视频连接', video_info)
        with requests.get(video_info, stream=True) as r:
            chunk_size = 1024  # 数据块的大小
            print('下载开始。。。')
            with open('./data/'+title+'.mp4', "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
        print('下载结束。。。')
    else:
        text_url = 'https://www.xiaohongshu.com/api/sns/v1/note/' + t_id + '/feed?page=1&num=5&fetch_mode=3&source=search%26keyword%3D%E5%90%B4%E6%98%95&ads_track_id=&platform=android&deviceId=ae9dd2b2-e1c2-374f-a21f-c2348cb27532&device_fingerprint=20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada&device_fingerprint1=20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada&versionName=6.0.1&channel=YingYongBao&sid=session.1575956991298113170894&lang=zh-Hans&t=1576048223&fid=&sign=5c2c9a076d7c099e2646228c688410a4'
        text_response = requests.get(text_url, headers=header, verify=False)
        # print('detail_text:', text_response.text)
        text_data = text_response.json()['data'][0]
        text_desc = text_data['note_list'][0]['desc']
        liked_count = text_data['note_list'][0]['liked_count']  # 点赞数
        collected_count = text_data['note_list'][0]['collected_count']  # 收藏数
        comments_count = text_data['note_list'][0]['comments_count']  # 评论数
        print('内容：', text_desc)
        print('点赞数:', liked_count)
        print('收藏数:', collected_count)
        print('评论数:', comments_count)
        print('=*'*30)
    com_url = 'https://www.xiaohongshu.com/api/sns/v5/note/' + t_id + '/comment/list?start=&num=20&show_priority_sub_comments=0&platform=android&deviceId=ae9dd2b2-e1c2-374f-a21f-c2348cb27532&device_fingerprint=20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada&device_fingerprint1=20191209205221c5e659f7f05bc14026a86df2429d297e01cbc3e8bff2dada&versionName=6.0.1&channel=YingYongBao&sid=session.1575956991298113170894&lang=zh-Hans&t=1576046621&fid=&sign=00cb9d3904fa13d14a94eace491178d2'
    com_response = requests.get(com_url, headers=header2, verify=False)
    # print('comments', com_response.text)
    com_data = com_response.json()['data']['comments']
    for comment in com_data:
        content = comment['content']  # 评论内容
        user_id = comment['user']['userid']  # 评论用户id
        nickname = comment['user']['nickname']  # 评论用户
        print('评论用户：', nickname)
        print('评论用户的id', user_id)
        print('评论内容：', content)
        print('-=' * 30)

    print('标题：', title)
    print('ID', t_id)
    print('=*' * 20)
