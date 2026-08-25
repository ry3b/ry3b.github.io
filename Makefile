# One data file (data/cv.json) -> cv.pdf, resume.pdf, and the generated
# regions of the papers / projects / coursework pages.

.PHONY: edit build check clean

edit:            ## browser editor at http://127.0.0.1:8000/_editor
	python3 tools/serve.py

build:           ## rebuild both PDFs and the generated page regions
	python3 tools/build.py

check:           ## list gaps in the data without building
	python3 tools/build.py --check

clean:
	rm -rf .build
