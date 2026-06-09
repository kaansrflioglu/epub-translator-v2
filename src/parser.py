import re
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.blocks = []
        self.current_block = []
        self.in_ignored_tag = 0
        self.block_tags = {
            'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
            'li', 'tr', 'ul', 'ol', 'blockquote', 'section', 
            'header', 'footer', 'aside', 'nav', 'article', 'body'
        }

    def flush_block(self):
        if self.current_block:
            # Join all parts of the current block
            block_text = ''.join(self.current_block)
            self.current_block = []
            
            # Split by the __BR__ placeholder we injected
            lines = block_text.split('__BR__')
            cleaned_lines = []
            for line in lines:
                # Replace multiple spaces/newlines with a single space
                collapsed = re.sub(r'\s+', ' ', line).strip()
                if collapsed:
                    cleaned_lines.append(collapsed)
            
            if cleaned_lines:
                # Re-join lines in the block with a single newline (preserves intentional <br/> breaks)
                self.blocks.append('\n'.join(cleaned_lines))

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'head', 'title'):
            self.in_ignored_tag += 1
        elif tag in self.block_tags:
            self.flush_block()
        elif tag == 'br':
            self.current_block.append('__BR__')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'head', 'title'):
            self.in_ignored_tag = max(0, self.in_ignored_tag - 1)
        elif tag in self.block_tags:
            self.flush_block()

    def handle_data(self, d):
        if self.in_ignored_tag == 0:
            # Replace all newlines/tabs inside data with single space to avoid layout breaking sentences
            normalized_data = re.sub(r'\s+', ' ', d)
            self.current_block.append(normalized_data)

    def get_data(self):
        self.flush_block()
        # Separate blocks/paragraphs with double newlines
        return '\n\n'.join(self.blocks)

def strip_tags(html_content):
    """Parses HTML content, strips tags, and returns formatted text."""
    s = MLStripper()
    s.feed(html_content)
    return s.get_data()
