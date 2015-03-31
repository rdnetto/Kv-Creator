import re


class KvElement:
    '''Root class for all elements in a .kv file'''
    pass


class KvComment(KvElement):
    '''Represents a comment/directive'''

    def __init__(self, text):
        self.text = text


class KvWidget(KvElement):
    def __init__(self, name):
        self.name = name
        self.elements = []


class KvProperty(KvElement):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class KvClassRule(KvElement):
    def __init__(self, name):
        self.name = name


class KvFile(KvElement):
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
        self.indent_level = -1
        self.parent = None
        self.parse()


    def parse(self):
        '''Parse the .kv file, and add links from the tree structure to the instantiated widgets.
        Returns: (rootRule, classRules)

        rootRule: the rule for the root widget
        classRules: a list of class rules defined at root scope
        '''

        # the scope of each line is defined by its indentation
        # comments should bypass scope rules

        last_indent = 0
        current_root = self
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

                    new_element = parse_line(current_root, indent_level, line_type, line_data)
                    current_root.elements.append(new_element)

                # the case for same scope and higher scope and handled the same, now that we've updated current_root
                if(indent_level > last_indent):
                    # deeper scope - add to last element
                    current_root = new_element
                    new_element = parse_line(current_root, indent_level, line_type, line_data)

                else:
                    # same scope - add to parent
                    new_element = parse_line(current_root, indent_level, line_type, line_data)
                    current_root.elements.append(new_element)

                last_indent = indent_level


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

