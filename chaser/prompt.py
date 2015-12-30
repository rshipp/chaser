YES = "y"
NO = "n"

def prompt(message, default=YES):
    if default == YES:
        yes = YES.upper()
        no = NO.lower()
        check = NO
    else:
        yes = YES.lower()
        no = NO.upper()
        check = YES

    response = input("{message} [{y}/{n}] ".format(message=message, y=yes, n=no))

    if response.lower() == check.lower():
        return check
    return default
