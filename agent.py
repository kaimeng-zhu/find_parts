import json
import numpy as np
from langchain_openai import OpenAIEmbeddings
import requests
from bs4 import BeautifulSoup
import json
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional

#todo: change private function name
#todo: change calling function to arg = arg
#todo: _arun

class Retrieve_internal:
    embeddings_model = OpenAIEmbeddings(openai_api_key="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")
    
    def __init__(self) -> None:
        with open("data/scrapData.json","r") as file:
            self.internal_docs = json.load(file)
        with open("data/128Embedding.npy","rb") as file:
            self.internal_docs_embeddings = np.load(file)
        

    
    def retrieve_internal(self, input: str, max_length: int = 1000, max_size: int = 1) -> str:
        input_embedding = self.embeddings_model.embed_documents([input])
        dot_distances = np.dot(self.internal_docs_embeddings, np.array(input_embedding).transpose())
        dot_distances = [(dot_distances[i],i) for i in range(len(dot_distances))]   
        dot_distances.sort(reverse=True)
        ret = ''
        append_idx = 0
        while len(ret) < max_length and append_idx < max_size:
            ret += self.internal_docs[dot_distances[append_idx][1]] + '\n'
            append_idx += 1
        return ret


class ScrapUltility:
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
    @classmethod
    def search_part(cls, query: str, get_video = True) -> str:
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

                    elif 'repair-story__instruction' in result['class']:
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
                ret.append(cls.search_part(query=part_number, get_video=False))
            else:
                ret.append(("name: "+ part_name," part number: " + part_number))
        return ret

from typing import Optional
from langchain.tools import BaseTool


class SearchPartTool(BaseTool):
    name = "get part info with part number"
    description = ("use this tool if you have a part number such as WPW10500154 or PS3406972, and want to get relevent information on that part."
                   "To use the tool you must provide exactly one argument ['part']."
                   "For example: if you want to know how to install PS3406972, use this tool with argument PS3406972")

    def _run(self, part) -> str:
        return ScrapUltility.search_part(query=part,get_video=True)
    
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

class RetrieveDocTool(BaseTool):
    name = "retrive troubleshooting document"
    description = ("Use this tool if you have a question about repair. "
                   "This tool need exactly one input [question]. Example input: "
                   "How to fix my fridge that's constantly ranning. How to fix my dishwasher door"
                   )
    
    doc_retriever = Retrieve_internal()
    
    
    def _run(self, question: str) -> str:
        return self.doc_retriever.retrieve_internal(input=question, max_length=3000, max_size = 5)

class SearchPartWithoutID(BaseTool):
    name = "search part without part number"
    description = ("use this tool if you want to search some part but do not have the part number or the machine model number. "
                   "This tool should only be used as last resort because it does not perform well"
                   "Need exactly one input [query], for example: dishwasher basket")
    
    def _run(self, query) -> str:
        return ScrapUltility.search_part(query=query,get_video=True)

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

class RelevantPartTool(BaseTool):
    name = "find relevant part for machine"
    description = (
    "Use this tool when you need to find related part of a machine. "
    "To use the tool you must provide exactly two argument [machine_model, query]. "
    "The first argument must be a model number of a machine, such as WDT780SAEM1. " 
    "The second argument can be a part number such as PS3406971, or a description, such as dishrack wheel. "
    "For exmaple: " 
    "question: I want a drawer track for FPHD2491KF0. Then call tool with machine_model: FPHD2491KF0, query: drawer track. "
    "question: is PS429725 compatible with my FGHS2631PF4A. Then call tool with machine_model: FPHD2491KF0, query: PS429725. "
    "If the result says it is compatible but under a different name, it is still compatible."
    )

    def _run(self, machine_model: Optional[str], query: Optional[str]):
        result =  ScrapUltility.get_compatible_parts(mode='model',source_part_ID=machine_model, query=query)
        if not result:
            return "did not found compatible parts"
        else:
            ret = 'Compatible parts found: '
            for r in result:
                ret += r + '\n'
        print(ret)
        return ret



tools = [RelevantPartTool(), SearchPartTool(), RetrieveDocTool()]

from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent


OPENAI_API_KEY = "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"
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    model_name='gpt-3.5-turbo'
)

conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

agent = initialize_agent(
    agent='structured-chat-zero-shot-react-description',
    tools=tools,
    llm=llm,
    temperature = 0,
    verbose=True,
    max_iterations=3,
    early_stopping_method='generate',
    memory=conversational_memory
)

new_prompt = agent.agent.create_prompt(
    prefix = "Answer the following questions as best you can. Use at least one tool for every answer, you can use multiple tools if needed. "
    "You can only answer questions related to refridgriator or dishwasher parts or repair. If user asks things that's not related to these, your final answer should be telling the user to ask relevent question. "
    "You have access to the following tools: ",
    suffix = ("Begin! Reminder to always use the exact characters `Final Answer` when responding. Always use the exact name of the argument when using tool. "
                "make sure Action is in the correct format"          
    ),
    tools = tools
)

#print(new_prompt.messages[0].prompt.template)
agent.agent.llm_chain.prompt = new_prompt

output = agent("Is PS3406971 compatible with my WDT780SAEM1 model")
#output = agent("How can I install part number PS11752778")
#output = agent("how to fix my dishwasher not drying")
print(output)