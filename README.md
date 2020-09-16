# 2020-personal-python

### 简介
[fzu软工实践个人编程作业1](https://edu.cnblogs.com/campus/fzu/SE2020/homework/11167)

### 目的
统计GitHub 归档数据中个人/仓库的4种事件(PushEvent, IssueCommentEvent, IssuesEvent, PullRequestEvent)的数量

### 使用示例
- 初始化：  
    input: python3 GHAnalysis.py -i data  
    output: init done  
- 测试：  
    input: python3 GHAnalysis.py -e PushEvent -u waleko  
    output: 2  
    input: python3 GHAnalysis.py -r katzer/cordova-plugin-background-mode -e PushEvent  
    output: 6  
    input: python3 GHAnalysis.py -u cdupuis -r atomist/automation-client -e PushEvent  
    output: 2  

