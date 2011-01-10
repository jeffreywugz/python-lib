// algorithmic
function irange(n){ for(let i = 0; i < n; i++ )yield i;}
function listk(iter) [i for(i in iter)]
function listv(iter) [i for each(i in iter)]
function range(n) listk(irange(n))
function zip(A, B) [[A[i], B[i]] for(i in A)]
function dict(pairs){ var result = {}; for each([k,v] in pairs) result[k] = v;  return result;}
function dictMap(f, d){ return dict([k, f(v)] for each([k,v] in Iterator(d))); }
Number.prototype.__iterator__ = function() { for ( let i = 0; i < this; i++ )yield i;};
function repeat(n, x){ for (var i=0; i<n; i++)yield x; }
function bind(obj, attrs) {for ([k,v] in Iterator(attrs))obj[k]=v; return obj;}

// string related
function repr(obj) {return JSON.stringify(obj);}
function str(obj){ return typeof obj == 'string'? obj: repr(obj);}
function sub(str, dict) str.replace(/{(\w+)}/g, function(m,k) dict[k])
String.prototype.format = function(dict) sub(this, dict);
String.prototype.seqSub = function(pat, seq) [typeof(i)=="string"? this.replace(pat, i): i for each(i in seq)];
function basename(path) path.replace(/.*\//, '')
function dirname(path) path.replace(/\/[^\/]*$/, '')
function str2dict(pat, str){
    var [rexp, keys] = [pat.replace(/\(\w+=(.*?)\)/g, '($1)'), pat.match(/\((\w+)=.*?\)/g) || []]
    keys = keys.map(function(i) i.replace(/\((\w+)=.*?\)/, '$1'));
    return let(m=str.match(rexp)) m? dict(zip(['__self__'].concat(keys), m)): null;
}

//global environment
function log() window.console &&  console.log.apply(null, arguments)
function getUrl() window.location.pathname
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

function http(url, content){
    var req = new XMLHttpRequest();
    req.open("POST", url, false);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.setRequestHeader("Connection", "close");
    req.send(content);
    return req.responseText;
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

