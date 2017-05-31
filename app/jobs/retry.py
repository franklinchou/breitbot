import time
from functools import wraps

def retry(checked_exception, tries=4, delay=3, backoff=2):
    def retry_decorate(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return f(*args, **kwargs)

                # checked_exception as type Exception or tuple of Exceptions
                except checked_exception as e:
                    time.sleep(m_delay)
                    m_tries = m_tries - 1
                    m_delay = m_delay * backoff

            return f(*args, **kwargs)
        return f_retry
    return retry_decorate

