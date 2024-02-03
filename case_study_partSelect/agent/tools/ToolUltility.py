import requests
from bs4 import BeautifulSoup
import json
from youtube_transcript_api import YouTubeTranscriptApi

class ToolUltility:
    def __init__(self) -> None:
        pass

    @classmethod
    def get_video_title(cls, video_ID: str) -> str:
        url = 'https://noembed.com/embed?url=https://www.youtube.com/watch?v='+video_ID
        result = requests.get(url)

        toJson = json.loads(result.content)
        video_title = toJson.get('title')
        return video_title

    @classmethod
    def get_youtube_title_and_trasncript(cls, video_ID: str) -> tuple():
        transcript_result = YouTubeTranscriptApi.get_transcript(video_ID)
        transcript = ''
        for d in transcript_result:
            transcript += d['text'] + ' '
        transcript = transcript.replace('\n', ' ')
        title = cls.get_video_title(video_ID)
        transcript = "vido title: "+ title + '\n' + "Transcript:\n " + transcript
        return (title,transcript)

    @classmethod
    def get_page_video_ID(cls, soup: BeautifulSoup) -> list:
    
        labels = ['div']
        classes = ['yt-video']
        results = soup.find_all(labels,class_=classes)
        viedo_ID_set = set()
        for result in results:
            # Extract and print details from each result
            video_ID = result['data-yt-init']
            if video_ID == "d6AvOkulk_g":
                continue
            viedo_ID_set.add(video_ID)
        return list(viedo_ID_set)

    @classmethod
    def get_all_title_and_transcript(cls, video_ID_list: list) -> list:
        ret = []
        for id in video_ID_list:
            try:
                ret.append(cls.get_youtube_title_and_trasncript(id))
            except Exception as e:
                print(e)
                continue
        return ret
    
    #search a part given part number
    #@param get_video: set true if you want to get youtube video transcrip on that page
    #@param get_story: set true if you want to get user repair story on the page
    @classmethod
    def search_part(cls, query: str, get_video = True, get_story = True) -> str:
        # Inspect the website to find the correct URL and parameters
        url = 'https://www.partselect.com/api/search/'
        params = {'searchterm': query}
        response = requests.get(url, params=params)
        ret = ''
        if response.status_code == 200:
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                #try to determine a page is parts or not. Parts page does not have other parts
                partsList = cls.get_compatible_parts(mode='part',soup=soup, searchPart=False)
                if len(partsList) > 0:
                    ret += "This isn't a part, might be a machine. Found following compatible parts for this machine:\n"
                    for name,part_number in partsList:
                        ret += name + ";"+ part_number + '\n'
                    ret += 'that is all\n'
                    get_video = False
                    get_story = False
                else:
                    part_number_span = soup.find('span', itemprop='productID')
                    if part_number_span:
                        ret += "\nPart number: " + part_number_span.get_text().strip()
                labels = ['div','h1']
                classes = ['pd__description','title-lg','title-main','repair-story__instruction','col-md-6 mt-3']
                results = soup.find_all(labels,class_=classes)
                printed_story = False
                printed_trouble_shooting = False
                printed_name = False
                for result in results:
                    # Extract and print details from each result
                    if not printed_name and('title-lg' in result['class'] or 'title-main' in result['class']):
                        ret += "\nName: "+ result.get_text(strip=True)
                        printed_name = True

                    elif 'pd__description' in result['class']:
                        description_title = result.find('h2', class_='title-md').get_text(strip=True)
                        description = result.find('div', itemprop='description').get_text(strip=True)
                        ret += '\n'+ description_title
                        ret += description

                    elif 'repair-story__instruction' in result['class'] and get_story:
                        if not printed_story:
                            ret += "\nRepair Story From Customer:"
                            printed_story = True
                        ret += '\n' + result.get_text(strip=True)
                    else:
                        if not printed_trouble_shooting:
                            ret += "\nTrouble Shooting:"
                            printed_trouble_shooting = True
                        ret += '\n'+result.get_text(strip=True)
                if get_video:
                    video_id_list = cls.get_page_video_ID(soup)
                    title_and_transcript_list = cls.get_all_title_and_transcript(video_ID_list=video_id_list)
                    for _, transcript in title_and_transcript_list:
                        ret += '\n' + transcript
                return ret
            except Exception as e:
                print(e)
                return "unknown error"
        else:
            print("search_part: network error")
            return "network error"
    
    #get compatible part or search compatible part given a model number of a machine
    @classmethod
    def get_compatible_parts(cls, mode: str = 'model', source_part_ID: str = None, query: str = None, 
                             soup: BeautifulSoup = None, searchPart = True):
        if mode == 'model' and source_part_ID and query:
            params = {"SearchTerm": query}
            url = "https://www.partselect.com/Models/" + source_part_ID + "/Parts/"
            response = requests.get(url, params)
            soup = BeautifulSoup(response.content, 'html.parser')
        elif mode == 'part' and soup:
            pass
        else:
            raise Exception("get_compatible_parts: incorrect args")
        parts_divs = soup.find_all('div', class_='mega-m__part')

        parts_list = []
        for part in parts_divs:
            part_name = part.find('a', class_='mega-m__part__name')
            part_number = part_name.find_next_sibling('div')
            if part_number:
                parts_list.append((part_name.get_text(strip=True), part_number.get_text(strip=True).split(':')[-1]))
        if len(parts_list) == 0:
            return []
        ret = []
        for part_name, part_number in parts_list:
            if searchPart:
                ret.append(cls.search_part(query=part_number, get_video=False, get_story=False))
            else:
                ret.append(("name: "+ part_name," part number: " + part_number))
        return ret
