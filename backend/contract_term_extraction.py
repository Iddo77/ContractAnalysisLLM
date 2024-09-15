import json
from typing import Tuple

from langchain_openai import ChatOpenAI
from langchain.schema import BaseOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from pydantic import ValidationError

from backend.langchain_utils import invoke_chain_with_error_handling
from backend.utils import extract_json_from_text
from models import Contract


class ContractTermExtractionAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.6)
        self.extract_contract_terms_chain = get_extract_contract_terms_chain(self.llm)

    async def extract_contract_terms(self, contract_text: str) -> Tuple[Contract, str]:
        input_data = {
            'contract_text': contract_text,
            'extra_messages': []
        }
        agent = invoke_chain_with_error_handling(self.extract_contract_terms_chain, input_data)
        return agent


def get_extract_contract_terms_chain(llm: ChatOpenAI):

    # JSON in prompt has double brackets, which is needed as escape characters.
    # Otherwise, LangChain tries to parse the texts as variables.

    prompt_text = """### CONTEXT:
The following text is a contract text containing various terms and constraints for work execution.

%%%
{contract_text}
%%%

### OBJECTIVE
Your task is to extract all definitions, sections and terms from the contract and structure them in a JSON format. 

### GUIDELINES
- Section may contain subsections, but this is not always the case.
- Amendments can be treated as sections.

### EXAMPLE
This is an example of the desired output, unrelated to the contract text above.

{{
  "title": "Employment Contract between TechCorp and John Smith",
  "definitions": {{
    "Agreement": "This Employment Contract establishes the terms of employment between TechCorp and John Smith."
  }},
  "sections": [
    {{
      "title": "1. Employment Terms",
      "terms": [
        {{
          "title": "1.1 Position and Duties",
          "content": "John Smith will be employed as a Software Engineer and will perform duties as assigned."
        }}
      ],
      "subsections": []
    }}
  ]
}}

Notes on the example:
- Additional definitions can be added to the definitions object.
- More sections, subsections, and terms can be added to the respective arrays if needed.
- The JSON will be validated against a Pydantic model, so make sure to stick to the structure.
- The top-level properties (title, definitions and sections) are required.
- If you add an object, like a term or a section, make sure to include ALL properties. If information is missing, use an empty string.

### RESULT
Respond with the JSON only. Do NOT add any other text. Stick to the structure of the JSON example. 
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert at extracting information from contracts and formatting it in JSON."),
            ("human", prompt_text),
            MessagesPlaceholder(variable_name="extra_messages")
        ]
    )

    chain = (
            prompt
            | llm
            | ContractJsonOutputParser()
    )
    return chain


class ContractJsonOutputParser(BaseOutputParser):
    def parse(self, text: str) -> Tuple[Contract, str]:
        try:
            text = extract_json_from_text(text)
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise OutputParserException(
                error=f"Invalid JSON format: {e}",
                observation="The output is not valid JSON. Ensure you provide the JSON as specified, and nothing else.",
                llm_output=text,
                send_to_llm=True
            )
        try:
            contract = Contract(**data)
        except ValidationError as e:
            raise OutputParserException(
                error=f"JSON does not conform to the expected structure: {e}",
                observation="The JSON structure is incorrect. Ensure it matches the required format.",
                llm_output=text,
                send_to_llm=True
            )
        return contract, text
