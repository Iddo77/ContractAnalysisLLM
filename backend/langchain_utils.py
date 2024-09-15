from langchain_core.exceptions import OutputParserException


def invoke_chain_with_error_handling(chain, input_data):
    try:
        ai_output = chain.invoke(input_data)
        return ai_output
    except OutputParserException as e:
        if e.send_to_llm:
            extra_messages = input_data.get("extra_messages", [])
            extra_messages.append(("ai", e.llm_output))
            extra_messages.append(("human", e.observation))
            input_data["extra_messages"] = extra_messages
            return chain.invoke(input_data)
        else:
            raise e
