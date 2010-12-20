// algorithmic
function dict(pairs){ var result = {}; for each([k,v] in pairs) result[k] = v;  return result;}
function dictMap(f, d){ return dict([k, f(v)] for each([k,v] in Iterator(d))); }
function range(start, stop, step){
    if(start == undefined)return;
    if(stop == undefined){ start = 0; stop = start; }
    if(step == undefined)step = 1;
    for(var i = start; i < stop; i += step)yield i;
}
function repeat(n, x){ for (var i=0; i<n; i++)yield x; }
function repeat2arr(n, x) genArr(repeat(n, x))
function arrScale(arr,n) Array.concat.apply([], repeat2arr(n, arr))
function arrCat() Array.concat.apply([], arguments)
function genArr(g) [i for each(i in g)]
function rand(n) Math.floor(Math.random()*(n+1))
function randChoice(seq) seq[rand(seq.length)]

// string related
function repr(obj) {return JSON.stringify(obj);}
function str(obj){ return typeof obj == 'string'? obj: repr(obj);}
String.prototype.format = function()let(dict=arguments[0]) this.replace(/{(\w+)}/g, function(m,k) dict[k])
String.prototype.seqSub = function(pat, seq) [typeof(i)=="string"? this.replace(pat, i): i for each(i in seq)];
function basename(path) path.replace(/.*\//, '')
function dirname(path) path.replace(/\/[^\/]*$/, '')

//global environment
function getQueryArgs(){ return parseQueryString(location.search.substring(1));}
function parseQueryString(query){ return dict(p.match(/([^=]+)=(.*)/).slice(1) for each(p in query.split('&')) if(p));}
function encodeQueryString(args){ return [k + "=" + encodeURIComponent(args[k].toString()) for(k in args)].join('&');}
function obj2QueryString(obj){return encodeQueryString(dictMap(function(v)JSON.stringify(v), obj));}
function errorFormat(msg, url, lineno){ return repr([msg, url, lineno]);}
function exceptionFormat(e){ return e? e.toString() + '\n' + str(e.stack): "";}
function onerror(msg, url, lineno) { alert(errorFormat(msg, url, lineno)); return true;}
// window.onerror = onerror;

// DOM element operation
function $(id){ return document.getElementById(id);}
function $F(id){ return $(id).value;}
function $c(w, c){ return [x for each(x in w.childNodes) if(x.className == c)];}
function $s(w, c){ return $c(w, c)[0];}
function insertAfter(parent, node, referenceNode){ parent.insertBefore(node, referenceNode.nextSibling);}
function hide(w){ w.style.display = 'none';}
function show(w){ w.style.display = 'block';}
function isVisible(w){ return w.style.display != 'none'; }
function toggleVisible(w){ isVisible(w)?hide(w):show(w);}
function setHeight(w){ w.style.height = w.scrollHeight + "px"; }
function scrollTo(w, top){ w.scrollTop = top; }
function textAreaGetCaret(textArea){ return textArea.selectionStart; }
function textAreaSetCaret(textArea, caret){ textArea.setSelectionRange(caret, caret);}

// hot key/click related
function parseHotKey(key){
    var funcKeys = {backspace:8, tab:9, enter:13, pause:19, escape:27, space:32,
                   pageup:33, pagedown:34, end:35, home:36, left:37, up:38, right:39, down:40,
                   print:44, insert:45, del:46,
                   f1:112, f2:113, f3:114, f4:115, f5:116, f6:117, f7:118, f8:119, f9:120, f10:121, f11:122, f12:123,
                   numlock:144, scrolllock:145,};
    function km(pat){ var m = key.toLowerCase().match(pat); return m? m[0]: null;}
    return {ctrl:km('ctrl'), alt:km('alt'), shift:km('shift'), button: km(/button[0-9]$/), wheel: km(/wheel$/),
            key: km(/\W[a-zA-Z]$/), func: funcKeys[km(/\w+$/)]};
}

function isHotKey(e, key){
    var k = parseHotKey(key);
    return (!k.ctrl || e.ctrlKey) && (!k.alt || e.altKey) && (!k.shift || e.shiftKey)
        && (!k.key || k.key.toUpperCase() == String.fromCharCode(e.charCode).toUpperCase())
        && (!k.func || k.func == e.which)
        && (!k.button || parseInt(k.button.substr(-1)) == e.button)
        && (k.key || k.func || k.button || k.wheel);
}

function hotKeyType(key) key.match('wheel$')? 'DOMMouseScroll': key.match('button[0-9]$')? 'click': 'keypress'

function bindHotKey(w, key, handler) w.addEventListener(hotKeyType(key), function(e) isHotKey(e, key) && handler(e), false)
function bindHotKeys(w, bindings)[bindHotKey(w, name, bindings[name]) for(name in bindings)]

// rpc stuff
function _httpSend(http, content){
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.setRequestHeader("Connection", "close");
    http.send(content);
}

function httpRawAsyncCall(url, args, handler, faultHandler){
    var http = new XMLHttpRequest();
    if(!faultHandler) faultHandler = function(http){throw http.responseText;};
    http.onreadystatechange = function() ajaxReq.readyState==4 || (http.status==200? handler(http): faultHandler(http));
    http.open("POST", url, false);
    _httpSend(http, args)
}

function httpAsyncCall(url, args, handler, faultHandler){
    httpAsyncRawCall(url, obj2QueryString(args),
                     function(http) handler(JSON.parse(http.responseText)), faultHandler);
}

function httpRawCall(url, args){
    var http = new XMLHttpRequest();
    http.open("POST", url, false);
    _httpSend(http, args);
    return http.status==200? http.responseText: http.responseText;
}

function httpCall(url, args){
    return JSON.parse(httpRawCall(url, obj2QueryString(args)));
}

function _pyRpc(url, func, args, kw){
    var [result,traceback] = httpCall(url, {func:func, args:(args||[]), kw:(kw||{})});
    if(traceback != null)throw traceback;
    return result;
}

function PyRpc(url){
    this.url = url || 'psh.cgi';
}

PyRpc.prototype.__noSuchMethod__ = function(name, args){
    return _pyRpc(this.url, name, [], args? args[0]: {});
}

// ComPyRpc means `common PyRpc'
function ComPyRpc(pyRpc){ this.pyRpc = (pyRpc || new PyRpc());}
ComPyRpc.prototype.id = function() this.pyRpc.id({});
ComPyRpc.prototype.get = function(path) this.pyRpc.get({path:path});
ComPyRpc.prototype.set = function(path, content) this.pyRpc.set({path:path, content:content});
ComPyRpc.prototype.popen = function(cmd, path) this.pyRpc.popen({cmd:cmd, path:path});

function safeCall(func, arg) {
    var result, exception;
    try{
        result = func(arg);
    }catch(e){
        exception = e;
    }
    return [result, exception]
}

function dump2html(ret, err, _ret, _err) [_ret.innerHTML, _err.innerHTML] = [str(ret), exceptionFormat(err)]
function dumpCall(func, arg, _ret, _err){ var [ret, err] = safeCall(func, arg);  return dump2html(ret, err, _ret, _err);}
function mkDumper(func, _ret, _err) function(arg) dumpCall(func, arg, _ret, _err)

// lish means `line shell'
function _lish(interp, input) {
    bindHotKey(top, 'ctrl-alt-i', function(e) input.focus());
    bindHotKey(input, 'enter', function(e) interp(e.target.value));
    input.focus();
    return function(expr) interp(input.value=expr.trim());
}

function lish(interp, panel) {
    panel.innerHTML = '<input type="text" class="input"/><pre class="error"></pre><pre class="output"></pre>';
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
    return _fish(function(line, content, caret) sched.execute(mkTasks(filter(line, content, caret), sh)), $s(panel, 'input'));
}

// use seq.map to makesure seq is an array instead of a string.
function mkTasks(seq, func) seq.map(function(i) typeof(i)=='number'? [null, null, i]: [func, i, 10])
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
