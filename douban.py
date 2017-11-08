import requests
from bs4 import BeautifulSoup
import random
import string
from time import sleep

NEW_USER_THRESHOLD = 5
MOVIE = 'https://movie.douban.com/subject/3868141/'

def get_content(url):
    web_data = requests.get(url,
                            headers={"User-Agent": 'Mozilla/5.0 ' + str(random.randint(0,10000))},
                            cookies={"Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))})
    web_data.encoding = 'utf-8'
    return web_data.text


def num_watched(url):
    soup = BeautifulSoup(get_content(url), 'lxml')
    line = str(soup.select('div.info h1')[0])
    left_parenthesis, right_parenthesis = line.rfind('电影(')+3, line.rfind(')')
    return int(line[left_parenthesis:right_parenthesis])


def movie_analyze(url):
    mark = 0
    user_header_list = []
    file = open("movie_analysis.txt","wb")
    user_count = 0
    new_user = 0
    stars_old = 0
    stars_new = 0
    while len(user_header_list) > 0 or mark == 0:
        print('currently working on mark '+ str(mark))
        review_url = url + 'reviews?start=' + str(mark)
        mark += 20
        soup = BeautifulSoup(get_content(review_url), 'lxml')
        user_header_list = soup.select('div.header-more')
        for header in user_header_list:
            user_count += 1
            author = header.select_one('a.author')
            people_url = author['href']
            people_id = people_url[people_url[:-1].rfind('/') + 1:people_url.rfind('/')]
            user_movie_collect = 'https://movie.douban.com/people/' + people_id + '/collect'

            user = author.text.replace('\n', '')
            num_movie_watched = num_watched(user_movie_collect)
            stars = int(header.find('span', {'property': 'v:rating'})['class'][0][-2])
            res = str(stars) + ' stars, watched ' + str(num_movie_watched) + ' movies, user: ' + user + ' ' + people_url + '\n'

            file.write(res.encode('utf-8'))
            file.flush()
            new_or_not = num_movie_watched < NEW_USER_THRESHOLD
            new_user += 1 if new_or_not else 0
            if new_or_not:
                stars_new += stars
            else:
                stars_old += stars

    file.write('\n\n'.encode('utf-8'))
    file.write(('Number of reviewers: ' + str(user_count)+'\n').encode('utf-8'))
    file.write(('Number of potentially new users: '+str(new_user)+'\n').encode('utf-8'))
    if new_user != 0:
        file.write(('Percentage of new users / all users : ' + "{:.1%}\n".format(new_user/float(user_count))).encode('utf-8'))
        file.write(('Average rating among old users: ' + "{0:.1f}\n".format(stars_old/float(user_count-new_user))).encode('utf-8'))
        file.write(('Average rating among new users: ' + "{0:.1f}\n".format(stars_new/float(new_user))).encode('utf-8'))
    file.close()


def main():
    movie_analyze(MOVIE)


if __name__ == '__main__':
    MOVIE = input('Enter URL of the movie page: ').strip()
    main()
