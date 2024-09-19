from typing import Optional
from langchain.tools import BaseTool
from .ToolUltility import ToolUltility
from .RetrieveInternal import RetrieveInternal
from .. import prompt
from .. import config

DATAPATH = config.DATAPATH #path to the data folder

class SearchPartTool(BaseTool):
    name = "Get Part Info With Part Number"
    description = prompt.SearchPartTool_desc

    def _run(self, part) -> str:
        prefix_string = "search part number " + part + " returns:\n"
        return prefix_string + ToolUltility.search_part(query=part,get_video=True)
    
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

class RetrieveDocTool(BaseTool):
    name = "Retrieve Troubleshooting Page"
    description = prompt.RetrieveDocTool_desc
    
    doc_retriever = RetrieveInternal(path=DATAPATH)
    
    
    def _run(self, question: str) -> str:
        retrieve_doc_tool_prefix = "If you find answers to your questions from the trouble shooting guide, please provide step by step answer in your thought, but use only the information from the guide:\n"
        return retrieve_doc_tool_prefix + self.doc_retriever.retrieve_internal(input=question, max_length=config.RETRIEVE_MAX_LENGTH, max_size = config.RETRIEVE_MAX_SIZE)
    
    def _arun(self, question: str) -> str:
        raise NotImplementedError("This tool does not support async")

# NOT USED, partSelect has really bad search engine
class SearchPartWithoutID(BaseTool):
    name = "Search Part Without Part Number"
    description = ("use this tool if you want to search some part but do not have the part number or the machine model number. "
                   "This tool should only be used as last resort because it does not perform well"
                   "Need exactly one input [query], for example: dishwasher basket")
    
    def _run(self, query) -> str:
        return ToolUltility.search_part(query=query,get_video=True)

    def _arun(self, query) ->str:
        raise NotImplementedError("This tool does not support async")

class ComptaiblePartTool(BaseTool):
    name = "Find Compatible Part For Machine"
    description = prompt.RelevantPartTool_desc

    def _run(self, machine_model: Optional[str], query: Optional[str]):
        prefix_string = "find compatible part: " + query + ", for machine " + machine_model + " returns: \n"
        result =  ToolUltility.get_compatible_parts(mode='model',source_part_ID=machine_model, query=query)
        if not result:
            return "It is not Compatible, do not use more tool and responde not compatible"
        else:
            ret = prefix_string + 'Posisble compatible part for' + machine_model + "\n"
            for r in result:
                ret += r + '\n'
            return ret
    
    def _arun(self,machine_model: Optional[str], query: Optional[str]) -> str:
        raise NotImplementedError("This tool does not support async")
