function getBlock(str, caret, sTag, eTag){
    var s = str.lastIndexOf(sTag, caret-1);
    var e = str.indexOf(eTag, caret);
    return str.substring(s==-1? 0: s+sTag.length, e==-1? str.length: e);
}
function filterLines(content, tag) { return map(function(i){ return i.substring(tag.length);}, content.match(RegExp(tag+'.*$', 'gm'))); }
function getCurLine(content, caret) { return getBlock(content, caret, '\n', '\n'); }

function splitByFirstLine(str) { var i = str.indexOf('\n')+1; return [str.substring(0, i), str.substr(i)]; }
function rpcDecode(str){
    var two_parts = splitByFirstLine(str);
    var head = two_parts[0];
    var content = two_parts[1];
    if(head == 'Exception:\n') throw content;
    else return content;
}

var rpc_path;
var query_path = getQueryArgs()['path'] || '';
function rpc_init(){ rpc_path = getUrl().search(/fsh\.html$/) == -1? function(x){return x;}: function(x){return 'psh.cgi?' + encodeQueryString({path:query_path, method:x}) + '&';} }
function get(){return rpcDecode(http(rpc_path('get'))); }
function set(content){ return rpcDecode(http(rpc_path('set'), content)); }
function popen(cmd) {return rpcDecode(http(rpc_path('popen'), cmd)); }

function isHtml(s) {return s && (s.match(/<.*?>/g) || []).length > 10; }
function preHtml(s) {return isHtml(s)? s: '<pre onClick="selectNode(this.firstChild)">' + s + '</pre>'; }
function dump2html(ret, err, _ret, _err) { _ret.innerHTML = preHtml(str(ret)); _err.innerHTML = exceptionFormat(err); return [ret, err]; }
function dumpCall(func, arg, _ret, _err){ var res = safeCall(func, arg);  return dump2html(res[0], res[1], _ret, _err);}
function mkDumper(func, _ret, _err) {return function(arg) {return dumpCall(func, arg, _ret, _err); }; }

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
    bindHotKey(top, 'ctrl-alt-i', function(e){ return input.focus(); });
    bindHotKey(input, 'enter', function(e){return interp(e.target.value); });
    input.focus();
    return function(expr){return interp(input.value=expr.trim()); };
}

function lish(interp, panel) {
    panel.innerHTML = '<input type="text" class="input"/><pre class="error"></pre><div class="output"></div>';
    return _lish(mkDumper(interp, $s(panel,'output'), $s(panel, 'error')) , $s(panel, 'input'));
}

// fish means `file shell'
function _fish(interp, input) {
    function fishHandle(interp, input){
        var content = input.value;
        var caret = textAreaGetCaret(input);
        return interp(getCurLine(content, caret), content, caret);
    }
    bindHotKey(top, 'ctrl-alt-h', function(e){ return toggleVisible(input);});
    bindHotKey(input, 'ctrl-alt-e', function(e) {return fishHandle(interp, e.target);});
    bindHotKey(input, 'ctrl-button0', function(e){return fishHandle(interp, e.target);});
    return function(expr, full){return interp(expr, full != undefined? input.value=full: input.value);};
}

function fish(interp, panel, text_filter, status) {
    panel.innerHTML = '<textarea name="content" class="input" rows="12">${content}</textarea><pre class="error"></pre><div class="status"></div><div class="lish"></div>';
    var sched = new Scheduler();
    function _status(id, tasks, i){return '<pre class="status">' + id + ': ' + tasks.slice(i).map(taskFormat).join(';') + '</pre>';};
    sched.onExecute = function(tasks, i){return $s(panel, 'status').innerHTML = (typeof(status) == 'function'? status(tasks,i): _status(status, tasks, i));}
    text_filter = text_filter || function(line, content){ return [line];};
    var sh = lish(interp, $s(panel, 'lish'));
    bindHotKey($s(panel, 'status'), 'button0', function(e){return toggleVisible($s(panel, 'input'));});
    bindHotKey($s(panel, 'input'), 'alt-wheel', function(e){ e.target.rows += getWheelDelta(e)/40; e.preventDefault();});
    function doTask(expr, content, caret){
        function reset_error(){ $s(panel, 'error').innerHTML = ''; };
        function error(msg){return $s(panel, 'error').innerHTML += msg;}
        var tasks = [];
        reset_error();
        try{
            var cmds = text_filter(expr, content, caret);
            tasks =mkTasks(cmds, sh);
            if (getQueryArgs()['debug'] == 'true'){
                error('text_filter({expr={expr}, caret={caret})\n'.format({'expr':expr, 'caret':caret}));
                error(tasks.map(taskFormat).join('\n') + '\n');
            }
        } catch(e) {
            error(exceptionFormat(e));
            return;
        }
        error('');
        if (getQueryArgs()['dryrun'] == 'true') {
                if(getQueryArgs()['debug'] != 'true') error(tasks.map(taskFormat).join('\n') + '\n');
        } else {
            sched.execute(tasks, 0);
        }
    }
    gsh = sh;
    return _fish(doTask, $s(panel, 'input'));
}

function generateTasks(_args, cmd, seq, _env){
    var args = str2dict(_args, cmd);
    if(!args)return [];
    var env = dict_merge(_env, args);
    var cmd_seq = map(function(t){ return typeof(t) == 'number'? t: sub(t, env);}, seq);
    log('generateTasks:', {'_args': _args, 'args': args, 'cmd':cmd, 'seq':seq, 'env': env, 'cmd_seq':cmd_seq});
    return cmd_seq;
}

function FshTasksGenerator(seq, args){
    bind(this, {seq:seq, args:'.*'});
}
FshTasksGenerator.prototype.gen = function(cmd) { return generateTasks(this.args, cmd, this.seq, this); }
