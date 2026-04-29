import omni

def run_dask_delayed(func, *args) -> omni.Result:
    return omni.Result.Ok(func(*args))
