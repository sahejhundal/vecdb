import uvicorn
import os

if __name__ == "__main__":
    server_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(server_dir)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[server_dir]) 