"""Render/生产环境启动入口"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 8000)))
