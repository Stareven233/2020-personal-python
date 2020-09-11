# -*- coding: utf-8 -*-
"""
初始化：
    input: python3 GHAnalysis.py -i data
    output: 0
测试：
    input: python3 GHAnalysis.py -e PushEvent -u greatfire
    output: 24

EventName
    PushEvent
    IssueCommentEvent
    IssuesEvent
    PullRequestEvent
"""

import json
import os
import argparse
import pickle

# todo 使用pandas读取json
#      优化__reduce_one
#      正则表达式逐行提取所需信息


class Data:
    def __init__(self):
        self.__user_events = {}
        self.__repo_events = {}
        self.__user_repo_events = {}

    @staticmethod
    def __read(file_path: str):
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                records.append(json.loads(line))
        return records

    def init(self, dir_path: str):
        records = []
        for cur_dir, sub_dir, filenames in os.walk(dir_path):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            for name in filenames:
                records.extend(self.__read(f'{cur_dir}/{name}'))

        records = self.__reduce_dicts(records)

        for i in records:
            user = i['actor__login']
            repo = i['repo__name']
            event = i['type']

            self.__user_events.setdefault(user, {})
            self.__user_repo_events.setdefault(user, {})
            self.__repo_events.setdefault(repo, {})
            self.__user_repo_events[user].setdefault(repo, {})

            self.__user_events[user][event] = self.__user_events[user].get(event, 0)+1
            self.__repo_events[repo][event] = self.__repo_events[repo].get(event, 0)+1
            self.__user_repo_events[user][repo][event] = self.__user_repo_events[user][repo].get(event, 0)+1

        # with open('0.json', 'wb', encoding='utf-8') as f:
            # json.dump(self.__user_events, f)
        with open('0.json', 'wb') as f:
            pickle.dump(self.__user_events, f)
        with open('1.json', 'wb') as f:
            pickle.dump(self.__repo_events, f)
        with open('2.json', 'wb') as f:
            pickle.dump(self.__user_repo_events, f)

    def load(self):
        if not any((os.path.exists(f'{i}.json') for i in range(3))):
            raise RuntimeError('error: data file not found')

        with open('0.json', 'rb') as f:
            self.__user_events = pickle.load(f)
        with open('1.json', 'rb') as f:
            self.__repo_events = pickle.load(f)
        with open('2.json', 'rb') as f:
            self.__user_repo_events = pickle.load(f)

    def __reduce_one(self, d: dict, prefix: str):
        """
        将字典递归降维，prefix只由当前及上层的key构成
        {'a': {'b': {'c': {'d': 'e'}}, 'bb': 'bb'}, 'aa': {'aa': 2}} -> {'c__d': 'e', 'a__bb': 'bb', 'aa__aa': 2}
        """

        # todo 或许可直接d[actor][login]取出想要的三个返回
        dd = {}
        for k, v in d.items():
            if isinstance(v, dict):
                dd.update(self.__reduce_one(v, k))
            else:
                dd[f'{prefix}__{k}' if prefix != '' else k] = v
        return dd

    def __reduce_dicts(self, records_list: list):
        return [self.__reduce_one(d, '') for d in records_list]

    def get_user_event(self, user: str, event: str) -> int:
        return self.__user_events.get(user, {}).get(event, 0)

    def get_repo_event(self, repo: str, event: str) -> int:
        return self.__repo_events.get(repo, {}).get(event, 0)

    def get_user_repo_event(self, user: str, repo: str, event: str) -> int:
        return self.__user_repo_events.get(user, {}).get(repo, {}).get(event, 0)


class Run:
    def __init__(self):
        self.basedir = os.path.dirname(os.path.abspath(__file__))
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.arg_init()

    def arg_init(self):
        self.parser.add_argument('-i', '--init', type=str)
        self.parser.add_argument('-u', '--user', type=str)
        self.parser.add_argument('-r', '--repo', type=str)
        self.parser.add_argument('-e', '--event', type=str)

    def analyse(self):
        args = self.parser.parse_args()

        self.data = Data()
        if args.init:
            self.data.init(args.init)
            return 0
        self.data.load()

        if not args.event:
            raise RuntimeError('error: the following arguments are required: -e/--event')
        if not args.user and not args.repo:
            raise RuntimeError('error: the following arguments are required: -u/--user or -r/--repo')

        if args.user and args.repo:
            res = self.data.get_user_repo_event(args.user, args.repo, args.event)
        elif args.user:
            res = self.data.get_user_event(args.user, args.event)
        else:
            res = self.data.get_repo_event(args.repo, args.event)
        return res


if __name__ == '__main__':
    a = Run()
    print(a.analyse())
