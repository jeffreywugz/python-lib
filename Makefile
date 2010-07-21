.PHONY: all test clean
all: test-control
test-me:
	me echo x=1 y=2 z
	me --init='a=[1,2,3]' a
	me identity :'[1,2,3]'
	me 'range(10)' / map :'lambda x:x*x' :_ / pformat
	me glob '*.py' / lop map sub_shell  '$$name\.$$ext' 'echo mv $$name.py $$name.perl'
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