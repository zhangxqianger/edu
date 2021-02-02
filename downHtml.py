from requests import request, cookies as c, get, post
import time
from bs4 import BeautifulSoup
import json
from urllib import parse
import tkinter as tk
import re
import os

host = 'https://hbt.gpa.enetedu.com'

cookies = c.RequestsCookieJar()
eneteducookies = c.RequestsCookieJar()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:83.0) Gecko/20100101 Firefox/83.0'
}


def downImg():
    page = get("https://mingshi8.hbte.com.cn/index.php/home/login/login.html", headers=headers)
    cookies.update(page.cookies)
    response = request("GET", "https://mingshi8.hbte.com.cn/index.php/Home/Login/Verify", headers=headers,
                       cookies=page.cookies, allow_redirects=False)
    cookies.update(response.cookies)
    name = "../img/" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ".jpg"
    file = open(file=name, mode='wb+')
    file.write(response.content)
    file.close()
    return name


def login(user, password, valid):
    form = {
        'id_number': user,
        'pwd': password,
        'code': valid,
        'idd': ''
    }
    print("cookies: ", cookies)
    response = post("https://mingshi8.hbte.com.cn/index.php/home/login/dologin.html", data=form,
                    headers=headers,
                    cookies=cookies, allow_redirects=False)
    cookies.update(response.cookies)
    project = get('https://mingshi8.hbte.com.cn/index.php/home/project/jxz_xq/id/287/uid/708283.html', headers=headers,
                  cookies=cookies)
    jumpUrl = re.match(r'.*(https://peixun.*html)', project.text, re.M | re.S).group(1)
    jump = get(jumpUrl[0:jumpUrl.find('"')], cookies=cookies, headers=headers)
    eneteducookies.update(jump.cookies)
    return jump


def study(resp, text):
    response = post("https://hbt.gpa.enetedu.com/UserCenter/GetPersonCenterList", data={'type': 4}, headers=headers,
                    cookies=eneteducookies)
    list = json.loads(response.text)
    data = list['data']
    for d in data:
        if d['choose']:
            text.insert(tk.END, d['name'] + "---" + str(d['id']) + '\n')
            text.see(tk.END)
            intPageNo = '1'
            iframe = get(
                "https://hbt.gpa.enetedu.com/ChooseCourseCenter/CourseInterface?newSearchFlag=true&themeID={}&intPageNo={}".format(
                    str(d['id']), intPageNo),
                cookies=eneteducookies, headers=headers)

            table = BeautifulSoup(iframe.text, features='html.parser').find(id='courseList')
            trs = table.findAll("tr")
            page = trs[-1]
            options = page.find('select').findAll('option')
            for option in options:
                intPageNo = option['value']
                url = "https://hbt.gpa.enetedu.com/ChooseCourseCenter/CourseInterface?themeID={}&intPageNo={}".format(
                    str(d['id']), intPageNo)
                iframe = get(
                    url,
                    cookies=eneteducookies, headers=headers)
                table = BeautifulSoup(iframe.text, features='html.parser').find('tbody', id='courseList')
                trs = table.findAll("tr")
                doParse(trs, text)

    text.insert(tk.END, '-------------学习完成-------------\n')
    text.see(tk.END)
    # 清空资源
    clear()



def doParse(trs, text):
    for i in range(len(trs) - 1):
        tds = trs[i].findAll("td")
        if tds[2].string.strip() == '视频课程':
            text.insert(tk.END, '\t' + tds[1]['title'] + '\n')
            text.see(tk.END)
            onclick = tds[1].find("a")['onclick']
            url = onclick[onclick.find('(') + 2: onclick.find(')') - 1]
            coursePage = get(host + url, headers=headers, cookies=eneteducookies)
            eneteducookies.update(coursePage.cookies)
            user = eneteducookies.get("EDUCATION_USER_INFO_SESSION_FRONT")
            id = parse.parse_qs(user)['id'][0]

            page = BeautifulSoup(coursePage.text, features='html.parser')
            courseID = page.find(id='courseID')['value']
            project_id = page.find(id='project_id')['value']
            classtopic_id = page.find(id='classtopic_id')['value']

            lis = page.find('ul', class_='courseName').findAll("li")
            for li in lis:
                a = li.find("a")
                text.insert(tk.END, '\t\t' + a.string.strip() + '\n')
                text.see(tk.END)
                onclick = a['onclick']
                coursewareid = onclick[onclick.find('(') + 1: onclick.find(')')]
                touch = 'https://hbt.gpa.enetedu.com/Common/RecordPlayBack?course_id={}&courseware_id={}&classtopic_id={}'.format(
                    courseID, coursewareid, classtopic_id)
                touchPage = get(touch, headers=headers, cookies=eneteducookies)
                cook = parse.parse_qs(touchPage.cookies.get("enet_studentCourseWareLearn" + coursewareid + '1'))
                if cook is None or len(cook) == 0:
                    continue
                key = cook['key']
                # eneteducookies.update(touchPage.cookies)
                survey = post('https://hbt.gpa.enetedu.com/VideoPlay/StudySurvey', data={
                    'course_id': courseID,
                    'courseware_id': coursewareid,
                    'start': '1000000',
                    'end': '9999999',
                    'student_id': id,
                    'course_type': '1'
                }, headers=headers, cookies=eneteducookies)
                eneteducookies.update(survey.cookies)
                status = post('https://hbt.gpa.enetedu.com/VideoPlay/updateStudyStatue2', data={
                    'subject_id': '0',
                    'course_id': courseID,
                    'courseware_id': coursewareid,
                    'course_type': '1',
                    'wordkey': key,
                    'iPlaySec': '9999',
                    'playSec': '0',
                    'classtopic_id': classtopic_id,
                    'student_id': id
                }, headers=headers, cookies=eneteducookies)

                post('https://hbt.gpa.enetedu.com//MyCourse/videocreditcomputing', data={
                    'classtopic_id': classtopic_id,
                    'courseid': courseID
                }, headers=headers, cookies=eneteducookies)


def clear():
    cookies.clear()
    eneteducookies.clear()
    path = '../img'
    imgs = os.listdir(path)
    for img in imgs:
        os.remove(path + '/' + img)
