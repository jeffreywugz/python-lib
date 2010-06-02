.PHONY: all test clean
all: test-meval
test-vgen:
	./vgen.py >vgen.html && firefox vgen.html
test-meval:
	me echo x=1 y=2 z
clean:
	rm *.pyc */*.pyc