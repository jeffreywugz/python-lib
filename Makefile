.PHONY: all test clean
all: test
test:
	./vgen.py >vgen.html && firefox vgen.html
clean:
	rm *.pyc