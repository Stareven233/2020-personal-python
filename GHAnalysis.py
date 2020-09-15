# -*- coding: utf-8 -*-

"""
初始化：
    input: python3 GHAnalysis.py -i data
    output: 0
测试：
    input: python3 GHAnalysis.py -e PushEvent -u waleko
    output: 2
    input: python3 GHAnalysis.py -r katzer/cordova-plugin-background-mode -e PushEvent
    output: 6
    input: python3 GHAnalysis.py -u cdupuis -r atomist/automation-client -e PushEvent
    output: 2
"""

import os
import argparse
import pickle
import re

# todo 一边re一边计数
# todo 尝试去掉多个get_函数

EVENTS = ("PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent", )
pattern = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?repo.*?"name":"(\S+?)"')
# pattern = re.compile('.*?((?:%s)Event).*?actor.*?"login":"(\\S+?)".*?repo.*?"name":"(\\S+?)"' % '|'.join(EVENTS))
# 正则太长?使用了|多次?会变得特别慢


class Data:
    def __init__(self):
        self.user_events = {}
        self.repo_events = {}
        self.user_repo_events = {}

    # @staticmethod
    # def __parse(file_path: str):
    #     """
    #     从json文件中逐行抽取所需信息元组(event, user, repo)
    #     """
    #     records = []
    #     with open(file_path, 'r', encoding='utf-8') as f:
    #         for line in f:
    #             res = pattern.search(line)
    #             if res is None or res[1] not in EVENTS:
    #                 continue
    #             records.append(res.groups())
    #     return records

    def __count_events(self, file_path: str):
        """
        从json文件中逐行抽取所需信息元组(event, user, repo)，并写入字典
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                res = pattern.search(line)
                if res is None or res[1] not in EVENTS:
                    continue

                event, user, repo = res.groups()
                self.user_events.setdefault(user, {})
                self.user_repo_events.setdefault(user, {})
                self.repo_events.setdefault(repo, {})
                self.user_repo_events[user].setdefault(repo, {})

                self.user_events[user][event] = self.user_events[user].get(event, 0)+1
                self.repo_events[repo][event] = self.repo_events[repo].get(event, 0)+1
                self.user_repo_events[user][repo][event] = self.user_repo_events[user][repo].get(event, 0)+1

    def init(self, dir_path: str):
        # records = []
        for cur_dir, sub_dir, filenames in os.walk(dir_path):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            for name in filenames:
                # records.extend(self.__parse(f'{cur_dir}/{name}'))
                self.__count_events(f'{cur_dir}/{name}')

        # for record in records:
            # event, user, repo = record
            #
            # self.user_events.setdefault(user, {})
            # self.user_repo_events.setdefault(user, {})
            # self.repo_events.setdefault(repo, {})
            # self.user_repo_events[user].setdefault(repo, {})
            #
            # self.user_events[user][event] = self.user_events[user].get(event, 0)+1
            # self.repo_events[repo][event] = self.repo_events[repo].get(event, 0)+1
            # self.user_repo_events[user][repo][event] = self.user_repo_events[user][repo].get(event, 0)+1

        with open('0.json', 'wb') as f:
            pickle.dump(self.user_events, f)
        with open('1.json', 'wb') as f:
            pickle.dump(self.repo_events, f)
        with open('2.json', 'wb') as f:
            pickle.dump(self.user_repo_events, f)

    def load(self):
        if not any((os.path.exists(f'{i}.json') for i in range(3))):
            raise RuntimeError('error: data file not found')

        with open('0.json', 'rb') as f:
            self.user_events = pickle.load(f)
        with open('1.json', 'rb') as f:
            self.repo_events = pickle.load(f)
        with open('2.json', 'rb') as f:
            self.user_repo_events = pickle.load(f)

    # def get_user_event(self, user: str, event: str) -> int:
    #     return self.user_events.get(user, {}).get(event, 0)
    #
    # def get_repo_event(self, repo: str, event: str) -> int:
    #     return self.repo_events.get(repo, {}).get(event, 0)
    #
    # def get_user_repo_event(self, user: str, repo: str, event: str) -> int:
    #     return self.user_repo_events.get(user, {}).get(repo, {}).get(event, 0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = Data()
        self.arg_init()

    def arg_init(self):
        self.parser.add_argument('-i', '--init', type=str)
        self.parser.add_argument('-u', '--user', type=str)
        self.parser.add_argument('-r', '--repo', type=str)
        self.parser.add_argument('-e', '--event', type=str)

    def analyse(self):
        args = self.parser.parse_args()

        # self.data = Data()
        if args.init:
            self.data.init(args.init)
            return 'init done'
        self.data.load()

        if not args.event:
            raise RuntimeError('error: the following arguments are required: -e/--event')
        if not args.user and not args.repo:
            raise RuntimeError('error: the following arguments are required: -u/--user or -r/--repo')

        if args.user and args.repo:
            res = self.data.user_repo_events.get(args.user, {}).get(args.repo, {}).get(args.event, 0)
        elif args.user:
            res = self.data.user_events.get(args.user, {}).get(args.event, 0)
        else:
            res = self.data.repo_events.get(args.repo, {}).get(args.event, 0)
        return res


if __name__ == '__main__':
    a = Run()
    print(a.analyse())
