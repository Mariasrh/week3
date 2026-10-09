import sys
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_servers():
    print("--- Test 1: Local Server ---")
    try:
        client_local = MultiServerMCPClient({
            "small_server": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-u", "my_small_server.py"]
            }
        })
        tools_local = await client_local.get_tools()
        print(" Local Server OK. Tools:", [t.name for t in tools_local])
    except Exception as e:
        print(" Local Server Failed:", e)

    print("\n--- Test 2: Public Server (Time) ---")
    try:
        client_time = MultiServerMCPClient({
            "time_server": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "mcp_server_time", "--local-timezone=Europe/Paris"]
            }
        })
        tools_time = await client_time.get_tools()
        print(" Public Server OK. Tools:", [t.name for t in tools_time])
    except Exception as e:
        print(" Public Server Failed:", e)

if __name__ == "__main__":
    asyncio.run(test_servers())