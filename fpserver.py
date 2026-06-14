import logging

logging.basicConfig(
    level   = logging.INFO,
    format  = "[%(asctime)s] %(levelname)s %(name)s - %(message)s",
    datefmt = "%H:%M:%S",
)

from server.database import init_db
from server.tcp_server import start_server

if __name__ == "__main__":
    init_db() 
    start_server()