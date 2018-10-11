import datetime
import random
import time
from random import randint, shuffle

import requests
import requests_html

QUESTION_ID = 28595636
URL = 'https://www.wjx.cn/m/28595636.aspx'


def bulid_post_head(sess):
    resp = sess.get(URL)
    iter = int(resp.text.find('rndnum'))
    start_i = iter
    while True:
        if resp.text[iter] == ';':
            break
        iter += 1
    print(resp.text[start_i:iter])
    rndnum = resp.text[start_i:iter].split('=')[1].strip('\"').split('.')[0]
    raw_t = round(time.time(), 3)
    t = int(str(raw_t).replace('.', ''))
    starttime = datetime.datetime.fromtimestamp(int(raw_t) - randint(1, 60 * 3)).strftime("%Y/%m/%d %H:%M:%S")
    data = {
        'curid': 28595636,
        'starttime': starttime,
        'source': 'directphone',
        'submittype': 1,
        'hlv': 1,
        'rn': int(rndnum),
        't': t,
    }
    return data


PERSON_CNT = 1091
VAILD_CNT = 683


def generate_chooses():
    booking = read_form()
    person_chooces = []
    ans_total = []
    choos_cnt = []
    
    for qes in booking.keys():
        all_cnt = sum(list(booking[qes].values()))
        ans_total.append(all_cnt)
        choose_cnt_person = []
        if qes == 1 or qes == 2:
            person_cnt = PERSON_CNT
        else:
            person_cnt = VAILD_CNT
        
        base_cnt = int(all_cnt / person_cnt)
        for each in range(person_cnt):
            choose_cnt_person.append(base_cnt)
        if all_cnt % person_cnt != 0:
            for each in range(all_cnt % person_cnt):
                choose_cnt_person[each] += 1
        choos_cnt.append(choose_cnt_person)
    
    steper_cnt = 0
    for person in range(PERSON_CNT):
        chooces = []
        invaild_flag = False
        for qes in booking.keys():
            qes_chos = []
            for each in range(choos_cnt[qes - 1][person]):
                while ans_total[qes - 1] != 0:
                    curr_chos_iter = (steper_cnt % len(booking[qes].keys())) + 1
                    if booking[qes][curr_chos_iter] != 0:
                        booking[qes][curr_chos_iter] -= 1
                        if qes == 2:
                            if person >= VAILD_CNT:
                                qes_chos.append(2)
                                invaild_flag = True
                                break
                            else:
                                qes_chos.append(1)
                                break
                        
                        qes_chos.append(curr_chos_iter)
                        ans_total[qes - 1] -= 1
                        steper_cnt += 1
                        break
                    else:
                        steper_cnt += 1
            chooces.append(qes_chos)
            if invaild_flag:
                break
        
        person_chooces.append(chooces)
    # for each in person_chooces:
    #     print(each)
    print(person_chooces)
    return person_chooces


def read_form():
    with open('forms', 'r') as f:
        lines = f.readlines()
    booking = {}
    each_line = iter(lines)
    line = next(each_line)
    while True:
        try:
            line = line.strip('\n')
            ques_num = int(line)
            booking[ques_num] = {}
            while True:
                line = next(each_line)
                if line != '\n':
                    items = line.split(' ')
                    booking[ques_num][int(items[0])] = int(items[1].strip('\n'))
                else:
                    line = next(each_line)
                    break
        except StopIteration:
            break
    return booking


def trans_choose_to_str(chos: list):
    res = ''
    for ques_num in range(18):
        try:
            new_cho = [str(i) for i in chos[ques_num]]
            new_cho = '|'.join(new_cho)
            res += '%d$%s}' % (ques_num + 1, new_cho)
        except IndexError:
            res += '%d$-3}' % (ques_num + 1)
    res = res[:-1]
    print(res)
    return res


def execute_fill():
    chooses = generate_chooses()
    shuffle(chooses)
    chooses = iter(chooses)
    each = next(chooses)
    cnt = 1
    while True:
        try:
            print('post person %d' % cnt)
            session = requests_html.HTMLSession()
            data = bulid_post_head(session)
            # data = {}
            data['submitdata'] = trans_choose_to_str(each)
            host = {
                'Host': 'www.wjx.cn',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
                "Cookie": "",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Forwarded-For": "%s.%s.%s.%s" % (
                    random.randint(0, 254), random.randint(0, 254), random.randint(0, 254), random.randint(0, 254))
            }
            rep = requests.post(url=URL, data=data)
            # print(rep.text)
            if rep.status_code == 200:
                print('success')
                each = next(chooses)
                cnt += 1
                time.sleep(5)
        except StopIteration:
            break


if __name__ == '__main__':
    # generate_chooses()
    execute_fill()
