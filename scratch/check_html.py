from html.parser import HTMLParser
import re

content = open('templates/devices.html', encoding='utf-8').read()

# Strip jinja tags for pure HTML tag balancing check
stripped_html = re.sub(r'\{%.*?%\}', '', content, flags=re.DOTALL)
stripped_html = re.sub(r'\{\{.*?\}\}', 'placeholder', stripped_html, flags=re.DOTALL)
stripped_html = re.sub(r'\{#.*?#\}', '', stripped_html, flags=re.DOTALL)

# Self closing tags
void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr', 'path', 'circle', 'line', 'polyline', 'rect', 'use', 'polygon'}

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.ids = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if 'id' in attrs_dict:
            id_val = attrs_dict['id']
            if id_val in self.ids:
                self.errors.append(f"Duplicate ID: '{id_val}' at line {self.getpos()[0]} (previously at line {self.ids[id_val]})")
            else:
                self.ids[id_val] = self.getpos()[0]

        if tag not in void_tags:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in void_tags:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]}")
            return
        last_tag, line = self.stack[-1]
        if last_tag == tag:
            self.stack.pop()
        else:
            # Check if tag is in stack
            tag_names = [t[0] for t in self.stack]
            if tag in tag_names:
                # Some tag wasn't closed
                unclosed = []
                while self.stack and self.stack[-1][0] != tag:
                    unclosed.append(self.stack.pop())
                self.stack.pop() # pop matching
                for u_tag, u_line in unclosed:
                    self.errors.append(f"Unclosed tag <{u_tag}> from line {u_line} before closing </{tag}> at line {self.getpos()[0]}")
            else:
                self.errors.append(f"Mismatched closing tag </{tag}> at line {self.getpos()[0]} (expected </{last_tag}> from line {line})")

checker = TagChecker()
checker.feed(stripped_html)

for tag, line in checker.stack:
    checker.errors.append(f"Unclosed tag <{tag}> from line {line} at EOF")

print(f"Total HTML structure errors: {len(checker.errors)}")
for e in checker.errors:
    print(" - ", e)
