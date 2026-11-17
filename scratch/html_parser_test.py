from html.parser import HTMLParser
import sys

class StrictHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower not in self.void_tags and not tag_lower.startswith('!'):
            self.stack.append((tag_lower, self.getpos()))

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.void_tags:
            return
        if not self.stack:
            self.errors.append(f"Line {self.getpos()[0]}:{self.getpos()[1]}: Unexpected closing tag </{tag}> (no matching open tag)")
            return
        last_tag, last_pos = self.stack.pop()
        if last_tag != tag_lower:
            self.errors.append(f"Line {self.getpos()[0]}:{self.getpos()[1]}: Mismatched closing tag </{tag}>. Expected </{last_tag}> (opened at line {last_pos[0]}:{last_pos[1]})")

with open('templates/devices.html', 'r', encoding='utf-8') as f:
    raw = f.read()

parser = StrictHTMLParser()
# Parse raw without stripping jinja
try:
    parser.feed(raw)
except Exception as e:
    print("Parser crashed on raw HTML:", e)

print(f"Raw parse errors: {len(parser.errors)}")
for err in parser.errors[:20]:
    print(" ", err)

if parser.stack:
    print(f"Unclosed tags in raw parse ({len(parser.stack)}):")
    for t, p in parser.stack:
        print(f"  <{t}> at line {p[0]}:{p[1]}")
