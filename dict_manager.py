import os
import re
from trabslater import Translation


HTML_INIT_TEMPLATE = b"""
<table>
    <tr>
        <th>Word</th><th>Transcription</th><th>Translation</th>
    </tr>
    %b
</table>
"""

HTML_INSERTION_TEMPLATE = b"""
<tr>
    <td>%b</td><td>%b</td><td>%b</td>
</tr>
"""

def update_dictionary(path: str, tt: Translation):
    """
    Update dictionary with translation results.

    Input:
            1. Path to file to write changes into.
            2. Translation object containing translation,
            transcription and word itself.
    """
    # Parse file name and directory from path.
    filename = re.search(r'/?(\w+\..{3,4})', path).group(1)
    directory = re.search(r'.*/', path)
    if directory:
        directory = directory.group(0)
    else:
        directory = '.'
    HTML = True if filename.endswith('.html') else False

    if filename not in os.listdir(directory):
        if HTML:
            with open(path, 'wb') as file:
                file.write(HTML_INIT_TEMPLATE % b'')
        else:
            with open(path, 'w') as file:
                pass
    # Insert results into template
    to_write_str_html = HTML_INSERTION_TEMPLATE % (tt.word.lower().encode('utf-8'), tt.transcription.encode('utf-8'), tt.translation.encode('utf-8'))
    to_write_str_txt = b'%b %b - %b\n' % (tt.word.lower().encode('utf-8'), tt.transcription.encode('utf-8'), tt.translation.encode('utf-8'))
    to_write_str = to_write_str_html if HTML else to_write_str_txt

    with open(path, 'rb') as file:
        if to_write_str in file.read():
            return

    if HTML:
        with open(path, 'rb') as file:
            contents = file.read()[91:-9]
        with open(path, 'wb') as file:
            file.write(HTML_INIT_TEMPLATE % (to_write_str + contents))
    else:
        with open(path, 'ab') as file:
            file.write(to_write_str.encode('utf-8'))

