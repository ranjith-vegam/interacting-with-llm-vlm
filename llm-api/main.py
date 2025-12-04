import uvicorn
from src.api.router import app
from src.config.settings import get_config

conf = get_config()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=conf.server.port)