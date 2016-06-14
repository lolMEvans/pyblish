def conditional_decorator(condition, decorator, decorator_args, module):
    """Wrap a function in a decorator if a condition is True-
    avoiding trying to import the function until condition is met for e.g. a function only exists for python version 3.
    Args:
        condition (bool): Whether to wrap the function in a decorator.
        decorator (str): String name of decorator to use.
        decorator_args: Argument(s) to be passed to decorator.
        module: Module that decorator function resides in so that this function
            can call the decorator function without importing.
    Return:
        Either the original function or a decorated original function depending on condition.
    """
    if(condition):
        decorator = getattr(module, decorator) if module else eval(decorator)
        return decorator(decorator_args)
    else:
        return lambda x: x