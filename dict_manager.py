from translater import Translation, translate, Translation_for_render
from bs4 import BeautifulSoup
from django.template import Template, Context
from django.conf import settings
import django

DICTIONARY_TEMPLATE = """<html>
	<head>
		<style type="text/css">
			ul > li {
				list-style-type: none;
			}

            .Word {
                padding-right: 20px;
                padding-left: 20px;
            }

            .Translations {
                padding-right: 20px;
            }

			.dropdown-content {
				background-color: #FFFFFF;
				display: none;

			}

			.Examples {
				overflow: hidden;
                                min-width: 400px;
			}

			.Examples:hover .dropdown-content {
				display: block;
			}

			.Examples:hover {
				border: 2px;
				border-color: #000;
			}

            th, td {
                border-bottom: 1px solid #ddd;
            }

            tr:hover {background-color: #f5f5f5;}

		</style>
	</head>
    <body>
        <table>
            <thead>
  			<th>Word</th><th>Translations</th><th>Examples</th>
    		</thead>  		
    		<tbody class="Main-table">
                {% for translation in translations %}
        			<tr>
        				<td class="Word">{{ translation.word }}</td><td class="Translations">{{ translation.translations }}</td>
        				<td class="Examples">
        					<span class="dropdown-trigger">{{ translation.trigger|safe }}</span>
        					<div class="dropdown-content">
                                {% for example in translation.examples %}
        						    <hr><span>{{ example|safe }}</span><br>
                                {% endfor %}
        					</div>
        				</td>
        			</tr>
                {% endfor %}
    		</tbody>
    	</table>
    </body>
</html>
"""

class DictManager:
    TEMPLATE_FILE = "dict_template.html"
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['.'],
            'APP_DIRS': False,
        },
    ]

    def __init__(self):
        # Use django templates without apps
        settings.configure(TEMPLATES=self.TEMPLATES)
        django.setup()

    def parse_dict(self):
        """
            Parses existing html dictionary in order to save data into updated one.
        """
        # Read contents of dictionary file (Language specific)
        with open(f"{self.lang}_dictionary.html", "rb") as file:
            dictfile = file.read()
        soup = BeautifulSoup(dictfile, "lxml")
        # Extract words
        words = list(map(lambda x: x.text, soup.find_all(class_="Word")))
        # Extract translations
        translations = list(map(lambda x: x.text, soup.find_all(class_="Translations")))
        # Get examples block
        examples_soup = soup.find_all(class_="Examples")
        all_examples = []
        for batch in examples_soup:
            examples_batch = []
            for example in batch.find_all("span"):
                # Delete flanking tags, but save inner ones
                str_content = "".join(map(str, example.contents))
                examples_batch.append(str_content)
            all_examples.append(examples_batch)
        return [Translation_for_render(w, t, e[0], e[1:]) for w, t, e in zip(words, translations, all_examples)]

    def render_dict(self, translations):
        """
            Render list of translations using template.
        """
        # Read template from file into string
        template = Template(DICTIONARY_TEMPLATE)
        context = Context(dict(translations=translations))
        rendered = template.render(context)
        return rendered

    def update_dict(self, translation):
        """
            Adds new translation to existing ones, but new dictionary is
            created on every call.
        """
        try:
            current = self.parse_dict()
            if translation.word in tuple(map(lambda x: x.word, current)):
                return
        # First use
        except FileNotFoundError:
            current = []
        # Add new translation
        current.insert(0, translation)
        rendered = self.render_dict(current)
        with open(f'{self.lang}_dictionary.html', 'wb') as file:
            file.write(rendered.encode("utf-8"))



if __name__ == "__main__":
    dm = DictManager()
    print(dm.update_dict())



