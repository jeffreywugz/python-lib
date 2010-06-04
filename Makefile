.PHONY: all test clean
all: test-vgen
test-meval:
	me echo x=1 y=2 z
test-vgen:
	me test_vgen >vgen.html && firefox vgen.html
clean:
	rm -rf *.pyc */*.pyc