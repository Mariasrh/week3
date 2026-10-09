from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP local server
mcp = FastMCP("My Small Local Server")

@mcp.tool()
def add_numbers(a: float, b: float) -> str:
    """Adds two numbers and returns the result."""
    return f"The result of {a} + {b} is {a + b}"

if __name__ == "__main__":
    # Run the server on stdio transport
    mcp.run(transport="stdio")