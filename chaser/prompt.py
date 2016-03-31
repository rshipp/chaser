import termcolor

YES = _("y")
NO = _("n")

def user_input(message):
    """Substitutable input prompt"""
    return input(message)

def prompt(message, default=YES, major='', color=None):
    """Handle pacman-like prompting overhead"""
    if default == YES:
        yes = YES.upper()
        no = NO.lower()
        check = NO
    else:
        yes = YES.lower()
        no = NO.upper()
        check = YES

    response = user_input((major and termcolor.colored(':: ', 'blue', attrs=['bold'])) + \
		termcolor.colored("{message} [{y}/{n}] ".format(
	message=message, y=yes, n=no), color=color, attrs=['bold']))

    if response.lower() == check.lower():
        return check
    return default
