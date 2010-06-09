.PHONY: all test clean
all: test-wiki
test-meval:
	me echo x=1 y=2 z
test-container:
	me test_container >tmp.html && firefox tmp.html
test-wiki:
	me test_wiki >tmp.html && firefox tmp.html
clean:
	rm -rf *.pyc */*.pyc