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
import asyncio
import aiofiles

# todo 尝试aiofiles
# todo 使用多进程配合协程

EVENTS = ("PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent", )
pattern = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?repo.*?"name":"(\S+?)"')


class Data:
    def __init__(self):
        self.user_events = {}
        self.repo_events = {}
        self.user_repo_events = {}

    async def __count_events(self, filename: str):
        """
        从单个json文件中逐行抽取所需信息元组(event, user, repo)，并写入字典
        """
        # with open(filename, 'r', encoding='utf-8') as f:
        async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
            async for line in f:
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

    async def __read_files(self, path, filenames):
        await asyncio.gather(
            *(self.__count_events(f'{path}/{f}') for f in filenames)
        )

    def init(self, dir_path: str):
        for cur_dir, sub_dir, filenames in os.walk(dir_path):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            asyncio.run(self.__read_files(cur_dir, filenames))
            # for name in filenames:
            #     self.__count_events(f'{cur_dir}/{name}')

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
