.PHONY: all test clean
all: test-container
test-meval:
	me echo x=1 y=2 z
test-container:
	me test_container >tmp.html && firefox tmp.html
test-wiki:
	me test_wiki >wiki.html && firefox wiki.html
clean:
	rm -rf *.pyc */*.pyc