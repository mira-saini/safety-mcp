from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
"PowerBI Server",
host="0.0.0.0",
port=8000
)

import tools.test_tools


if __name__ == "__main__":
    #local dev: use stdio, deploy: use streamable-http
    mcp.run(transport="stdio") #comment out when deploying to server, uncomment when testing locally
    #mcp.run(transport="streamable-http")