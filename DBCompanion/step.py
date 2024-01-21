from utils.oai_utils import get_gpt_response
from utils.code_utils import get_executable_code,get_execution_output
from openai import Client

class Step:
    def __init__(self,instruction,query, id) -> None:
        self.queries = []
        self.instructions = instruction
        self.queries.append(query)
        self.llm_responses = []
        self.code_history = []
        self.executed_queries = []
        self.meta = {}
        self.id = id

    def __fetch_llm_response(self,client):
        self.llm_responses.append(
            get_gpt_response(client=client, system_prompt=self.instructions, user_prompt=self.queries[-1])
        )
        self.executed_queries.append(
            self.queries[-1]
        )
    
    def execute_code(self,executable_code:str):
        output = get_execution_output(executable_code)
        if ".png" in output:
            self.meta['return_type'] = 'plot'
        elif "<table" in output:
            self.meta['return_type'] = 'table'
        else:
            self.meta['return_type'] = 'text'
        self.meta['details'] = output.strip()
        
    def compile(self, connection_param_dict:dict, save_location:str, client:Client, execute=False):
        try:
            if len(self.llm_responses)==0 and not execute:
                raise ValueError("You may need to execute step in order to preview it. You can force execute by calling preview with `execute=True`")
            elif len(self.llm_responses)==0 and execute:
                self.__fetch_llm_response(client)
                self.compile(connection_param_dict=connection_param_dict, save_location=save_location, client=client, execute=execute)
            else:
                executable_code =  get_executable_code(
                    llm_response=self.llm_responses[-1],
                    connection_param_dict=connection_param_dict,
                    save_location=save_location
                    )
                self.code_history.append(executable_code)
                return self.execute_code(executable_code)
        except Exception as e:
            if executable_code:
                self.code_history.append(executable_code)
            self.meta['return_type'] = 'error'
            self.meta['details'] = e
            return
    
    @property
    def title(self):
        return self.queries[-1]
    
    def __repr__(self) -> str:
        return f"""Name: {self.queries[-1]}"""
    