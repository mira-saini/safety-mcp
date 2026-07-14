from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
"PowerBI Server",
host="0.0.0.0",
port=8000
)

#search_description

#filter_for_date
#filter_business_unit_as_key
#filter_OSHA_severity_code
#filter everything except hand-written data (search, count incidences)

#aggregate_by_field
#return table or JSON

#suman puyal
@mcp.tool()
def hello(name: str) -> str:
    """
    Generate a greeting message for the user with their name. Invoke when user says "Hello" or "Hi".
    """
    return f"Hello {name}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")