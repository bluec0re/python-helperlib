from __future__ import unicode_literals, absolute_import
import sys, re


def _nonempty(value):
    if not value:
        return ''
    else:
        return value.decode()


def _tigetstr(cap_name):
    # String capabilities can include "delays" of the form "$<2>".
    # For any modern terminal, we should be able to just ignore
    # these, so strip them out.
    import curses
    cap = _nonempty(curses.tigetstr(cap_name))
    return re.sub(r'\$<\d+>[/*]?', '', cap)


class TerminalController(object):
    """
    A class that can be used to portably generate formatted output to
    a terminal.

    `TerminalController` defines a set of instance variables whose
    values are initialized to the control sequence necessary to
    perform a given action.  These can be simply included in normal
    output to the terminal:

        >>> term = TerminalController()
        >>> print 'This is '+term.GREEN+'green'+term.NORMAL

    Alternatively, the `render()` method can used, which replaces
    '${action}' with the string required to perform 'action':

        >>> term = TerminalController()
        >>> print term.render('This is ${GREEN}green${NORMAL}')

    If the terminal doesn't support a given action, then the value of
    the corresponding instance variable will be set to ''.  As a
    result, the above code will still work on terminals that do not
    support color, except that their output will not be colored.
    Also, this means that you can test whether the terminal supports a
    given action by simply testing the truth value of the
    corresponding instance variable:

        >>> term = TerminalController()
        >>> if term.CLEAR_SCREEN:
        ...     print 'This terminal supports clearning the screen.'

    Finally, if the width and height of the terminal are known, then
    they will be stored in the `COLS` and `LINES` attributes.
    """
    # Cursor movement:
    BOL = ''             #: Move the cursor to the beginning of the line
    UP = ''              #: Move the cursor up one line
    DOWN = ''            #: Move the cursor down one line
    LEFT = ''            #: Move the cursor left one char
    RIGHT = ''           #: Move the cursor right one char

    # Deletion:
    CLEAR_SCREEN = ''    #: Clear the screen and move to home position
    CLEAR_EOL = ''       #: Clear to the end of the line.
    CLEAR_BOL = ''       #: Clear to the beginning of the line.
    CLEAR_EOS = ''       #: Clear to the end of the screen

    # Output modes:
    BOLD = ''            #: Turn on bold mode
    BLINK = ''           #: Turn on blink mode
    DIM = ''             #: Turn on half-bright mode
    REVERSE = ''         #: Turn on reverse-video mode
    NORMAL = ''          #: Turn off all modes

    # Cursor display:
    HIDE_CURSOR = ''     #: Make the cursor invisible
    SHOW_CURSOR = ''     #: Make the cursor visible

    # Terminal size:
    COLS = None          #: Width of the terminal (None for unknown)
    LINES = None         #: Height of the terminal (None for unknown)

    # Foreground colors:
    BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''

    # Background colors:
    BG_BLACK = BG_BLUE = BG_GREEN = BG_CYAN = ''
    BG_RED = BG_MAGENTA = BG_YELLOW = BG_WHITE = ''

    _STRING_CAPABILITIES = """
    BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1
    CLEAR_SCREEN=clear CLEAR_EOL=el CLEAR_BOL=el1 CLEAR_EOS=ed BOLD=bold
    BLINK=blink DIM=dim REVERSE=rev UNDERLINE=smul NORMAL=sgr0
    HIDE_CURSOR=cinvis SHOW_CURSOR=cnorm""".split()
    _COLORS = """BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE""".split()
    _ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

    def __init__(self, term_stream=sys.stdout):
        """
        Create a `TerminalController` and initialize its attributes
        with appropriate values for the current terminal.
        `term_stream` is the stream that will be used for terminal
        output; if this stream is not a tty, then the terminal is
        assumed to be a dumb terminal (i.e., have no capabilities).
        """
        # Curses isn't available on all platforms
        try:
            import curses
        except ImportError:
            return

        # If the stream isn't a tty, then assume it has no capabilities.
        if not term_stream.isatty():
            return

        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try:
            curses.setupterm()
        except:
            return

        # Look up numeric capabilities.
        self.COLS = curses.tigetnum('cols')
        self.LINES = curses.tigetnum('lines')

        # Look up string capabilities.
        for capability in self._STRING_CAPABILITIES:
            (attrib, cap_name) = capability.split('=')
            setattr(self, attrib, _tigetstr(cap_name))

        # Colors
        set_fg = _tigetstr('setf')
        if set_fg:
            for i, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, color, _nonempty(curses.tparm(
                    set_fg.encode(), i)))
        set_fg_ansi = _tigetstr('setaf')
        if set_fg_ansi:
            for i, color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                setattr(self, color, _nonempty(curses.tparm(
                    set_fg_ansi.encode(), i)))
        set_bg = _tigetstr('setb')
        if set_bg:
            for i, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, 'BG_'+color, _nonempty(curses.tparm(
                    set_bg.encode(), i)))
        set_bg_ansi = _tigetstr('setab')
        if set_bg_ansi:
            for i, color in zip(range(len(self._ANSICOLORS)),
                               self._ANSICOLORS):
                setattr(self, 'BG_'+color, _nonempty(curses.tparm(
                    set_bg_ansi.encode(), i)))

    def render(self, template):
        """
        Replace each $-substitutions in the given template string with
        the corresponding terminal control string (if it's defined) or
        '' (if it's not).
        """
        return re.sub(r'\$\$|\${\w+}', self._render_sub, template)

    def _render_sub(self, match):
        group = match.group()
        if group == '$$':
            return group
        else:
            return getattr(self, group[2:-1])

    def remove_ctrl_chars(self, string):
        for color in self._COLORS:
            string = string.replace(getattr(self, color), '')
            string = string.replace(getattr(self, 'BG_'+color), '')
        for capability in self._STRING_CAPABILITIES:
            attrib = capability.split('=')[0]
            if hasattr(self, attrib):
                string = string.replace(getattr(self, attrib), '')
        return string

