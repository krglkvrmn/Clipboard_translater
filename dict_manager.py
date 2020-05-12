HTML_INIT_TEMPLATE = """
<table>
    <tr>
        <th>Word</th><th>Transcription</th><th>Translation</th>
    </tr>
    {}
</table>
"""

HTML_INSERTION_TEMPLATE = """
<tr>
    <td>{}</td><td>{}</td><td>{}</td>
</tr>
"""

def update_dictionary(path, tt):
    filename = re.search(r'/?(\w+\..{3,4})', path).group(1)
    directory = re.search(r'.*/', path)
    if directory:
        directory = directory.group(0)
    else:
        directory = '.'
    HTML = True if filename.endswith('.html') else False

    if filename not in os.listdir(directory):
        if HTML:
            with open(path, 'w') as file:
                file.write(HTML_INIT_TEMPLATE.format(''))
        else:
            with open(path, 'w') as file:
                pass

    to_write_str_html = HTML_INSERTION_TEMPLATE.format(tt.word.lower(), tt.transcription, tt.translation)
    to_write_str_txt = '{} {} - {}\n'.format(tt.word.lower(), tt.transcription, tt.translation)
    to_write_str = to_write_str_html if HTML else to_write_str_txt

    with open(path, 'rb') as file:
        if to_write_str.encode('utf-8') in file.read():
            return

    if HTML:
        with open(path, 'rb') as file:
            contents = file.read()[90:]
        with open(path, 'wb') as file:
            file.write(HTML_INIT_TEMPLATE.format(to_write_str + contents).encode('utf-8'))
    else:
        with open(path, 'ab') as file:
            file.write(to_write_str.encode('utf-8'))
        with open(path, 'a') as file:
            file.write('\n')
