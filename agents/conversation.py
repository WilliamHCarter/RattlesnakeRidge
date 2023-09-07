
from dataclasses import dataclass
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.messages import ChatMessage
from agents.agent import Agent, PlayerAgent

@dataclass
class ConversationResponse:
    text: str
    conversation_ends: bool    

class Conversation:
    def __init__(self, agents: list[Agent | PlayerAgent], prompt: str, extra_flavor: dict, llm):
        # Declare vars
        self.agents = agents 
        self.conversations = []
        self.formatted_prompts = []

        # Create the prompts and conversations
        for i, agent in enumerate(agents):
            self.formatted_prompts.append(prompt.format(**{**agent._raw, **extra_flavor}))

            #Initialize the conversations  
            if not isinstance(agent, PlayerAgent):  
                self.conversations.append(LLMChain(
                    llm=llm,
                    prompt=PromptTemplate.from_template(self.formatted_prompts[i]),
                    verbose=False,
                    memory=self.agents[i]._memory
                ))
            else:
              self.conversations.append('player')


    def __parse_response(self, text: str) -> ConversationResponse:
        # If the text starts with "[QUIT]", the conversation
        # is over and that command should be stripped.
        terminate_prefix = '[QUIT]'
        if text.startswith(terminate_prefix):
            text = text[len(terminate_prefix):].lstrip()
            return ConversationResponse(text, True)
        return ConversationResponse(text, False)


    #Loops through each member of the conversation and allows them to speak.
    def converse(self, initial_message: str) -> ConversationResponse:
        carried_message = initial_message
        responses: list[ConversationResponse] = []

        while self.agents:
            current_agent = self.agents[0]
            if isinstance(current_agent, PlayerAgent):
                self.agents.pop(0)
                self.agents.append(current_agent)
                tmp = self.conversations.pop(0)
                self.conversations.append(tmp)                
                return responses
            
            # Let the current agent talk
            res, mes = self.__talk(carried_message)
            responses.append(res)
            for a in self.agents:
                a._memory.chat_memory.add_message(mes)

            # Put the current agent at the end of the list
            self.agents.pop(0)
            self.agents.append(current_agent)
            tmp = self.conversations.pop(0)
            self.conversations.append(tmp)

            carried_message = res.text
    
    #Makes a single agent speak given a message.
    def __talk(self, input_message: str) -> tuple[ConversationResponse, ChatMessage]:
        if (isinstance(self.conversations[0], PlayerAgent)):
            raise ValueError("PlayerAgent shoudn't talk via this method");
        full_response = self.conversations[0]({"message": input_message})
        response = self.__parse_response(full_response['text'])

        # We need to remove and rename the AIMessage that gets added automatically
        # and re-add it as a ChatMessage with the correct label
        cm = self.agents[0]._memory.chat_memory
        cm.messages = cm.messages[:-1]
        message = ChatMessage(role=self.agents[0].name, content=response.text)
        # Return the generated response
        return response, message