#######################################################################
# Example use case: progress bar
#######################################################################

class ProgressBar(object):
    """
    A 3-line progress bar, which looks like::

                                Header
        20% [===========----------------------------------]
                           progress message

    The progress bar is colored, if the terminal supports color
    output; and adjusts to the width of the terminal.
    """
    BAR = '%3d%% ${GREEN}[${BOLD}%s%s${NORMAL}${GREEN}]${NORMAL}\n'
    HEADER = '${BOLD}${CYAN}%s${NORMAL}\n\n'

    def __init__(self, term, header):
        self.term = term
        self.__quirks = False
        if not (self.term.CLEAR_EOL and self.term.UP and self.term.BOL):
           # raise ValueError("Terminal isn't capable enough -- you "
           #                  "should use a simpler progress dispaly.")
            sys.stdout.write(
                self.term.render("${RED}Terminal isn't capable enough -- you "
                                 "should use a simpler progress display."
                                 "${NORMAL}"))
            self.__quirks = True
        self.width = self.term.COLS or 75
        self.bar = term.render(self.BAR)
        self.header = self.term.render(self.HEADER % header.center(self.width))
        self.cleared = 1 #: true if we haven't drawn the bar yet.
        self.update(0, '')

    def update(self, percent, message):
        if self.cleared:
            sys.stdout.write(self.header)
            self.cleared = 0
        if self.__quirks:
            sys.stdout.write("%.2f%%..." % (percent*100.0))
        else:
            n = int((self.width-10)*percent)
            sys.stdout.write(
                self.term.BOL + self.term.UP + self.term.CLEAR_EOL +
                (self.bar % (100*percent, '='*n, '-'*(self.width-10-n))) +
                self.term.CLEAR_EOL + message.center(self.width))

    def clear(self):
        if not self.cleared:
            sys.stdout.write(self.term.BOL + self.term.CLEAR_EOL +
                             self.term.UP + self.term.CLEAR_EOL +
                             self.term.UP + self.term.CLEAR_EOL)
            self.cleared = 1

class Table(object):
    """
    Prints a Table

    Arguments:
        term       - TerminalController instance
        rows       - 2-dimensional array with table data
        col_format - format specs of cols ("c" == center, "r" == right,
                     "l" == left)
        seperator  - seperator between cols (default " ")
        borders    - print borders around table and between rows
                     (default False)
    """

    def __init__(self, term, rows, col_format, seperator=" ", borders=False):
        self.term = term
        if sys.version_info >= (3, 0, 0):
            self.rows = [[ str(c) for c in r] for r in rows]
        else:
            self.rows = [[ unicode(c) for c in r] for r in rows]
        self.col_format = col_format
        self.seperator = seperator
        self.borders = borders
        self.col_width = [ max([ len(
                                    self.term.remove_ctrl_chars(d[i])
                                 ) if i < len(d) else 0
                                for d in self.rows ]) for i in
                                    range(0, len(self.col_format))]
        self.max_width = self.term.COLS or 75
        self.width = sum(self.col_width) + len(self.seperator) * (
                len(self.col_format) - 1) + (4 if self.borders else 0)

    def render(self, stream=sys.stdout):
        cur_width = self.width if self.width < self.max_width \
                               else self.max_width
        if self.borders:
            stream.write("-"*cur_width + "\n")

        for row in self.rows:
            if self.borders:
                stream.write("| ")
            for i, col in zip(range(0, len(row)), row):
                if self.col_format[i] == "c":
                    stream.write(col.center(self.col_width[i]))
                elif self.col_format[i] == "l":
                    stream.write(col.ljust(self.col_width[i]))
                elif self.col_format[i] == "r":
                    stream.write(col.rjust(self.col_width[i]))

                if i < len(row) - 1:
                    stream.write(self.seperator)

            for i in range(len(row), len(self.col_format)):
                stream.write(' ' * (self.col_width[i]))
                if i < len(row) - 1:
                    stream.write(self.seperator)

            if self.borders:
                stream.write(" |\n")
                stream.write("-"*cur_width)

            stream.write("\n")

        if self.borders and len(self.rows) == 0:
            stream.write("-"*cur_width + "\n")
