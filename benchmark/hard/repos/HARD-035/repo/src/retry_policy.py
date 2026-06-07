def plan_retries(response, attempts, base_delay=1, max_delay=None):
    delays = []
    for attempt in range(attempts):
        delay = base_delay * (2 ** attempt)
        if max_delay is not None and delay > max_delay:
            delay = max_delay
        delays.append(delay)
    return delays
