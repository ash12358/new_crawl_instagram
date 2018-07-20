import os


class CrawlAssist(object):
    def __init__(self):
        self.user_id_names = []
        pass

    @staticmethod
    def is_valid(username):
        if username == '----':
            return False
        else:
            return True

    @staticmethod
    def is_crawled(user_id):
        if os.path.exists('./jsons/' + user_id + '.txt'):
            return True
        else:
            return False

    def get_user_id_names(self):
        with open('./user_id_usernames.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.user_id_names = [line.strip().split('|') for line in lines]
        return self.user_id_names

    @staticmethod
    def save_jsons_to_txt(user_id, encoded_jsons):
        with open('./jsons/' + user_id + '.txt', 'w', encoding='utf-8') as f:
            for json in encoded_jsons:
                f.write(json + '\n')
        print('保存至', './jsons/' + user_id + '.txt')
