PY=python

.PHONY: setup spider scorpion

setup:
	$(PY) -m pip install -r requirements.txt

spider:
	$(PY) src/spider.py -r -l 2 -p ./data/ https://example.com

scorpion:
	$(PY) src/scorpion.py ./data/image.jpg
