import calendar
import requests
import re
from bs4 import BeautifulSoup

def fetch_url(url, user_agent):
    """ Request the html contents from a URL.
    
        Args:
        url (str): URL to fetch.
        user_agent (str, optional): User-agent string to use for the request. Defaults to None.

        Returns:
        BeautifulSoup object if successful, None if an exception occurs.
    """
    headers = {'User-Agent': user_agent} if user_agent else {}
    try:
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the URL: {url}. Error: {e}")
        return None
   
def get_timeframe(before, after):
    """ Transforms the BEFORE and AFTER variables into timeframe arguments.
        Returns a dictionary with keys for start and end date components: 
        start_year, start_month, start_day, end_year, end_month, end_day.
    """
    def parse_date(date_str, start=True):
        parts = list(map(int, date_str.split("-")))
        year = parts[0]
        if len(parts) == 1:
            month = 1 if start else 12
            day = 1 if start else 31
        elif len(parts) == 2:
            month = parts[1]
            day = 1 if start else calendar.monthrange(year, month)[1]
        elif len(parts) == 3:
            month, day = parts[1], parts[2]
        
        return year, month, day

    start_year, start_month, start_day = parse_date(after, start=True)
    end_year, end_month, end_day = parse_date(before, start=False)

    args = {'start_year': start_year, 'start_month': start_month, 'start_day': start_day, 'end_year': end_year, 'end_month': end_month, 'end_day': end_day}

    return args


def get_category_idx(category):
    """ Transforms the given category into a three digit number.
        Naver uses the three digit number in a URL to refer to a category. 
    """ 
    category_mappings = {'정치': 100, '경제': 101, '사회': 102, '생활문화': 103, '세계': 104, 'IT/과학': 105, '오피니언': 110, 'TV': 115}
    
    try:
        category_idx = category_mappings[category]
        return category_idx
    except KeyError:
        raise ValueError(f"Invalid category provided: {category}. Valid categories are: {', '.join(category_mappings.keys())}")


def get_max_page_idx(url, user_agent):
    try:
        soup = fetch_url(url+'&page=2000', user_agent)
        headline_tag = soup.find('div', {'class': 'paging'}).find('strong')
        regex = re.compile(r'<strong>(?P<num>\d+)')
        match = regex.findall(str(headline_tag))
        return int(match[0])
    except Exception:
        return 0