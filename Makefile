.PHONY: all test clean
all: test-me
test-me:
	me echo x=1 y=2 z
	me identity :'[1,2,3]'
	me 'range(100)' / map :'lambda x:x*x' :_ / pformat
	me glob '*.py' / lop map shell_tpl 'echo mv $$name.py $$name.perl' '$$name\.$$ext'
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