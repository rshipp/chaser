YES = "y"
NO = "n"

def user_input(message):
    """Substitutable input prompt"""
    return input(message)

def prompt(message, default=YES):
    """Handle pacman-like prompting overhead"""
    if default == YES:
        yes = YES.upper()
        no = NO.lower()
        check = NO
    else:
        yes = YES.lower()
        no = NO.upper()
        check = YES

    response = user_input("{message} [{y}/{n}] ".format(message=message, y=yes, n=no))

    if response.lower() == check.lower():
        return check
    return default
