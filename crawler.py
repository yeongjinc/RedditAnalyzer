import praw
import json

CRAWLING_PERIOD_SEC = 10
CLIENT_SECRET = 'client.secret'

SUBREDDIT_LIST = ['news']
POSTS_FILE = 'posts.txt'
COMMENTS_FILE = 'comments.txt'

def getReddit(c_id, c_secret, u_agent):
    reddit = praw.Reddit(client_id=c_id, client_secret=c_secret, user_agent=u_agent);
    return reddit;

def serialize(subs_list):
    return json.dumps(subs_list)

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

#def timer(reddit, period):


if __name__ == "__main__":
    cs_file = open(CLIENT_SECRET, 'r')
    lines = cs_file.read().splitlines()
    reddit = getReddit(lines[2], lines[3], lines[4])




