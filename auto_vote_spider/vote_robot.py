# -*- coding: utf-8 -*-

# try:
#    from urllib.parse import urlparse  # Python 3
# except ImportError:
#    from urlparse import urlparse  # Python 2
import json
import urllib
import urllib2
import ssl

# 变量
import time
import datetime
import random


config = {
    'userId': '',
    'phone': '***********',  # 手机号码
    'password': '***********',  # 密码
    'accessToken': '',  # 保存登录后服务器返回的 token
    'energy': 40,  # 能量值
    'energyUpdateTime': 0
}

vip_list = [
    {'name': '金马', 'userId': 9909, 'latestArtTime': 0}
    # {'name': '南宫远', 'userId': 2234, 'latestArtTime': 0}
]


def loginViaPassword():
    url = r'https://be02.bihu.com/bihube-pc/api/user/loginViaPassword'
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': r'application/x-www-form-urlencoded;charset=utf-8',
        'Referer': r'https://bihu.com/login',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    data = {
        'phone': config['phone'],
        'password': config['password']
    }
    context = ssl._create_unverified_context()
    data = urllib.urlencode(data).encode('utf-8')
    req = urllib2.Request(url, headers=headers, data=data)
    rsp = urllib2.urlopen(req, context=context).read()
    rsp = rsp.decode('utf-8')
    # data_str = json.loads(rsp)['data']
    print('loginViaPassword, ' + rsp)

    # 判断是否登录成功
    is_succ = parse_loginResult(rsp)
    return is_succ


# {"data":{"accessToken":"0c1bbbbbbbbbbbbbbbb","memberId":"","userId":"2189999"},"res":1,"resMsg":"success"}
def parse_loginResult(body):
    data_str = json.loads(body)
    res = data_str['res']
    is_succ = False
    if res == 1:
        config['userId'] = data_str['data']['userId']
        config['accessToken'] = data_str['data']['accessToken']
        is_succ = True

    print('parse_loginResult, is_succ: ', is_succ)
    # write_infoLog('[登录]--返回：' + body)
    return is_succ


def update_averagy(consume):
    # 能量已满，且没有点赞消耗，则不处理
    if config['energy'] == 100 and consume == 0:
        return
    # 异常的更新，不处理
    if config['energy'] < consume:
        return

    # 每 24 小时满 100 个能量，每秒钟恢复 100/(24*60*60) 点能量，
    # (updateTime - config['energyUpdateTime']) 为上次更新到现在到秒数
    updateTime = time.time()
    newEnergy = (updateTime - config['energyUpdateTime']) * 100 / (24 * 60 * 60)
    print('update_averagy, newEnergy: ' + str(newEnergy))
    config['energy'] = config['energy'] + newEnergy - consume

    # 能量最多达到 100 点
    if config['energy'] > 100:
        config['energy'] = 100

    config['energyUpdateTime'] = updateTime
    print('update_averagy, ' + datetime_str() + '\tenergy left: ' + str(config['energy']))


# 返回是否有点赞能量，能量必须大于10，方能点赞
def has_vote_averagy():
    return config['energy'] >= 10


# 给文章点赞
def upVote(artId):
    url = r'https://be02.bihu.com/bihube-pc/api/content/upVote'
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': r'application/x-www-form-urlencoded;charset=utf-8',
        'Referer': r'https://bihu.com/article' + str(artId),
        'Origin': r'https://bihu.com/',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    data = {
        'userId': config['userId'],
        'accessToken': config['accessToken'],
        'artId': artId
    }

    context = ssl._create_unverified_context()
    data = urllib.urlencode(data).encode('utf-8')
    req = urllib2.Request(url, headers=headers, data=data)
    rsp = urllib2.urlopen(req, context=context).read()
    rsp = rsp.decode('utf-8')
    print('upVote, [vote]-[return]: ' + rsp)

    return rsp


