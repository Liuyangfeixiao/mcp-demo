# client.py
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
# 添加 LLM
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 这里使用 StdioServerParameters 来指定服务器的启动方式
server_params = StdioServerParameters(
    command="mcp",  # 可执行命令
    args=["run", "server.py"],  # 启动服务器的参数
    env=None,  # 环境变量
)

llm_client = OpenAI(api_key=os.environ["LLM_API_KEY"], 
                    base_url=os.environ['LLM_BASE_URL'])

def call_llm(prompt, functions):
    model_name = "deepseek-chat"

    print("CALLING LLM")
    response = llm_client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        tools=functions,
        # 可选参数
        temperature=1.,
        max_tokens=1000,
        top_p=1.
    )

    response_message = response.choices[0].message
    # 需要调用的 function tool
    function_to_call = []
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            print("TOOL: ", tool_call)
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            function_to_call.append({"name": name, "args": args})

    return function_to_call

def convert_to_llm_tool(tool: types.Tool):
    """将MCP的 Tool 转换为 LLM Tool"""
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema['properties']
            }
        }
    }

    return tool_schema

async def run():
    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # 初始化连接
            await session.initialize()

            # 列出 server 的 resources
            resources = await session.list_resources()
            print("LISTING RESOURCES")
            for resource in resources:
                print(f"Resource: {resource}")
            
            # 列出 server 的 tools
            tools = await session.list_tools()
            print("LISTING TOOLS")
            functions = []
            for tool in tools.tools:
                print(f"Tool: {tool.name}")
                print(f"Tool {tool.inputSchema['properties']}")
                functions.append(convert_to_llm_tool(tool))
            
            prompt = "Add 2 to 3"

            # 询问 LLM 调用哪个工具
            functions_to_call = call_llm(prompt, functions)

            # 调用建议的 Tools
            print("CALLING TOOL")
            for f in functions_to_call:
                result = await session.call_tool(f['name'], arguments=f['args'])
                print("TOOLS result: ", result.content)

if __name__ == "__main__":
    import asyncio
    # 启动客户端的会话
    asyncio.run(run())

