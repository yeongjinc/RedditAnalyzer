import praw
import json
import threading
import time
import os

CRAWLING_PERIOD_SEC = 3600
CLIENT_SECRET = 'client.secret'

SUBREDDIT_LIST = ['news', 'uncensorednews', 'worldnews', 'Upliftingnews',
                    'truenews', 'fakenews', 'politicalnews']
POSTS_FILE = 'posts.txt'
COMMENTS_FILE = 'comments.txt'

INF_TIME = 3600*24*30 # a month

def getReddit(c_id, c_secret, u_agent):
    reddit = praw.Reddit(client_id=c_id, client_secret=c_secret, user_agent=u_agent);
    return reddit;

def serialize(subs_list):
    return json.dumps(subs_list, indent=2)

def crawler(reddit, start_date, end_date):
    subs_list = []
    comments_list = []
    for subreddit_name in SUBREDDIT_LIST:
        subreddit = reddit.subreddit(subreddit_name)
        # test with 1478592000, 1478678400
        subs = subreddit.submissions(start_date, end_date)
        for sub in subs:
            raw_sub_dic = vars(sub) # including inner classes like 'Comment'
            sub_dic = {k:v for k, v in raw_sub_dic.items()
                        if not k.startswith('_')
                        and k != 'subreddit'}
            sub_dic['author'] = sub_dic['author'].name
            subs_list.append(sub_dic)

            sub.comments.replace_more(limit=0)
            for comment in sub.comments.list():
                raw_comment_dic = vars(comment)
                comment_dic = {k:v for k, v in raw_comment_dic.items()
                                if not k.startswith('_')
                                and k != 'subreddit'}
                #if comment_dic['body'] == '[removed]':
                #    continue
                if comment_dic['author'] is not None:
                    comment_dic['author'] = comment_dic['author'].name
                comments_list.append(comment_dic)
    return (serialize(subs_list), serialize(comments_list))

def append_to_json(json_file, data):
    s = str(data)
    json_file.seek(0, os.SEEK_END)
    pos = json_file.tell() - 2
    if pos > 0:
        json_file.seek(pos, os.SEEK_SET)
        json_file.truncate()
        s = ',' + s[1:]
    json_file.write(s)

def timer(reddit, posts_file, comments_file):
    while True:
        end_date = int(time.time())
        start_date = end_date - CRAWLING_PERIOD_SEC
        res = crawler(reddit, start_date, end_date)
        append_to_json(posts_file, res[0])
        append_to_json(comments_file, res[1])
        time.sleep(CRAWLING_PERIOD_SEC)
        # time.sleep(10) #test


if __name__ == "__main__":
    cs_file = open(CLIENT_SECRET, 'r')
    lines = cs_file.read().splitlines()
    cs_file.close()

    reddit = getReddit(lines[2], lines[3], lines[4])

    p_f = open(POSTS_FILE, 'a+')
    c_f = open(COMMENTS_FILE, 'a+')

    cthread = threading.Thread(target=timer,args=[reddit, p_f, c_f])
    cthread.daemon = True
    cthread.start()

    try:
        time.sleep(INF_TIME)
    except KeyboardInterrupt:
        print 'over'
    p_f.close()
    c_f.close()



