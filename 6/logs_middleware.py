from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import jwt
from jwt import PyJWTError
from logging.handlers import RotatingFileHandler
import logging



def get_logger(path="logs/api.log"):
    """
    Creates a rotating log
    """
    logFormatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    
    # add a rotating handler
    if not logger.handlers:
        # Agregar un nuevo manejador solo si no se ha agregado anteriormente
        handler = RotatingFileHandler(path, maxBytes=100*1000000, backupCount=20)
        handler.setFormatter(logFormatter)
        logger.addHandler(handler)
    return logger

SECRET_KEY = "fca9f70fc9713c56316dba657364f8980be3aba009dac436a5a3fcc319b08c40"
ALGORITHM = "HS256"

logger = get_logger()




class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = datetime.now()
        response = await call_next(request)
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        user = None
        detail = None
        header = response.headers.items()
        for h in header:
            if h[0] == "set-cookie":
                if "Authorization" in h[1]:
                    token = h[1].split(" ")[1]
                    token = token[:-2]
                    try:
                        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        user = payload.get("sub")
                    except:
                        print("Hubo un erro al realizar el payload de las cookies")
                elif "detail" in h[1]:
                    detail = h[1].split("=")[1]
                    if "Webhook" in detail:
                        detail = detail.split(";")[0]
                    else:
                        detail = detail.split(";")[0][1:-1]

        if "Host" in request.headers:
            Host = request.headers["Host"]
        else:
            Host = None

        if "User-Agent" in request.headers:
            agent = request.headers["User-Agent"]
        else:
            agent = None

        path = request.url.path
        
        log_message = f"{request.method}|{response.status_code}|{request.url}|{path}|{request.client.host}:{request.client.port}|{elapsed_time.total_seconds()}|{user}|{detail}|{Host}|{agent}"
        if int(response.status_code) > 300:
            logger.error(log_message)
        else:
            logger.info(log_message)
        return response
