from loguru import logger as log

log.remove(0)
log.add('debug.log',
        format='{time:DD.MM.YYYY HH:mm:ss:ms}|{level}|{name} {function} line:{line}|{message}',
        level='DEBUG',
        rotation='1 MB',
        compression='zip')
