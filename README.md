# Improve How Students Search for Courses

## I - Project Intention
This project is originally a course project from UMSI 650 - Information Retrieval. Based on our own experience as students, we know that students are struggling with choosing the right courses for themselves, especially when they are still unsure about their future career path and want to try anything they're interested in.

For students from the University of Michigan, they are able to use [Atlas](https://atlas.ai.umich.edu/) to look up a specific course and the course evaluation. Although the returned results also show what other courses that peers were taking in the same semester or previsous semesters, students, still, need to know the course names first, which sometimes is a bumper for students really want to do their search.

Therefore, we want to use the knowledge learned from the course to build a course search enginee by ourselves. 🤓

## II - Data
### Data Recourse
The data we used for this project is from [UMSI course website](https://www.si.umich.edu/programs/courses). We collected all courses it has, including course number, course name, and course description. 

Here are some codes that you can use.
```
from bs4 import BeautifulSoup
import requests


def get_all_courses(myurl, mylist=[], course_source='umsi'):

    if course_source == 'umsi':
        response = requests.get(myurl)
        txt = response.text
        soup = BeautifulSoup(txt, 'html.parser')
        next_page = soup.find('li', class_='pager__item pager__item--next')

    if next_page:
        items = soup.find_all("div", class_="item-teaser-group")
        courses_item = [item['href'].split('/')[3] for item in items[0].find_all('a', href=True) if item['href'].split('/')[3]]
        mylist.extend(courses_item)
        next_page_url = myurl + next_page.find('a')['href']
        # print(mylist)
        # print(next_page_url)
        courses = get_all_courses(next_page_url)


    elif course_source == 'ross':
        response = requests.get(myurl)
        txt = response.text
        soup = BeautifulSoup(txt, 'html.parser')
        next_page = soup.find('li', class_='pager-next')
        # print(next_page)

    if next_page:
        items = soup.find_all('tr', class_='extra')
        course_urls = [item.find('a')['href'] for item in items]
        mylist.extend(course_urls)
        next_page_url = f"{myurl.split('?')[0]}?{next_page.find('a')['href'].split('?')[1]}"
        # print(next_page_url)
        courses = get_all_courses(next_page_url,course_source='ross')
        # pass


    return mylist
```
