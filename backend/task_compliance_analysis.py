import json
import asyncio
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from langchain.schema import BaseOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from pydantic import ValidationError

from backend.langchain_utils import invoke_chain_with_error_handling
from backend.utils import extract_json_from_text
from models import Contract, TaskAnalysisResult, TaskAnalysisResponse


class TaskComplianceAnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.6)
        self.analyze_task_compliance_chain = get_analyze_task_compliance_chain(self.llm)

    async def analyze_task_compliance(self, contract_json: str, task_description: str,
                                      task_cost: float) -> TaskAnalysisResult:
        input_data = {
            'contract_json': contract_json,
            'task_description': task_description,
            'task_cost': task_cost,
            'extra_messages': []
        }
        task_analysis_result = invoke_chain_with_error_handling(self.analyze_task_compliance_chain, input_data)
        return task_analysis_result


def get_analyze_task_compliance_chain(llm: ChatOpenAI):

    # JSON in prompt has double brackets, which is needed as escape characters.
    # Otherwise, LangChain tries to parse the texts as variables.

    prompt_text = """### CONTEXT:
The following JSON is a contract containing various terms and constraints for work execution.

%%%
{contract_json}
%%%

### OBJECTIVE
You task is to analyze whether the following task is compliant to the contract:

TASK: {task_description}
COST: {task_cost}

The analysis must be formatted as a JSON, detailed below.

### GUIDELINES
- Find the applicable terms in the contract and then reason whether the task complies to these terms.
- Possibly, the task compliance is ambiguous.
    
### EXAMPLE

This is an example of the desired output, unrelated to the contract JSON above.

{{
  "task_description": "Training session in an offshore location in Greenland",
  "task_cost": 2800,
  "applicable_terms": [
    {{
      "title": "2.1 Travel Budget Cap",
      "content": "The total travel budget for any single trip must not exceed $3,000."
    }}
  ],
  "reasoning": "The trip does not exceed the budget cap of $3,000.",
  "compliance": true,
  "ambiguous": false
}}

This is an example of an ambiguous case:

{{
  "task_description": "Training session in an offshore location in Greenland",
  "task_cost": 4000,
  "applicable_terms": [
    {{
      "title": "2.1 Travel Budget Cap",
      "content": "The total travel budget for any single trip must not exceed $3,000."
    }},
    {{
      "title": "2.2 Special Approval for Offshore Locations",
      "content": "Trips to offshore locations may exceed the budget cap with prior written approval from the project manager."
    }}
  ],
  "reasoning": "The trip was planned in advance and exceeds the budget cap of $3,000. However, it involves travel to an offshore location. It's unclear if prior approval was obtained, creating ambiguity about whether the expense is allowable.",
  "compliance": false,
  "ambiguous": true
}}

Notes on the example:
- **All properties are required** and must match the structure provided.
- **Terms consist of a title and content** and must refer back LITERALLY to the contract JSON.
- The JSON will be validated against a Pydantic model, so make sure to stick to the structure.
- The task_cost type in the model is a float, so do not include a currency symbol.

### RESULT
Respond with the JSON only. Do NOT add any other text. Stick to the structure of the JSON examples. 
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert at judging compliance of tasks to a contract."),
            ("human", prompt_text),
            MessagesPlaceholder(variable_name="extra_messages")
        ]
    )

    chain = (
            prompt
            | llm
            | TaskComplianceJsonOutputParser()
    )
    return chain


class TaskComplianceJsonOutputParser(BaseOutputParser):
    def parse(self, text: str) -> TaskAnalysisResult:
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
            return TaskAnalysisResult(**data)
        except ValidationError as e:
            raise OutputParserException(
                error=f"JSON does not conform to the expected structure: {e}",
                observation="The JSON structure is incorrect. Ensure it matches the required format.",
                llm_output=text,
                send_to_llm=True
            )


async def analyze_tasks_compliance(contract_json: str, tasks: List[dict],
                                   agent: TaskComplianceAnalysisAgent) -> TaskAnalysisResponse:

    async def analyze_single_task(task):
        task_description = task['task_description']
        task_cost = task['task_cost']
        try:
            return await agent.analyze_task_compliance(contract_json=contract_json,
                                                       task_description=task_description,
                                                       task_cost=task_cost)
        except Exception as e:
            return TaskAnalysisResult(
                task_description=task_description,
                task_cost=task_cost,
                applicable_terms=[],
                reasoning=f"An error occurred while analyzing compliance: {e}.",
                compliance=False,
                ambiguous=True
            )

    # Gather all analyze_single_task coroutines to run them concurrently
    results = await asyncio.gather(*(analyze_single_task(task) for task in tasks))

    return TaskAnalysisResponse(results=results)
