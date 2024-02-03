from youtube_transcript_api import YouTubeTranscriptApi
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from .tools.Tools import RelevantPartTool, SearchPartTool, RetrieveDocTool
from . import prompt 
from . import config

class Agent():
    def __init__(self) -> None:
        self.tools = [RelevantPartTool(), SearchPartTool(), RetrieveDocTool()]


        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            temperature=config.OPEN_AI_TEMPRATURE,
            model_name= config.OPENAI_MODEL
        )

        self.conversational_memory = ConversationBufferWindowMemory(
            memory_key='chat_history',
            k=config.MEMORY_K,
            return_messages=True
        )

        self.agent = initialize_agent(
            agent='structured-chat-zero-shot-react-description',
            tools=self.tools,
            llm=self.llm,
            verbose=config.AGENT_VERBOSE,
            max_iterations=config.AGENT_NUM_ITER,
            early_stopping_method='generate',
            memory=self.conversational_memory
        )


        new_prompt = self.agent.agent.create_prompt(
            prefix = prompt.agentPrefix,
            suffix = prompt.agentSufix,
            tools = self.tools
        )
        self.agent.agent.llm_chain.prompt = new_prompt
    
    def run(self, input: str) -> str:
        return self.agent(input)
