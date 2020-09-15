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
from concurrent.futures import ThreadPoolExecutor

# todo 使用多线程io

EVENTS = ("PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent", )
pattern = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?repo.*?"name":"(\S+?)"')


class Data:
    def __init__(self):
        self.user_events = {}
        self.repo_events = {}
        self.user_repo_events = {}

    def __count_events(self, filename: str):
        """
        从单个json文件中逐行抽取所需信息元组(event, user, repo)，并写入字典
        """
        with open(filename, 'r', encoding='utf-8') as f:
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
        pool = ThreadPoolExecutor()
        # 近600M数据，单线程2.5s, 默认(40?)线程3.5s
        for cur_dir, sub_dir, filenames in os.walk(dir_path):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            for name in filenames:
                # self.__count_events(f'{cur_dir}/{name}')
                pool.submit(self.__count_events, f'{cur_dir}/{name}')
        pool.shutdown()

        with open('0.pkl', 'wb') as f:
            pickle.dump(self.user_events, f)
        with open('1.pkl', 'wb') as f:
            pickle.dump(self.repo_events, f)
        with open('2.pkl', 'wb') as f:
            pickle.dump(self.user_repo_events, f)

    def load(self):
        if not any((os.path.exists(f'{i}.pkl') for i in range(3))):
            raise RuntimeError('error: data file not found')

        with open('0.pkl', 'rb') as f:
            self.user_events = pickle.load(f)
        with open('1.pkl', 'rb') as f:
            self.repo_events = pickle.load(f)
        with open('2.pkl', 'rb') as f:
            self.user_repo_events = pickle.load(f)


class Run:
    def __init__(self):
        self.data = Data()
        self.parser = argparse.ArgumentParser()
        self.args_init()

    def args_init(self):
        self.parser.add_argument('-i', '--init', type=str)
        self.parser.add_argument('-u', '--user', type=str)
        self.parser.add_argument('-r', '--repo', type=str)
        self.parser.add_argument('-e', '--event', type=str)

    def analyse(self):
        args = self.parser.parse_args()
        event, user, repo = args.event, args.user, args.repo

        if args.init:
            self.data.init(args.init)
            return 'init done'
        self.data.load()

        if not event:
            raise RuntimeError('error: the following arguments are required: -e/--event')
        if not user and not repo:
            raise RuntimeError('error: the following arguments are required: -u/--user or -r/--repo')

        if user and repo:
            res = self.data.user_repo_events.get(user, {}).get(repo, {}).get(event, 0)
        elif user:
            res = self.data.user_events.get(user, {}).get(event, 0)
        else:
            res = self.data.repo_events.get(repo, {}).get(event, 0)
        return res


if __name__ == '__main__':
    a = Run()
    print(a.analyse())
