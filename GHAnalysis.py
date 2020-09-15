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
from multiprocessing import Manager, Pool, cpu_count

# todo 使用多进程io

EVENTS = ("PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent", )
pattern = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?repo.*?"name":"(\S+?)"')


class Data:
    def __init__(self):
        self.user_events = {}
        self.repo_events = {}
        self.user_repo_events = {}

    @staticmethod
    def parse_events(filename: str, user_events, repo_events, user_repo_events):
        """
        从单个json文件中逐行抽取所需信息元组(event, user, repo)，并写入字典
        """
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                res = pattern.search(line)
                if res is None or res[1] not in EVENTS:
                    continue

                event, user, repo = res.groups()
                u_e = user_events.setdefault(user, {})
                r_e = repo_events.setdefault(repo, {})
                ur_e = user_repo_events.setdefault(user, {})
                # 设默认值并记录字典第一层的键给中间变量

                ur_e.setdefault(repo, {})
                u_e[event] = u_e.get(event, 0)+1
                r_e[event] = r_e.get(event, 0)+1
                ur_e[repo][event] = ur_e[repo].get(event, 0)+1
                # 利用中间变量计数

                user_events[user] = u_e
                repo_events[repo] = r_e
                user_repo_events[user] = ur_e
                # 将值重新赋给manager.dict
                # 这都是因为它不支持多层直接修改

    def init(self, dir_path: str):
        manager = Manager()
        u_e, r_e, ur_e = manager.dict(), manager.dict(), manager.dict()
        pool = Pool(processes=cpu_count())

        for cur_dir, sub_dir, filenames in os.walk(dir_path):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            for name in filenames:
                pool.apply_async(self.parse_events, args=(f'{cur_dir}/{name}', u_e, r_e, ur_e))
        pool.close()
        pool.join()

        with open('0.pkl', 'wb') as f:
            pickle.dump(dict(u_e), f)
        with open('1.pkl', 'wb') as f:
            pickle.dump(dict(r_e), f)
        with open('2.pkl', 'wb') as f:
            pickle.dump(dict(ur_e), f)

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
