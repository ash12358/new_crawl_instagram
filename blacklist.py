

class Blacklist(object):
    def __init__(self):
        self.blacklist = []
        with open('./blacklist.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.blacklist = [line.strip() for line in lines]

    def is_in_blacklist(self, username):
        if username in self.blacklist:
            return True
        else:
            return False

    def add_blackname(self, username):
        self.blacklist.append(username)
        self.save_to_txt()
        print('更新黑名单', username)

    def save_to_txt(self):
        with open('./blacklist.txt', 'w', encoding='utf-8') as f:
            for line in self.blacklist:
                f.write(line + '\n')
