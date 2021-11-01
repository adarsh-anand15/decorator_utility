import time
import functools
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import os
import re
import sys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDA = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDB = '\033[22m'
    ENDC = '\033[39m'
    ENDU = '\033[24m'

def prettify(func):
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        args_list = [str(arg) for arg in args]
        for i in range(len(args_list)):
            pattern_groups = re.findall(r"(?<=\:)([\w\ \[\]\-\_]+\:\s)|^([\*\w\s\[\]\-\_]+\:\s)|\,([\*\w\s\[\]\-\_]+\:\s)|\n([\*\w\s\[\]\-\_]+\:\s)|(\*[\*\w\s\[\]\-\_]+\*)", args_list[i])
            for pattern_group in pattern_groups:
                for pattern in pattern_group:
                    if pattern:
                        args_list[i] = re.sub(r"{}".format(pattern.replace('*', '\*').replace('[','\[').replace(']', '\]')), rf"{bcolors.BOLD}{pattern}{bcolors.ENDB}", args_list[i])
         
        return func(*args_list, **kwargs)
    return wrapper_func

pprint = prettify(print)


def timer(func):
    @functools.wraps(func)
    def timer_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        args_list = [arg for arg in args]
        kwargs_list = [f"{key}={value}" for key, value in kwargs.items()]
        arguments_list = args_list + kwargs_list
        print(
            f"time taken to execute function: {func.__name__}, with arguments: {arguments_list}: {duration}")
        return result

    return timer_wrapper


def print_logs(debug=False):
    def logs_dec(func):
        @functools.wraps(func)
        def logs_wrapper(*args, **kwargs):
            args_list = [arg for arg in args]
            kwargs_list = [f"{key}={value}" for key, value in kwargs.items()]
            arguments_list = args_list + kwargs_list
            
            buf_stdout = StringIO()
            buf_stderr = StringIO()
            with redirect_stdout(buf_stdout):
                with redirect_stderr(buf_stderr):
                    try:
                        result = func(*args, **kwargs)
                        stdout_logs = buf_stdout.getvalue()
                        stderr_logs = buf_stderr.getvalue()
                        main_color = bcolors.HEADER
                    except:
                        import traceback
                        traceback.print_exc()
                        stdout_logs = buf_stdout.getvalue()
                        stderr_logs = buf_stderr.getvalue()
                        result = None
                        main_color = bcolors.FAIL
                    
                                
            if debug == True:
                print(main_color)
                print(f"[MAIN CONFIG]: Process {os.getpid()} finished")
                print(f"{func.__name__} executed with arguments: {arguments_list}")
                print(f"[FINAL RESULT]: {result}")
                print(f"[STDOUT LOGS]:{bcolors.ENDC}\n{stdout_logs}")
            if stderr_logs.strip():
                print(bcolors.FAIL, file=sys.stderr)
                print(f"\n!!!!!!!!!![STDERR LOGS]!!!!!!!!!!:\n{stderr_logs}", file=sys.stderr)
                print(bcolors.ENDC, file=sys.stderr)
            return result
        return logs_wrapper
    return logs_dec


def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [a for a in args]                      # 1
        kwargs_repr = [f"{k}={v}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug

