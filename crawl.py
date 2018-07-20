import os
import re
import requests
import json
from lxml import etree
from urllib import parse
from utils import *

class Crawl(object):
    def __init__(self):
        self.PAT = re.compile(r'queryId:"(.+?)",', re.MULTILINE)
        self.headers = {
            "Origin": "https://www.instagram.com/",
            "Referer": "https://www.instagram.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
            "Host": "www.instagram.com",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, sdch, br",
            "accept-language": "zh-CN,zh;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Upgrade-Insecure-Requests": "1",
        }

        self.jso = {"id": "", "first": 12, "after": ""}

        self.BASE_URL = "https://www.instagram.com"

        self.NEXT_URL = 'https://www.instagram.com/graphql/query/?query_hash={0}&variables={1}'

        self.username = None

        self.is_black = False

        self.encoded_jsons = []

        self.qq = None

    def define_request(self, url):
        ties = 10
        while ties > 0:
            try:
                res = self.qq.get(url=url, headers=self.headers, timeout=5)
                if res.status_code == 200:
                    res.encoding = "utf-8"
                    return res
            except:
                ties -= 1
                print('倒数第%d次尝试' % ties)

    def crawl_next(self, html, query_id_url, rhx_gis, id):
        print('下一页')

        edges = html["user"]["edge_owner_to_timeline_media"]["edges"]
        end_cursor = \
            html["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        has_next = \
            html["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]

        self.extract_from_edges(edges)

        # query_content = qq.get(BASE_URL + query_id_url[1])
        query_content = self.define_request(self.BASE_URL + query_id_url[1])
        query_id_list = self.PAT.findall(query_content.text)

        self.jso["id"] = id
        self.jso["first"] = 12
        self.jso["after"] = end_cursor
        # 注意了这处dumps默认会出都自动在，逗号和冒号后面添加空格，导致了格式不符合
        text = json.dumps(self.jso, separators=(',', ':'))
        xhr_code = "{0}:{1}".format(rhx_gis, text)
        # print(xhr_code)
        # for query_hash in query_id_list:
        # query_hash = "472f257a40c653c64c666ce877d59d2b"
        query_hash = query_id_list[2]
        url = self.NEXT_URL.format(query_hash, parse.quote(text))
        # print(url)
        gis = ctx.call("get_gis", xhr_code)
        # 就是缺少了这个GIS参数
        self.headers.setdefault("X-Instagram-GIS", gis)
        self.headers.update({"X-Instagram-GIS": gis})

        # res = qq.get(url=url, headers=headers)
        res = self.define_request(url)

        try:
            html = json.loads(res.content.decode(), encoding='utf-8')

            if has_next and len(self.encoded_jsons) < 200:
                self.crawl_next(html['data'], query_id_url, rhx_gis, id)
            else:
                print('has_next', has_next)
                print('len,', len(self.encoded_jsons))

                if len(self.encoded_jsons) == 0:
                    self.is_black = True
        except:
            print('encoding error --------------')
            pass

    def convert_text_to_a_line(self, text):
        texts = text.split('\n')
        text = ''
        for te in texts:
            text += te.strip()
            if len(te.strip()) > 0:
                text += ' '
        text = text[:-1]
        return text

    def extract_from_edges(self, edges):

        print('提取图片')

        for edge in edges:

            if not edge['node']['is_video']:
                encoded_json = json.dumps(edge, separators=(',', ':'))
                self.encoded_jsons.append(encoded_json)
                if len(self.encoded_jsons) >= 200:
                    break

                # img_url = edge["node"]["display_url"]
                #
                # # img_url = convert_text_to_a_line(img_url)
                # edges_for_text = edge['node']['edge_media_to_caption']['edges']
                # text = ''
                # if edges_for_text and len(edges_for_text) > 0:
                #     text = edges_for_text[0]['node']['text']
                #     text = convert_text_to_a_line(text)
                # if len(img_url_texts.keys()) < 200:
                #     img_url_texts[img_url] = text
                #     encoded_json = json.dumps(edge, separators=(',', ':'))
                #     encoded_jsons.append(encoded_json)
                # else:
                #     break

                # print('phtot, save')
            else:
                # print('video, pass')
                pass

        # 直接将json数据保存下来

    def crawl_first(self):
        print('进入主页')
        self.qq = requests.session()
        query = self.username
        temp_url = self.BASE_URL + '/' + query + '/'
        global_url = temp_url
        self.headers.update({'Referer': temp_url})
        # res = qq.get(url=temp_url, headers=headers)

        print('请求res')
        res = self.define_request(temp_url)
        print(res.status_code)

        html = etree.HTML(res.content.decode())
        all_a_tags = html.xpath('//script[@type="text/javascript"]/text()')  # 图片数据源
        query_id_url = html.xpath('//script[@type="text/javascript"]/@src')  # query_id 作为内容加载

        js_data = None
        rhx_gis = None
        for a_tag in all_a_tags:
            if 'window._sharedData' in str(a_tag.strip()) and 'window._sharedData)' not in str(a_tag.strip()):
                data = a_tag.split('= {')[1][:-1]  # 获取json数据块
                try:
                    js_data = json.loads('{' + data, encoding='utf-8')
                    rhx_gis = js_data["rhx_gis"]
                    id = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
                    edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"][
                        "edges"]
                    # self.extract_from_edges(edges)
                    self.crawl_next(js_data["entry_data"]["ProfilePage"][0]["graphql"], query_id_url, rhx_gis, id)
                except:
                    print('encoding error ---------------')
                #     pass
        self.qq.close()

        pass

    def crawl_by_username(self, username):
        self.is_black = False
        self.encoded_jsons = []
        self.qq = None
        self.username = username
        print('开始爬取', self.username)

        self.crawl_first()
        # save_to_txt(username)
        # 现在不保存到txt中，而是保存到mongodb中，所以需要将该用户的信息按照字典格式返回

        # pass
        pass