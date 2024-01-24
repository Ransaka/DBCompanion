import os
from .step import Step
from utils.db_utils import detect_database_schema, get_engine
from utils.code_utils import HidePrints,in_notebook
from openai import OpenAI
import markdown
from tqdm import tqdm
from utils.prompt import (
    DATABASE_PROMPT_CATEGORY_NAME,
    DEFAULT_INSTRUCTION_MAP,
    DATABASE_PROMPT_PREFIX,
    START_PROMPT_CATEGORY_NAME,
    EXAMPLE_PROMPT_CATEGORY_NAME,
    END_PROMPT_CATEGORY_NAME
)

class Report:
    def __init__(
            self,
            name:str,
            save_directory:str,
            api_key:str,
            start_instructions:str=None,
            database_instructions:str=None,
            example_instuctions:str=None,
            end_instructions:str=None
    ) -> None:

        self.__check_name(name)
        self.__check_dir_permission()
        self.name = name
        self.steps:list[Step] = []
        self.instruction = {}
        self.save_directory = save_directory
        self.n_steps = 0
        self.oai_client = OpenAI(api_key=api_key)
        # setting instructions
        self._set_instructions(
            instruction_type=START_PROMPT_CATEGORY_NAME,
            instruction=start_instructions
        )
        self._set_instructions(
            instruction_type=END_PROMPT_CATEGORY_NAME,
            instruction=end_instructions
        )
        self._set_instructions(
            instruction_type=EXAMPLE_PROMPT_CATEGORY_NAME,
            instruction=example_instuctions
        )
        self._set_instructions(
            instruction_type=DATABASE_PROMPT_CATEGORY_NAME,
            instruction=database_instructions
        )

    def add_source_database(self, username, password, port, host, database, tables=None):
        self.connection = get_engine(host=host, username=username, password=password, database=database, port=port)
        self.connection.ping()
        self.database_schema = detect_database_schema(connecton=self.connection, database=database, tables_to_lookup=tables)
        self.__connection_params = {
            'username':username,
            'password':password,
            'host':host,
            'port':port,
            'database':database
            }
        if self.instruction[DATABASE_PROMPT_CATEGORY_NAME] is None:
            __database_instruction = DATABASE_PROMPT_PREFIX + self.database_schema
            self.add_instruction(
                instruction_type=DATABASE_PROMPT_CATEGORY_NAME, instruction=__database_instruction)

    def _set_instructions(self, instruction_type, instruction):
        self.__check_instructions(instruction_type)
        if instruction is None:
            instruction = DEFAULT_INSTRUCTION_MAP[instruction_type]
        self.add_instruction(
            instruction_type=instruction_type, instruction=instruction)

    @staticmethod
    def __check_name(name):
        if "." in name:
            raise ValueError(f"Name should not contain periods(.)")
    
    @staticmethod
    def __check_dir_permission():
        # Check read and write permissions
        path = os.getcwd()
        read_permission = os.access(path, os.R_OK)
        write_permission = os.access(path, os.W_OK)

        if read_permission and write_permission:
            pass
        else:
            raise PermissionError(f"{path}")
        
    @staticmethod
    def __check_instructions(instruction_type):
        if instruction_type not in DEFAULT_INSTRUCTION_MAP:
            raise ValueError("Instruction type should be one of {}, recieved {}".format(
                ", ".join(list(DEFAULT_INSTRUCTION_MAP.keys())), instruction_type))

    def add_instruction(self, instruction_type, instruction):
        self.__check_instructions(instruction_type)
        self.instruction[instruction_type] = instruction
    
    @property
    def system_prompt(self):
        return """{}\n{}\n{}\n{}""".format(
            self.instruction[START_PROMPT_CATEGORY_NAME],
            self.instruction[DATABASE_PROMPT_CATEGORY_NAME],
            self.instruction[EXAMPLE_PROMPT_CATEGORY_NAME],
            self.instruction[END_PROMPT_CATEGORY_NAME]
            )

    def add_step(self, query: str):
        self.steps.append(
            Step(instruction=self.system_prompt,query=query, id=self.n_steps+1)
        )
        self.n_steps += 1
    
    @staticmethod
    def __create_directory(directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    def compile_report(self, force_execute_steps=True):
        if not force_execute_steps:
            raise NotImplementedError("force_execute_steps=False functionality not yet implemented")
        
        # with HidePrints():
        self.__create_directory(self.save_directory)
        self.report_path = f"{self.save_directory}/{self.name}.md"
        with open(self.report_path,'w') as f:
            f.write(f"<h1>{self.name: ^100}</h1>\n")
            for step in tqdm(self.steps,total=self.n_steps, desc='Compiling report... '):
                step.compile(
                    connection_param_dict=self.__connection_params,
                    save_location=self.save_directory,
                    client=self.oai_client,
                    execute=force_execute_steps
                )
                f.write(f"<h3>{step.id} - {step.title}</h3>\n")
                if step.meta['return_type']=='plot':
                    f.write(f"<img src='{step.meta['details']}'>\n")
                elif step.meta['return_type']=='table':
                    f.write(f"{step.meta['details']}\n")
                else:
                    f.write(f"<p>{step.meta['details']}</p>\n")
    
    def save_as_html(self):
        report_path_html = self.report_path.replace(".md",".html")
        markdown.markdownFromFile(input=self.report_path, output=report_path_html)