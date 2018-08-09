import requests
import time
from bs4 import BeautifulSoup
import shutil
import tempfile
import urllib.request, urllib.error
import transliterate
from datetime import datetime
import re
import fileinput
sleep_time = 3

def main():

    def copyrights():
        copyrights = '<p align="center"><b>Скомпилировано из материалов форума http://selfrealization.info</b></p><br/><br/>'
        current_date = '<p>ver.:' + str(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")) + '</p><br/><br/>'
        link = '<p>Постоянная ссылка на скачивание: <i>https://goo.gl/9BTa3P </i></p><br/>'
        all = copyrights + current_date + link
        return all

    # add tags in html document
    def add_html_tages(title, parameter):
        html_open = '<html>'
        html_close = '</html>'
        body_open = '<body>'
        body_close = '</body>'
        html_head_open = '<head> <meta charset="utf-8">'
        html_head_close = '</head>'
        html_title_open = '<title>'
        html_title_close = '</title>'
        if parameter == 'htmlopen':
            document = html_open +\
                   html_head_open +\
                   html_title_open +\
                   title +\
                   html_title_close +\
                   html_head_close +\
                   body_open
            return document
        if parameter == 'htmlclose':
            document = body_close + html_close
            return document



    # get data from url
    def request_data_from_url(url):
        time.sleep(sleep_time)
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                return soup
        except urllib.error.HTTPError as e:
            print('HTTPError code: ', e.code)

    # get number of page for each topics
    def get_number_of_page_topics(url):
        page = request_data_from_url(url)
        body = page.body
        pageNavHeader = page.find('span', class_='pageNavHeader')
        if pageNavHeader == None:
            number_of_pages = 1
            return number_of_pages
        else:
            number_of_pages_string = pageNavHeader.text.strip()
            number_of_pages_tuple = tuple(item for item in number_of_pages_string.split(' '))
            number_of_pages = int(number_of_pages_tuple[3])
            print(number_of_pages, ' pages in topic')
            return number_of_pages

    def get_title(url, type):
        page = request_data_from_url(url)
        head = page.head
        pageNavHeader = head.find('title').text.strip()
        title_list = pageNavHeader.split(' ')
        title_cyr = title_list[0] + '_' + title_list[1]
        title_h1 = title_list[0] + ' ' + title_list[1]
        if type == 'cyr':
            return title_cyr
        if type == 'h1':
            print('procesing page have a title: ', title_h1)
            return title_h1
        else:
            title = transliterate.translit(title_cyr, reversed=True)
            return title

    # write to file
    def write_to_file(filename, message):
        print('writing data to file: ', filename)
        try:
            file = open(filename, "a", encoding='utf-8')
            file.write(message)
            file.close()
        except IOError:
            print("An IOError has occurred!")

    # read handling urls from file
    def read_urls(filename):
        print('read urls from file: ', filename)
        try:
            with open(filename, encoding='utf-8') as file:
                print('open file: ', filename)
                url_list = [row.strip() for row in file]
                return url_list
        except IOError:
            print("An IOError has occurred!")

    # read file with start urls
    list = read_urls('urls')

    # handling each url
    for source_url in list:
        title = get_title(source_url, 'lat')
        title_cyr = get_title(source_url, 'cyr')
        title_h1 = get_title(source_url, 'h1')
        filename = title + '.html'
        print('handling url: ', source_url)
        open_tags = add_html_tages(title_h1, parameter='htmlopen')
        write_to_file(filename, open_tags)
        write_to_file(filename, copyrights())
        h_1 = '<br/><br/><h1 align="center">' + title_h1 + '</h1><br/>'
        write_to_file(filename, h_1)
        # get theme number of pages
        number_of_pages = get_number_of_page_topics(source_url)
        current_page = 0
        # collecting topics pages in one file
        while current_page < number_of_pages:
            if current_page == 0:
                page = request_data_from_url(source_url)
                print('downloding page #', current_page, 'from: ', source_url)
            else:
                url = source_url + 'page-' + str(current_page + 1)
                page = request_data_from_url(url)
                print('downloding page #', current_page, 'from: ', url)
            body = page.body
            # raw_messages = body.findAll('div', class_='messageContent') article
            messages = str(body.findAll('article'))
            write_to_file(filename, messages)
            current_page = current_page + 1

        close_tages = add_html_tages(title, parameter='htmlclose')
        write_to_file(filename, close_tages)
        print('downloaded all data')
        print('clearing file...')
        newfilename = 'book.' + filename
        source_file = open(filename, "r", encoding='utf-8')
        output_file = open(newfilename, "a", encoding='utf-8')
        for line in source_file:
            clear_messages_1 = line.replace('][', '')
            clear_messages_2 = clear_messages_1.replace('>[<', '><')
            clear_messages_3 = clear_messages_2.replace('>]<', '><')
            output_file.write(clear_messages_3)

        source_file.close()
        output_file.close()


if __name__ == '__main__':
    main()

