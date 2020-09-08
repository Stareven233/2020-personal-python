import json
import os
import argparse


class Data:
    def __init__(self, dict_address: str = None, reload: int = 0):
        if reload == 1:
            self.__init(dict_address)
        if dict_address is None and not os.path.exists('1.json') and not os.path.exists('2.json') and not os.path.exists('3.json'):
            # todo any()
            raise RuntimeError('error: init failed')
        x = open('1.json', 'r', encoding='utf-8').read()
        self.__4Events4PerP = json.loads(x)
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)

    def __init(self, dict_address: str):
        json_list = []
        for root, dic, files in os.walk(dict_address):
            for f in files:
                if f[-5:] == '.json':
                    json_path = f
                    x = open(dict_address+'\\'+json_path,
                             'r', encoding='utf-8').read()
                    str_list = [_x for _x in x.split('\n') if len(_x) > 0]
                    for i, _str in enumerate(str_list):
                        try:
                            json_list.append(json.loads(_str))
                        except:
                            pass
        records = self.__listOfNestedDict2ListOfDict(json_list)
        self.__4Events4PerP = {}
        self.__4Events4PerR = {}
        self.__4Events4PerPPerR = {}
        for i in records:
            if not self.__4Events4PerP.get(i['actor__login'], 0):
                self.__4Events4PerP.update({i['actor__login']: {}})
                self.__4Events4PerPPerR.update({i['actor__login']: {}})
            self.__4Events4PerP[i['actor__login']][i['type']
                                         ] = self.__4Events4PerP[i['actor__login']].get(i['type'], 0)+1
            if not self.__4Events4PerR.get(i['repo__name'], 0):
                self.__4Events4PerR.update({i['repo__name']: {}})
            # todo setdefault
            self.__4Events4PerR[i['repo__name']][i['type']
                                       ] = self.__4Events4PerR[i['repo__name']].get(i['type'], 0)+1
            if not self.__4Events4PerPPerR[i['actor__login']].get(i['repo__name'], 0):
                self.__4Events4PerPPerR[i['actor__login']].update({i['repo__name']: {}})
            self.__4Events4PerPPerR[i['actor__login']][i['repo__name']][i['type']
                                                          ] = self.__4Events4PerPPerR[i['actor__login']][i['repo__name']].get(i['type'], 0)+1
        with open('1.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerP,f)
        with open('2.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerR,f)
        with open('3.json', 'w', encoding='utf-8') as f:
            json.dump(self.__4Events4PerPPerR,f)

    def __parseDict(self, d: dict, prefix: str):
        # 将字典递归降维，prefix只由当前及上层的key构成
        # {'a': {'b': {'c': {'d': 'e'}}, 'bb': 'bb'}, 'aa': {'aa': 2}} -> {'c__d': 'e', 'a__bb': 'bb', 'aa__aa': 2}
        _d = {}
        for k in d.keys():
            if str(type(d[k]))[-6:-2] == 'dict':
                # type(d[k]) == dict
                _d.update(self.__parseDict(d[k], k))
            else:
                _k = f'{prefix}__{k}' if prefix != '' else k
                _d[_k] = d[k]
        return _d

    def __listOfNestedDict2ListOfDict(self, a: list):
        records = []
        for d in a:
            _d = self.__parseDict(d, '')
            records.append(_d)
        return records

    def getEventsUsers(self, username: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        else:
            return self.__4Events4PerP[username].get(event,0)

    def getEventsRepos(self, reponame: str, event: str) -> int:
        if not self.__4Events4PerR.get(reponame,0):
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event,0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__4Events4PerP.get(username,0):
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame,0):
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def analyse(self):
        if self.parser.parse_args().init:
            self.data = Data(self.parser.parse_args().init, 1)
            return 0
        else:
            if self.data is None:
                self.data = Data()
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        # 查询某个用户在某个项目中某个事件的数量
                        res = self.data.getEventsUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo, self.parser.parse_args().event)
                    else:
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().reop, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -l or -c are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
    a = Run()
