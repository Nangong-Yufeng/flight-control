"""
用于给日志输出加点颜色
"""


def log_error(string):
    """

    """
    print('\033[1;31m[ERROR]:'+string+'\033[0m')


def log_note(string):
    print('\033[3;4;36m[NOTE]:'+string+'\033[0m')


def log_info(string):
    print('\033[0m[INFO]:'+string+'\033[0m')


if __name__ == '__main__':
    log_error("This is error")
    log_note("This is note")
    log_info("This is info")
    print("--------")
    print('\033[0m[0]\033[0m')
    print('\033[1m[1]\033[0m')
    print('\033[2m[2]\033[0m')
    print('\033[3m[3]\033[0m')
    print('\033[4m[4]\033[0m')
    print('\033[5m[5]\033[0m')
    print('\033[6m[6]\033[0m')
    print('\033[7m[7]\033[0m')
    print('\033[30m[30]\033[0m')
    print('\033[31m[31]\033[0m')
    print('\033[32m[32]\033[0m')
    print('\033[33m[33]\033[0m')
    print('\033[34m[34]\033[0m')
    print('\033[35m[35]\033[0m')
    print('\033[36m[36]\033[0m')
    print('\033[37m[37]\033[0m')
