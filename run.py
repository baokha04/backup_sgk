import asyncio
import sys
import uvicorn

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # NOTE: reload=True on Windows may force SelectorEventLoop, which breaks Playwright.
    # If you need reload, be aware that subprocesses might fail.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
