from blacklist import *
from crawl_assist import *
from crawl import *

if __name__ == '__main__':
    blacklist = Blacklist()
    crawl = Crawl()

    # print(blacklist.is_in_blacklist('abc'))
    # print(blacklist.is_in_blacklist('ltr9'))
    # blacklist.add_blackname('kkkkk')

    # print(CrawlAssist.is_valid('----'))
    # print(CrawlAssist.is_crawled('aaa'))

    crawl_assist = CrawlAssist()
    user_id_usernames = crawl_assist.get_user_id_names()

    start = 11460
    end = 11535
    cur = start + 1
    for user_id, username in user_id_usernames[start: end]:
        print('总共：', end, '，当前：', cur)
        cur += 1
        if blacklist.is_in_blacklist(username):
            print(username, '在黑名单中')
            continue

        if CrawlAssist.is_valid(username) and not CrawlAssist.is_crawled(user_id):

            crawl.crawl_by_username(username)
            if crawl.is_black:
                blacklist.add_blackname(username)
            else:
                CrawlAssist.save_jsons_to_txt(user_id, crawl.encoded_jsons)
        else:
            print(username, '用户名非法，或者已爬取')
    pass