# server.py
from mcp.server.fastmcp import FastMCP

# 创建一个 MCP Server
mcp = FastMCP("Demo")

# 添加一个相加的 Tools
@mcp.tool()
def add(a: int, b: int):
    """add two numbers"""
    return a+b

# 添加一个动态的 greeting
@mcp.resource("greeting://{name}")
def greeting(name: str):
    """Greet someone by name"""
    return f"Hello! {name}"


