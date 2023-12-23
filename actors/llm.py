import openai
import ast, copy, random
from openai import OpenAI
import common.utils 
from common.enums import ChatbotType
from common.config import Config
import random
import time

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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"
)

def escapeString(s):
    s = s.replace('1', '\"1\"')
    s = s.replace(' 1', ' \"1\"')    
    s = s.replace('[1', '[\"1\"')
    s = s.replace('2', '\"2\"')
    s = s.replace('[2', '[\"2\"')
    s = s.replace(' 2', ' \"2\"')    
    s = s.replace('3', '\"3\"')
    s = s.replace('[3', '[\"3\"')
    s = s.replace(' 3', ' \"3\"')
    s = s.replace('4', '\"4\"')    
    s = s.replace(' 4', ' \"4\"')    
    s = s.replace('[4', '[\"4\"')
    s = s.replace('5', '\"5\"')    
    s = s.replace(' 5', ' \"5\"')    
    s = s.replace('[5', '[\"5\"')
    s = s.replace('6', '\"6\"')    
    s = s.replace(' 6', ' \"6\"')    
    s = s.replace('[6', '[\"6\"')
    s = s.replace('7', '\"7\"')    
    s = s.replace(' 7', ' \"7\"')    
    s = s.replace('[7', '[\"7\"')
    s = s.replace('8', '\"8\"')
    s = s.replace(' 8', ' \"8\"')    
    s = s.replace('[8', '[\"')
    s = s.replace('9', '\"9\"')    
    s = s.replace(' 9', ' \"9\"')
    s = s.replace('[9', '[\"9\"')
    s = s.replace('*', '\"*\"')
    s = s.replace(' *', '\"*\"')    
    s = s.replace('[*', '[\"*\"')                        
    return s

def firstTimeReply(msgs):
    s = msgs[0]['content']
    i = s.find("please solve this 4x4 sudoku puzzle")
    if i < 0:
        return ""
    start = s.find("[[",i)
    end = s.find("]]",start)
    return '{"rows": '+ escapeString(s[start:end+2]) + '}'


def call_loop(llm_model,msgs,temp=1.0):
    response = ''
    while not(response):
        try:
            response = client.chat.completions.create(model = llm_model, messages=msgs,temperature=temp,max_tokens=800).choices[0].message.content
        except:
            response = ''
            random_seconds = random.randint(5,25)            
            print("LLM call exception occurred, will sleep for " + str(random_seconds) + " seconds.", flush=True)
            time.sleep(random_seconds)
    return response

def llm4(msgs,msg='',temp=1.0) -> str:
    first_time_reply = ""
    #llm = 'openai/gpt-3.5-turbo'    
    #llm = 'mythomist7b'
    #llm = 'anthropic/claude-2',
    #llm = 'teknium/openhermes-2.5-mistral-7b'
    #llm = 'alpindale/goliath-120b'
    #llm = 'mistralai/mistral-7b-instruct'
    #llm = 'meta-llama/llama-2-13b-chat'
    #llm = 'lizpreciatior/lzlv-70b-fp16-hf'
    llm = 'openai/gpt-3.5-turbo'
    #llm = 'openai/gpt-4'
    #llm = 'meta-llama/llama-2-70b-
    #print("About to call this LLM: " + llm,flush=True)
    if msg:
        msgs = [{"role": "user", "content": msg}]
        return call_loop(llm,msgs,temp=temp)
    else:
        first_time_reply = firstTimeReply(msgs)
    if first_time_reply:
        print("First time, will return this reply: " + first_time_reply)
        return firstTimeReply(msgs)
    return call_loop(llm,msgs,temp=temp)
        
def makeChoice(prior_choices,N=4):
    # Completely blind: replacement_str = str(random.randint(1,4))
    #return str(random.randint(1,4))
    r = random.randint(1,N)
    while r in prior_choices:
        r = random.randint(1,N)
    return str(r)
        
def singleRandomReplacement(given_puzzle):
    N = len(given_puzzle)
    print("Inside singleRandomReplacement with this: " + str(given_puzzle) + "\nwith puzzle dimension: " + str(N))
    puzzle = copy.deepcopy(given_puzzle)    
    sublists_with_star = [sublist for sublist in puzzle if "*" in sublist]
    if sublists_with_star:
        chosen_sublist = random.choice(sublists_with_star)
        star_indices = [i for i, x in enumerate(chosen_sublist) if x == "*"]
        prior_choices = set([int(x) for i, x in enumerate(chosen_sublist) if x != "*"])
        if star_indices:
            random_index = random.choice(star_indices)
            choice = makeChoice(prior_choices,N=N)
            print("Decided to operate on this sublist: " + str(chosen_sublist)  + ", will replace index " + str(random_index) + " with this choice: " + choice)
            chosen_sublist[random_index] = choice
            print("Result: " +  str(chosen_sublist) + ". Prior choices: " + str(prior_choices))                  
    return puzzle

