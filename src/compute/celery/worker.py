import omni

def start_celery_worker(queue: str) -> omni.Result:
    return omni.Result.Ok(True)
