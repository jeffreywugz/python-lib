.PHONY: all test clean
all: test-msh
test-me:
	me echo x=1 y=2 z
test-control:
	me test_control >tmp.html && firefox tmp.html
test-container:
	me test_container >tmp.html && firefox tmp.html
test-msh:
	me test_msh >tmp.html && firefox tmp.html
test-wiki:
	me test_wiki >tmp.html && firefox tmp.html
clean:
	rm -rf *.pyc */*.pyc