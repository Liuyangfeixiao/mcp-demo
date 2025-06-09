# client.py
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# 这里使用 StdioServerParameters 来指定服务器的启动方式
server_params = StdioServerParameters(
    command="mcp",  # 可执行命令
    args=["run", "server.py"],  # 启动服务器的参数
    env=None,  # 环境变量
)

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
            for tool in tools.tools:
                print(f"Tool: {tool.name}")

            # 调用 Resources
            print("READING RESOURCE")
            content, mime_type = await session.read_resource("greeting://world")
            # print(f"Resource Content: {content} (MIME Type: {mime_type})")

            # 调用 Tools
            print("CALLING TOOL")
            result = await session.call_tool("add", arguments={"a": 1, "b": 2})
            print(result.content)

if __name__ == "__main__":
    import asyncio
    # 启动客户端的会话
    asyncio.run(run())

