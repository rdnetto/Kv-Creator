import re


class KvElement:
    '''Root class for all elements in a .kv file'''
    pass


class KvComment(KvElement):
    '''Represents a comment/directive'''

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "KvComment: " + repr(self.text)


class KvWidget(KvElement):
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.widget = None

    def populate(self, widget):
        '''Merges a widget tree into the KvElement tree.'''

        # Merge root
        assert self.name == type(widget).__name__.split(".")[-1]
        self.widget = widget

        # There should be at least as many children in the widget as there are in the kv file
        # Note that there can be more, if the widget automatically adds children
        widgets = filter(is_widget, self.elements)
        assert len(widgets) <= len(widget.children), "self.elements = {}\nwidget.children = {}".format(self.elements, widget.children)

        # the elements and widget tree are in opposite orders
        for e, c in zip(widgets, reversed(widget.children)):
            e.populate(c)

    def __repr__(self):
        return "KvWidget: {} {{{} elements, widget = {}}}".format(self.name, len(self.elements), self.widget)

    def __str__(self):
        '''Creates a textual representation of the KvElement tree.'''

        res = repr(self) + "\n"

        for e in self.elements:
            res += indent(str(e)) + "\n"

        return res


class KvProperty(KvElement):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "KvProperty: {{name = {}, value = {}}}".format(self.name, self.value)


class KvClassRule(KvElement):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "KvClassRule: " + self.name


class KvFile:
    '''Represents the structure of a KvFile'''

    # each line must match one of the following formats:
    # comments ('#...')
    commentRE = re.compile(r"^#(.*)$")

    # widget rules - 'Foo:'
    widgetRE = re.compile(r"^(\w+):\s*$")

    # class rules - '<Widget>:'
    classRE = re.compile(r"^\<(\w+)\>:\s*$")

    # properties - 'prop: expression'
    propRE = re.compile(r"^(\w+):\s*(.+)$")

    rule_formats = [("comment", commentRE), ("widget", widgetRE), ("class", classRE), ("property", propRE)]

    def __init__(self, path):
        self.path = path
        self.rootRule = None
        self.elements = []
        self.parse()


    def parse(self):
        '''Parse the .kv file, and add links from the tree structure to the instantiated widgets.
        Returns: (rootRule, classRules)

        rootRule: the rule for the root widget
        classRules: a list of class rules defined at root scope
        '''

        # define a fake root element to collect the parse output
        root = KvElement()
        root.elements = []
        root.indent_level = -1
        root.parent = None
        root.__repr__ = lambda: "<root>"

        # the scope of each line is defined by its indentation
        # comments should bypass scope rules
        last_indent = 0
        current_root = root
        new_element = None

        with open(self.path, "r") as f:
            # Parse the .kv file, line-by-line
            # Need to infer structure from indentation

            for (line_no, line) in enumerate(f, 1):
                line_content = line.lstrip()

                if(len(line_content) == 0):
                    continue

                indent_level = indent_count(line[: len(line) - len(line_content)], line)
                line_type = None

                # identify the line format
                for (name, regex) in KvFile.rule_formats:
                    line_data = regex.match(line_content)

                    if(line_data is not None):
                        line_type = name
                        break

                if(line_type is None):
                    raise Exception("Parsing error on line {}:\n{}".format(line_no, line))

                # identify the scope, and insert the data accordingly
                if(indent_level < last_indent):
                    # higher scope - need to go up until we find our parent
                    while(current_root.indent_level >= indent_level):
                        assert current_root.parent is not None
                        current_root = current_root.parent

                elif(indent_level > last_indent):
                    # deeper scope - add to last element
                    current_root = new_element

                # add new element
                new_element = parse_line(current_root, indent_level, line_type, line_data)
                current_root.elements.append(new_element)

                last_indent = indent_level

        widgets = list(filter(is_widget, root.elements))
        assert len(widgets) <= 1
        self.elements = root.elements
        self.rootRule = widgets[0] if len(widgets) > 0 else None


def indent_count(s, line):
    '''Returns an integer representing the no. of spaces by which the line has been indented.'''

    res = 0

    for c in s.expandtabs():
        if(c == ' '):
            res += 1
        else:
            raise Exception("Invalid char {} in indentation {} of line {}".format(repr(c), repr(s), repr(line)))

    return res


def parse_line(parent, indent_level, line_type, data):
    '''Parses an element are returns it

    parent: the parent element. Will be KvFile for the root element
    indent_level: an integer corresponding to the depth in the parse tree
    line_type: one of "comment", "widget", "class", "property"
    data: capture groups from the regex, as returned by re.match()
    '''

    if(line_type == "comment"):
        res = KvComment(data.group(1))
    elif(line_type == "widget"):
        res = KvWidget(data.group(1))
    elif(line_type == "class"):
        res = KvClassRule(data.group(1))
    elif(line_type == "property"):
        res = KvProperty(data.group(1), data.group(2))
    else:
        raise Exception("Unknown line_type: " + str(line_type))

    res.indent_level = indent_level
    res.parent = parent
    return res


def is_widget(e):
    '''Helper method which returns True if e is a KvWidget'''

    return isinstance(e, KvWidget)


def indent(s, prefix="    "):
    return prefix + ("\n" + prefix).join(s.splitlines())

