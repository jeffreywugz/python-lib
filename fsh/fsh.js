function isHtml(s) s && (s.match(/<.*?>/g) || []).length > 10
function preHtml(s) isHtml(s)? s: '<pre>' + s + '</pre>'
function dump2html(ret, err, _ret, _err) [_ret.innerHTML, _err.innerHTML] = [preHtml(str(ret)), exceptionFormat(err)]
function dumpCall(func, arg, _ret, _err){ var [ret, err] = safeCall(func, arg);  return dump2html(ret, err, _ret, _err);}
function mkDumper(func, _ret, _err) function(arg) dumpCall(func, arg, _ret, _err)

// lish means `line shell'
function safeCall(func, arg) {
    var result, exception;
    try{
        result = func(arg);
    }catch(e){
        exception = e;
    }
    return [result, exception]
}

function _lish(interp, input) {
    bindHotKey(top, 'ctrl-alt-i', function(e) input.focus());
    bindHotKey(input, 'enter', function(e) interp(e.target.value));
    input.focus();
    return function(expr) interp(input.value=expr.trim());
}

function lish(interp, panel) {
    panel.innerHTML = '<input type="text" class="input"/><pre class="error"></pre><div class="output"></div>';
    return _lish(mkDumper(interp, $s(panel,'output'), $s(panel, 'error')) , $s(panel, 'input'));
}

// fish means `file shell'
function getCurLine(content, caret){
    [s, e] = [content.lastIndexOf("\n", caret-1), content.indexOf("\n", caret)];
    return content.substring(s+1, e!=-1? e: content.length);
}
function filterLines(content, tag) [i.substring(tag.length) for each(i in content.match(RegExp(tag+'.*$', 'gm')))]
function filterLine(content, tag) filterLines(content, tag)[0]

function fishHandle(interp, input){
    line = getCurLine(input.value, textAreaGetCaret(input));
    return interp(line, input.value, textAreaGetCaret(input));
}

function _fish(interp, input) {
    bindHotKey(top, 'ctrl-alt-h', function(e) toggleVisible(input));
    bindHotKey(input, 'ctrl-alt-e', function(e) fishHandle(interp, e.target));
    bindHotKey(input, 'ctrl-button0', function(e) fishHandle(interp, e.target));
    return function(expr, full) interp(expr, full != undefined? input.value=full: input.value);
}

function fish(interp, panel, filter, id) {
    panel.innerHTML = '<textarea name="content" class="input" rows="12">${content}</textarea><pre class="status"></pre><div class="lish"></div>';
    var sched = new Scheduler();
    sched.onExecute = function(tasks) $s(panel, 'status').innerHTML = id + ': ' + repr(tasks.map(taskFormat));
    filter = filter || function(line, content) [line];
    sh = lish(interp, $s(panel, 'lish'));
    bindHotKey($s(panel, 'status'), 'button0', function(e) toggleVisible($s(panel, 'input')));
    bindHotKey($s(panel, 'input'), 'ctrl-wheel', function(e){ e.target.rows += 4*e.detail; e.preventDefault();});
    function doTask(line, content, caret) sched.execute(mkTasks(filter(line, content, caret), sh));
    return _fish(doTask, $s(panel, 'input'));
}

// use seq.map to makesure seq is an array instead of a string.
function mkTasks(seq, func) seq.map(function(i) typeof(i)=='number'? [null, null, i]: [func, i, 0])
function taskFormat(t) {var [func,arg,delay] = t; return func? arg: '#'+delay;}
function Scheduler(){}
Scheduler.prototype.cancel = function() clearTimeout(this.timer);
Scheduler.prototype.execute = function(tasks){
    this.onExecute && this.onExecute(tasks);
    this.cancel();
    if(!tasks || !tasks.length)return;
    var [func, arg, delay] = tasks[0];
    if(func && !func(arg))return;
    self = this;
    this.timer = setTimeout(function() self.execute(tasks.slice(1)), delay);
}

function splitByFirstLine(str) let(i = str.indexOf('\n')+1) [str.substring(0, i), str.substr(i)]
function rpcDecode(str){
    let [head, content] = splitByFirstLine(str);
    if(head == 'Exception:\n') throw content;
    else return content;
}
function get() rpcDecode(http('get'))
function set(content) rpcDecode(http('set', content))
function popen(cmd) rpcDecode(http('popen', cmd))
