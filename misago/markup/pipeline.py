from importlib import import_module

from bs4 import BeautifulSoup
from django.conf import settings


class MarkupPipeline(object):
    """
    Small framework for extending parser
    """
    def extend_markdown(self, md):
        for extension in settings.MISAGO_MARKUP_EXTENSIONS:
            module = import_module(extension)
            if hasattr(module, 'extend_markdown'):
                hook = getattr(module, 'extend_markdown')
                hook.extend_markdown(md)
        return md

    def process_result(self, result):
        soup = BeautifulSoup(result['parsed_text'])
        for extension in settings.MISAGO_MARKUP_EXTENSIONS:
            module = import_module(extension)
            if hasattr(module, 'clean_parsed'):
                hook = getattr(module, 'clean_parsed')
                hook.process_result(result, soup)

        souped_text = unicode(soup.body).strip()[6:-7]
        result['parsed_text'] = souped_text.strip()
        return result

pipeline = MarkupPipeline()
