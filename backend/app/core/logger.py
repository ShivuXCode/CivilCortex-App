import logging
import sys
import os
import contextvars

# Context variables for correlation
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
job_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("job_id", default="")

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        req_id = request_id_var.get()
        job_id = job_id_var.get()
        
        # Format the prefixes
        req_prefix = f"[req:{req_id}] " if req_id else ""
        job_prefix = f"[job:{job_id}] " if job_id else ""
        
        record.correlation_prefix = f"{req_prefix}{job_prefix}"
        return True

# Create a custom logger
logger = logging.getLogger("CivilCortex")
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler(sys.stdout)
f_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "civilcortex.log"))
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Add correlation filter
correlation_filter = CorrelationFilter()
c_handler.addFilter(correlation_filter)
f_handler.addFilter(correlation_filter)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(correlation_prefix)s%(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(correlation_prefix)s%(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
if not logger.hasHandlers():
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
