

from typing import Optional
from langchain.tools import BaseTool
from .ToolUltility import ToolUltility
from .RetrieveInternal import RetrieveInternal
from .. import prompt

DATAPATH = "data"

class SearchPartTool(BaseTool):
    name = "get part info with part number"
    description = prompt.SearchPartTool_desc

    def _run(self, part) -> str:
        return ToolUltility.search_part(query=part,get_video=True)
    
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

class RetrieveDocTool(BaseTool):
    name = "retrive troubleshoot page"
    description = prompt.RetrieveDocTool_desc
    
    doc_retriever = RetrieveInternal(path=DATAPATH)
    
    
    def _run(self, question: str) -> str:
        return self.doc_retriever.retrieve_internal(input=question, max_length=3000, max_size = 5)
    
    def _arun(self, question: str) -> str:
        raise NotImplementedError("This tool does not support async")

# NOT USED, partSelect has really bad search engine
class SearchPartWithoutID(BaseTool):
    name = "search part without part number"
    description = ("use this tool if you want to search some part but do not have the part number or the machine model number. "
                   "This tool should only be used as last resort because it does not perform well"
                   "Need exactly one input [query], for example: dishwasher basket")
    
    def _run(self, query) -> str:
        return ToolUltility.search_part(query=query,get_video=True)

    def _arun(self, query) ->str:
        raise NotImplementedError("This tool does not support async")

class RelevantPartTool(BaseTool):
    name = "Find relevant part for machine"
    description = prompt.RelevantPartTool_desc

    def _run(self, machine_model: Optional[str], query: Optional[str]):
        result =  ToolUltility.get_compatible_parts(mode='model',source_part_ID=machine_model, query=query)
        if not result:
            return "did not found compatible parts"
        else:
            ret = ''
            for r in result:
                ret += r + '\n'
            return ret
    
    def _arun(self,machine_model: Optional[str], query: Optional[str]) -> str:
        raise NotImplementedError("This tool does not support async")
