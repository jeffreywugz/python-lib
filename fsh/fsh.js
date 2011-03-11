function getBlock(str, caret, sTag, eTag){
    let [s, e] = [str.lastIndexOf(sTag, caret-1), str.indexOf(eTag, caret)];
    return str.substring(s==-1? 0: s+sTag.length, e==-1? str.length: e);
}
function filterLines(content, tag) [i.substring(tag.length) for each(i in content.match(RegExp(tag+'.*$', 'gm')))]
function getCurLine(content, caret) getBlock(content, caret, '\n', '\n')

function splitByFirstLine(str) let(i = str.indexOf('\n')+1) [str.substring(0, i), str.substr(i)]
function rpcDecode(str){
    let [head, content] = splitByFirstLine(str);
    if(head == 'Exception:\n') throw content;
    else return content;
}

function get() rpcDecode(http('get'))
function set(content) rpcDecode(http('set', content))
function popen(cmd) rpcDecode(http('popen', cmd))

function isHtml(s) s && (s.match(/<.*?>/g) || []).length > 10
function preHtml(s) isHtml(s)? s: '<pre onClick="selectNode(this.firstChild)">' + s + '</pre>'
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
function _fish(interp, input) {
    function fishHandle(interp, input){
        let [content, caret] = [input.value, textAreaGetCaret(input)];
        return interp(getCurLine(content, caret), content, caret);
    }
    bindHotKey(top, 'ctrl-alt-h', function(e) toggleVisible(input));
    bindHotKey(input, 'ctrl-alt-e', function(e) fishHandle(interp, e.target));
    bindHotKey(input, 'ctrl-button0', function(e) fishHandle(interp, e.target));
    return function(expr, full) interp(expr, full != undefined? input.value=full: input.value);
}

function fish(interp, panel, filter, status) {
    panel.innerHTML = '<textarea name="content" class="input" rows="12">${content}</textarea><pre class="error"></pre><div class="status"></div><div class="lish"></div>';
    var sched = new Scheduler();
    function _status(id, tasks, i) '<pre class="status">' + id + ': ' + tasks.slice(i).map(taskFormat).join(';') + '</pre>';
    sched.onExecute = function(tasks, i) $s(panel, 'status').innerHTML = (typeof(status) == 'function'? status(tasks,i): _status(status, tasks, i))
    filter = filter || function(line, content) [line];
    sh = lish(interp, $s(panel, 'lish'));
    bindHotKey($s(panel, 'status'), 'button0', function(e) toggleVisible($s(panel, 'input')));
    bindHotKey($s(panel, 'input'), 'ctrl-wheel', function(e){ e.target.rows += 4*e.detail; e.preventDefault();});
    function doTask(expr, content, caret){
        function error(msg) $s(panel, 'error').innerHTML = msg;
        var tasks = [];
        try{
            tasks =mkTasks(filter(expr, content, caret), sh);
        } catch(e) {
            error(exceptionFormat(e));
            return;
        }
        error('');
        sched.execute(tasks, 0);
    }
    return _fish(doTask, $s(panel, 'input'));
}

function generateTasks(_args, cmd, seq, _env){
    let args = str2dict(_args, cmd);
    if(!args)return [];
    log(args)
    args = dict([[k,v] for each([k,v] in Iterator(args))if(v)]);
    log(args)
    let env = bind(dict(Iterator(_env)), args);
    log('gen: ', _args, cmd, seq, env);
    return [typeof(t) == 'number'? t: sub(t, env) for each(t in seq)];
}

function FshTasksGenerator(seq, args){
    bind(this, {seq:seq, args:'.*'});
}
FshTasksGenerator.prototype.gen = function(cmd) generateTasks(this.args, cmd, this.seq, this);