# randint(1,12) gives accuracy of about 27-28
# randint(1,10) gives accuracy of about 29-31

#RL = 2
#RH = 6

RL = 6
RH = 26

# 2-6 does reliably better than 0.4 on average, and close to or better than 0.5 sometimes
# 3-7 also does very well. And 2-5 seems even better. 

def setRR(l,h):
    global RL, RH 
    RL = l
    RH = h

def getRLH():
    global RL, RH
    return RL, RH

def randomReplacements(given_puzzle):
    global RL, RH
    for _ in range(1,random.randint(RL,RH)):
        given_puzzle = singleRandomReplacement(given_puzzle)
    return given_puzzle
    
def llm4Random(msgs) -> str:
    print("Inside the RANDOM llm...")
    s = msgs[0]['content']
    i = s.find("try to solve this Sudoku puzzle ")
    first_time = False
    if i < 0:
        i = s.find("try again starting from this Sudoku board")
    if i < 0:
        i = s.find("lease solve this ")
        if i < 0:
            print("Could not find a puzzle to solve, will resort to the usual LLM...")
            return llm4(msgs)
        else:
            print("First time!!!!!!!!!!!!!!!!")
            first_time = True
    start = s.find("[[",i)
    end = s.find("]]",start)
    puzzle_str = s[start:end+2]
    print("Found this puzzle str before quoting: " + puzzle_str)    
    if first_time and not('"' in puzzle_str):
        puzzle_str = escapeString(puzzle_str)
        print("Puzzle str after escaping: " + puzzle_str)
    puzzle = None
    try:
        if first_time:
            print("About to literal_eval for first time...")
            puzzle = ast.literal_eval(puzzle_str)
            print("Right after...")
        else:
            #puzzle = ast.literal_eval(escapeString(puzzle_str))
            escaped = escapeString(puzzle_str)
            print("\nABOUT TO LIT EVAL THIS escapee: " + escaped)
            puzzle = ast.literal_eval(escaped)
    except Exception as e: 
        print("Literal evaluation failed with this error: " + str(e))
    print("Literal evaluation succeeded, will try to do the random replacement now on this puzzle string: " + str(puzzle))
    new_puzzle = None
    if first_time:
        new_puzzle = puzzle
    else:
        try:
            new_puzzle = randomReplacements(puzzle)
        except:
            print("Random replacement failed!")
    print("Random replacement WORKED, with this new_puzzle: " + str(new_puzzle))
    new_puzzle_str = str(new_puzzle).replace("'", '"')
    res = '{"rows": ' + new_puzzle_str + '}'
    return res

class LLMAgent(object):

    def __init__(self, config) -> None:
        self.config = config
        self.chatbot = self._initialize_chatbot(config.chatbot_type)
    
    def compose_messages(self, roles, msg_content_list) -> object:
        if not (len(roles) == len(msg_content_list)):
            raise "Failed to compose messages"
        msgs = [{"role" : roles[i], "content" : msg_content_list[i]} for i in range(len(roles))]
        return msgs
    
    def get_reply(self, messages, temperature = None, max_tokens = None) -> str:
        return self.chatbot.get_reply(messages, temperature, max_tokens)

    def _initialize_chatbot(self, chatbot_type):
        if chatbot_type == ChatbotType.OpenAI:
            return OpenAIChatbot(self.config.openai_model, self.config.openai_api_key)
        else:
            raise "Not supported for now!"


class ChatbotBase(object):

    def __init__(self) -> None:
        pass

    def get_reply(self, messages, temperature = None, max_tokens = None) -> str:
        return ""
    
    
class OpenAIChatbot(ChatbotBase):

    def __init__(self, openai_model, openai_api_key) -> None:
        super().__init__()
        self.model = openai_model
        openai.api_key = openai_api_key

    def get_reply(self, messages, temperature = None, max_tokens = None) -> str:
        print("LLM Query:", messages)
        try:
            reply = llm4(messages)
            #reply = llm4Random(messages)
            print("LLM Reply: [[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[\n", reply,flush=True)
            print("\n]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]\n\n",flush=True)
            return reply
        except:
            reply = "Failed to get LLM reply"
            print(reply,flush=True)
            return reply
