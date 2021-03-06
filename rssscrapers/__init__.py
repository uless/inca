import os as _os

_expected_file_end = "_scraper.py"

__all__ = [fname for fname in _os.listdir('rssscrapers') if fname[-len(_expected_file_end):]==_expected_file_end and not fname.startswith('.')]

for module in __all__:
    __import__('.'.join(['rssscrapers',module.replace('.py','')]))
