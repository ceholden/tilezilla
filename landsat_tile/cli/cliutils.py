import click


class Echoer(object):

    """ Stylistic wrapper around click.echo for communicating with user

    Communication methods:

        1. process: announce beginning of some process
        2. item: progress within a process for an item
        3. info: general information
        4. warnings: warnings, less severe than errors
        5. error: errors

    Args:
      message_indent (int): indent messages beyond process/item/info indicator
        by a number of spaces (default: 0)
      file (str): write output to a file (default: 'stdout')
      err (bool): if True and file is 'stdout', write to 'stderr' instead

    """

    def __init__(self, message_indent=0, file='stdout', err=False):
        self.message_indent = message_indent

        if file == 'stdout':
            self.file = None
        elif file == 'stderr':
            self.file = None
            err = True
        else:
            self.file = file

        self.err = err

    def process(self, msg, **kwargs):
        """ Print a message about a process

        Process messages are prepended with "==> "
        """
        msg = click.style(msg, **kwargs)
        pre = click.style('==> ' + ' ' * self.message_indent,
                          fg='blue', bold=True)

        click.echo(pre + msg, file=self.file, err=self.err)

    def item(self, msg, **kwargs):
        """ Print a progress message for an  item

        Item messages are prepended with "-   "
        """
        msg = click.style(msg, fg='green', bold=True, **kwargs)
        pre = click.style('-   ' + ' ' * self.message_indent, fg='green')

        click.echo(pre + msg, file=self.file, err=self.err)

    def info(self, msg, fg='black', **kwargs):
        """ Print an info message

        Information messages a prepended with "*   "
        """
        msg = click.style(msg, fg='black', **kwargs)
        pre = click.style('*   ' + ' ' * self.message_indent,
                          fg='black', bold=True)

        click.echo(pre + msg, file=self.file, err=self.err)

    def warning(self, msg, fg='red', **kwargs):
        """ Print a warning message

        Warning messages are prepended with "X   "
        """
        msg = click.style(msg, fg='yellow', **kwargs)
        pre = click.style('X   ' + ' ' * self.message_indent,
                          fg='yellow', bold=True)

        click.echo(pre + msg, file=self.file, err=self.err)

    def error(self, msg, fg='red', **kwargs):
        """ Print an error message

        Error messages are prepended with "X   "
        """
        msg = click.style(msg, fg='red', **kwargs)
        pre = click.style('X   ' + ' ' * self.message_indent,
                          fg='red', bold=True)

        click.echo(pre + msg, file=self.file, err=self.err)
