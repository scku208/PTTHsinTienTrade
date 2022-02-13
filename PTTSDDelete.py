from PyPtt import PTT
import datetime
import pandas as pd

from collections import OrderedDict as odict

def crawl_handler(post_info):

    if post_info.delete_status != PTT.data_type.post_delete_status.NOT_DELETED:
        if post_info.delete_status == PTT.data_type.post_delete_status.MODERATOR:
            print(f'[板主刪除][{post_info.author}]')
        elif post_info.delete_status == PTT.data_type.post_delete_status.AUTHOR:
            print(f'[作者刪除][{post_info.author}]')
        elif post_info.delete_status == PTT.data_type.post_delete_status.UNKNOWN:
            print(f'[不明刪除]')
        return

    ALL_POSTS[post_info.aid] = post_info
    print(f'[{post_info.aid}][{post_info.title}]')


if __name__ == '__main__':
    #板上自動po文時的上色函式
    def write_line(color_command, line_text):
        return PTT.command.Ctrl_C + PTT.command.Left + f'{color_command}' + PTT.command.Right + f'{line_text}' + PTT.command.Ctrl_C

    ptt_bot = PTT.API()

    # !!REPLACE WITH YOUR PTT ACCOUNT AND PASSWORD!!
    # !!請務必調整為你在PTT上使用的帳戶名稱與密碼!!
    ptt_bot.login('your ptt account', 'your ptt password')


    ALL_POSTS = odict()
    

    #看版名稱
    BOARD_NAME = 'HsinTien'
    #搜尋觀鍵字(後續還會再詳細檢查)
    SEARCH_TYPE = PTT.data_type.post_search_type.KEYWORD
    SEARCH_CONDITION = '交易'
    #搜尋最新的幾篇結果
    POST_COUNT = 100

    #用來檢查是不是星期六發文的，目前沒作用
    LAST_LAST_SATURDAY = datetime.datetime.today() - datetime.timedelta(days=(datetime.datetime.today().isoweekday()+(1+7*1)))
    LAST_LAST_SATURDAY = LAST_LAST_SATURDAY.replace(hour=0, minute=0, second=0, microsecond=0)

    #PyPTT說明文件裡的教學內容，有調整的地方是crawl_board時會將結果存到ALL_POSTS變數中
    newest_index = ptt_bot.get_newest_index(
            PTT.data_type.index_type.BBS,
            BOARD_NAME,
            search_type=SEARCH_TYPE,
            search_condition=SEARCH_CONDITION,
        )

    start_index = newest_index - POST_COUNT + 1

    error_post_list, del_post_list = ptt_bot.crawl_board(
        PTT.data_type.crawl_type.BBS,
        crawl_handler,
        BOARD_NAME,
        # 使用 index 來標示文章範圍
        start_index=start_index,
        end_index=newest_index,
        search_type=SEARCH_TYPE,
        search_condition=SEARCH_CONDITION,
        # 使用 aid 來標示文章範圍
        # Since 0.8.27
        # start_aid=start_aid,
        # end_aid=end_aid,
        # index 與 aid 標示方式擇一即可
        query=True
    )

    #用來儲存檢查後的文章，依檢查結果分類
    PICKED_POSTS = odict()
    WARNING_POSTS = {'query': odict(), 'detail': odict(), 'delete': odict()}
    ERROR_POSTS = {'date': odict(), 'detail': odict()}

    for aid, post in ALL_POSTS.items():
        if not post.title.startswith('[交易] '):
            WARNING_POSTS['query'][aid] = post
            #發文格式不符合 或不是交易文
        else:
            post_detail  = ptt_bot.get_post(
                BOARD_NAME,
                # 使用 aid 來標示文章範圍
                # Since 0.8.27
                post_aid=post.aid,
            )

            if post_detail.delete_status == 1: #already delete
                WARNING_POSTS['delete'][post_detail.aid] = post_detail
            elif post_detail.content == '[]': # parse fault
                ERROR_POSTS['detail'][post_detail.aid] = post_detail
            else:
                #不在星期六發的文章
                if pd.Timestamp(post_detail.date[4:]).isoweekday() != 6:
                    ERROR_POSTS['date'][post_detail.aid] = post_detail
                else:
                    PICKED_POSTS[post_detail.aid] = post_detail


    #存檔
    pd.to_pickle(PICKED_POSTS, 'pp.xz')
    pd.to_pickle(WARNING_POSTS, 'wp.xz')
    pd.to_pickle(ERROR_POSTS, 'ep.xz')


    # print(f'post_date: {post_date}')
    # if post_date.isoweekday() != 6 and not post.title.startswith('R:'): # 星期六
    #     raise ValueError('不在星期六發文')
    # if post_date == LAST_LAST_SATURDAY.replace(hour=0, minute=0, second=0, microsecond=0):
    #     PICKED_POSTS[aid] = post
    # else:
    #     pass


    # content = [f"預計刪除{write_line('1;33', LAST_LAST_SATURDAY.strftime('%Y年%m月%d號'))}的文章如下："]
    # for aid, post in PICKED_POSTS.items():
    #     content.append(write_line('0;33', f'    {post.author.ljust(12, " ")} ') + write_line('0;', f'{post.title}'))
    # content = '\r\n'.join(content)

    # ptt_bot.post(
    #     board='Test',
    #     title='PyPtt 程式色碼貼文測試',
    #     content=content,
    #     post_type=0,
    #     sign_file=0)
    
    ptt_bot.logout()

    # if error_post_list:
    #     for aid in error_post_list:
    #         post_info = ptt_bot.get_post(BOARD_NAME, post_aid=aid)

    # if del_post_list:
    #     pass

    # for p in ALL_POSTS:
    #     if 
