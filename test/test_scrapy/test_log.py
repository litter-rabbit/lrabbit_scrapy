
from lrabbit_spider.utils.log import log


log.info("test")
log.debug("test")
log.error("test")
log.critical("test")
log.warning("test")
log.error(Exception("test"))
log.warning(['error'])