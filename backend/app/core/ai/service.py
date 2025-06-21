from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, AsyncGenerator
from app.database.chat_history_service import insert_chat_history, get_chat_history, format_chat_history
from .tools import ProductSearchTool, ProductPriceTool, ProductAddressTool, ProductSpecsTool, ProductPolicyTool, SearchWebTool, FlexibleProductSearchTool
from .prompts import product_prompt, product_prompt_2, product_prompt_4, product_prompt_5, product_prompt_6
from datetime import datetime
from openai import RateLimitError
import tiktoken

load_dotenv()

OPEN_API_API_KEY = os.getenv("OPENAI_API_KEY")
if OPEN_API_API_KEY is None:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

product_search_tools = ProductSearchTool()
product_price_tools = ProductPriceTool()
product_address_tools = ProductAddressTool()
product_specs_tools = ProductSpecsTool()
product_policy_tools = ProductPolicyTool()
search_web_tools = SearchWebTool()
flexible_product_search_tools = FlexibleProductSearchTool()


class CustomerHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()

    def on_chat_message(self, message: str, **kwargs: Any) -> None:
        print(f"Chat message saved: {message}")

def get_llm_and_agent() -> AgentExecutor:
    llm_products = ChatOpenAI(
        openai_api_key=OPEN_API_API_KEY,
        model="gpt-4.1",
        temperature=0.7,
        max_tokens=3000,
        top_p=1,
        frequency_penalty=0,
        streaming=True,
        callbacks=[CustomerHandler()],
    )

    tools = [
        # product_search_tools,
        # product_price_tools,
        # product_address_tools,
        # product_specs_tools,
        # product_policy_tools,
        flexible_product_search_tools,
        search_web_tools
    ]

    # functions = [convert_to_openai_function(tool) for tool in tools]

    current_date = datetime.now()


    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", product_prompt_6.format(current_date=current_date)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(llm=llm_products, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=3,
        # return_only_outputs=True,
        # return_only_outputs=True,
        # return_direct=True,
        return_intermediate_steps=True,
    )

    return agent_executor

def get_answer_from_llm(
    user_input: str,
    thread_id: str,
) -> Dict[str, Any]:
    """
    Hàm lấy câu trả lời cho một câu hỏi
    
    Args:
        question (str): Câu hỏi của người dùng
        thread_id (str): ID của cuộc trò chuyện
        
    Returns:
        str: Câu trả lời từ AI
    """
    if user_input is None:
        raise ValueError("User input cannot be None.")
    if thread_id is None:
        raise ValueError("Thread ID cannot be None.")


    agent_executor = get_llm_and_agent()

    # Get the chat history
    chat_history = get_chat_history(thread_id=thread_id)
    formatted_chat_history = format_chat_history(chat_history)

    response = agent_executor.invoke(
        {
            "input": user_input,
            "chat_history": formatted_chat_history,
        },
    )
    
    # Save the chat history
    if isinstance(response, dict) and "output" in response:
        # insert_chat_history(thread_id, user_input, response)
        insert_chat_history(thread_id, user_input, response["output"])

    return response

async def get_answer_streaming(
    user_input: str,
    thread_id: str,
) -> AsyncGenerator[Dict, None]:
    try:
        # Implement token counting
        enc = tiktoken.get_encoding("o200k_base")
        input_tokens = len(enc.encode(user_input))
        
        # Get limited chat history to prevent token overflow
        chat_history = get_chat_history(thread_id=thread_id, limit=10)  # Only get last 10 messages
        formatted_chat_history = format_chat_history(chat_history)
        
        # Đảo ngược lịch sử để bắt đầu từ tin nhắn mới nhất
        reversed_history = list(reversed(formatted_chat_history))

        # Khởi tạo biến để lưu trữ lịch sử đã cắt và tổng số token
        trimmed_history = []
        total_tokens = input_tokens

        # Duyệt qua lịch sử từ mới nhất đến cũ nhất
        for msg in reversed_history:
            msg_tokens = len(enc.encode(str(msg)))
            if total_tokens + msg_tokens > 25000:
                break
            trimmed_history.insert(0, msg)  # Chèn vào đầu danh sách
            total_tokens += msg_tokens
            
        agent_executor = get_llm_and_agent()
        final_answer = ""

        async for event in agent_executor.astream_events(
            {
                "input": user_input,
                "chat_history": trimmed_history,
            },
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"].get("chunk")
                if chunk and hasattr(chunk, "content"):
                    content = chunk.content
                    if content:
                        final_answer += content
                        yield content
    
    except RateLimitError as e:
        error_message = "I apologize, but I'm receiving too many requests right now. Please try again in a few moments."
        yield error_message
        return

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        yield error_message
        return

    finally:
        if final_answer and final_answer.strip():
            try:
                insert_chat_history(thread_id, user_input, final_answer)
            except Exception as e:
                print(f"Error inserting chat history: {str(e)}")


if __name__ == "__main__":
    import asyncio
    
    async def test():
        # answer = get_answeget_answer_streamingr_stream("hi", "test-session")
        # print(answer)
        async for event in get_answer_streaming("hi", "test-session"):
            print('event:', event)
        print('done')

    
    asyncio.run(test())