def is_cancelled(msg):
    return True if msg.strip('/').lower() in ('back', 'start') else False