'''
https://be02.bihu.com/bihube-pc/api/content/show/getFollowArtList

{"data":{"artList":{"endRow":20,"firstPage":1,"hasNextPage":true,"hasPreviousPage":false,"isFirstPage":true,"isLastPage":false,"lastPage":8,
"list":[{"cmts":433,"createTime":1523887809000,"del":false,"down":0,"downs":10,"follow":1,"id":223834,"money":5591.96,"rtf":0,"snapcontent":"昨天我发了一条朋友圈说，很多人其实不太了解Everipedia的价值，有些人甚至视而不见，今天就让我来简单给大家分析分析","snapimage":"img/854d43365ce40a8f88f72a6253af8fd2.jpeg","title":"【EOS】你可能低估了 EOS 上的明星空投项目：Everipedia","up":0,"ups":2661,"userIcon":"img/6f1120c73505bdf3a87d399811a3eda5.jpeg","userId":9909,"userName":"金马","valid":0},
{"cmts":349,"createTime":1523844003000,"del":false,"down":0,"downs":9,"follow":1,"id":220791,"money":6485.05,"rtf":0,"snapcontent":"上周（4月9日-4月15日）EOS相关重要消息回顾。--------TeamEOSCannon--------1、4月1","snapimage":"img/ed4cd1424d81599d6ac93962edb25551.jpg","title":"【2018年第15周 EOS信息周报】一周重要信息均在于此 |EOS Cannon|","up":0,"ups":3372,"userIcon":"img/59bfa3ec49a5c107147dbb6038c649fb.png","userId":334485,"userName":"EOSCannon","valid":0}],
"navigatePages":8,"navigatepageNums":[1,2,3,4,5,6,7,8],"nextPage":2,"pageNum":1,"pageSize":20,"pages":12,"prePage":0,"size":20,"startRow":1,"total":236},"type":"art"},"res":1,"resMsg":"success"}
'''
def VoteFollowArtList(body):
    data_str = json.loads(body)
    res = data_str['res']

    vote_count = 0
    vote_suc = False
    log_content_format = u'[%s]--【%s】的最新文章已有【%d】赞，文章收益【¥%.2f】，文章标题【%s】'
    if res == 1 and data_str['data']['artList']['size'] > 0:
        for item in data_str['data']['artList']['list']:
            log_content = log_content_format % (datetime_str(), item['userName'], item['ups'], item['money'], item['title'])
            print('VoteFollowArtList, ' + log_content)

            # 看是否是已关注的大V的文章
            '''
            is_vip_art = False
            for vipItem in vip_list:
                if (item['userId'] == vipItem['userId']):
                    is_vip_art = True
                    break

            if (is_vip_art):
                if item['up'] == 0 and item['ups'] < 300:
                    # print(item)
                    vote_data = upVote(item['id'])  # 执行点赞
                    res_vote = vote_data['res']
                    if res_vote == 1:
                        # 点赞成功，减掉10个能量值
                        update_averagy(10)
                        print('VoteFollowArtList, :) vote success，energy -10')
                        vote_suc = True
                        vote_count = vote_count + 1
            '''

    print('VoteFollowArtList, vote total success count: ', vote_count)

    # 如果res为1，说明结果正常
    return (res == 1), vote_suc


def getFollowArtList():
    url = r'https://be02.bihu.com/bihube-pc/api/content/show/getFollowArtList'
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': r'application/x-www-form-urlencoded;charset=utf-8',
        'Referer': r'https://bihu.com/?category=follow',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    data = {
        'userId': config['userId'],
        'accessToken': config['accessToken']
    }

    context = ssl._create_unverified_context()
    data = urllib.urlencode(data).encode('utf-8')
    req = urllib2.Request(url, headers=headers, data=data)
    rsp = urllib2.urlopen(req, context=context).read()
    rsp = rsp.decode('utf-8')

    print('getFollowArtList, ' + rsp)
    return rsp


def datetime_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 主逻辑
def Run():
    print('============================== Run ==============================')
    succ = loginViaPassword()
    if not succ:
        print('Run, login fail')
        return

    print('Run, login success and vote for big V below: ')
    print(vip_list)
    while succ:
        # 更新当前能量值
        update_averagy(0)
        # 如果有能量，再去刷新、点赞
        if has_vote_averagy():
            body = getFollowArtList()
            list_succ, vote_succ = VoteFollowArtList(body)
            if not list_succ:
                succ = False
                print('Run, get follow art list fail and exit')
                break
            elif vote_succ:
                print('Run, :) Congratulations vote success')
                # random.randint(0, 9)
                # time.sleep(5)

        else:
            print('Run, energy not enough and try later')
            time.sleep(10)  # 如果没有能量，十秒钟之后再循环判断

        succ = False

config['energyUpdateTime'] = time.time()
Run()
