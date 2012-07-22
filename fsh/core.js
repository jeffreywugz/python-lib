// algorithmic
function identity(x) { return x; }
function minA(A){ return Math.min.apply(null, A); }
function maxA(A){ return Math.max.apply(null, A); }
function min(){ return minA(array(arguments)); }
function max(){ return maxA(array(arguments)); }
function range(n){ var res = []; for(var i = 0; i < n; i++)res.push(i); return res; }
function len(a){ return a.length;}
function listk(iter) { var res = []; for(var i in iter)res.push(i); return res; }
function listv(iter) { var res = []; for(var i in iter)res.push(iter[i]); return res; }
function filter(f, ls){ var res = []; for(var x in ls) if(f(ls[x]))res.push(ls[x]); return res;}
function map(f, ls) { var res = []; for(var x in ls)res.push(f(ls[x])); return res;}
function array(x) { var res = []; for(var i = 0; i < x.length; i++)res.push(x[i]); return res;}
function zipA(As) { var res = []; for(var i in range(minA(map(len, As)))) res.push(map(function(A){ return A[i];}, As)); return res;}
function zip(){ return zipA(array(arguments));}
function enumerate(iter){ return zip(range(len(iter)), iter);}
function dict(pairs){ var result = {}; for(var i in pairs) result[pairs[i][0]] = pairs[i][1];  return result;}
function dict_filter(f, d){ var res = {}; for(var k in d) if(f(d[k]))res[k] = d[k]; return res;}
function dict_map(f, ls) { var res = []; for(var x in ls)res.push([x, f(ls[x])]); return dict(res);}
function repeat(n, x){ var res = []; for (var i=0; i<n; i++)res.push(x); return res;}
function list_mergeA(As){ return [].concat.apply([], As); }
function list_merge(){ return list_mergeA(array(arguments)); }
function bind(obj, attrs) {for (var k in attrs)obj[k]=attrs[k]; return obj;}
function clone(obj) { return obj == null?null: bind({}, obj);}
function dict_merge(A, B){ var res = clone(A); for(var k in B)res[k] = (A[k] || B[k]); return res;}
// string related
function repr(obj) {return JSON.stringify(obj);}
function str(obj){ return typeof obj == 'string'? obj: repr(obj);}
function sub(str, dict) { return str.replace(/{(\w+)}/g, function(m,k){ return dict[k]; }); }
String.prototype.format = function(dict) { return sub(this, dict); }
String.prototype.seqSub = function(pat, seq) {self=this; return map(function(x) {return typeof(x)=="string"? self.replace(pat, x): x; }, seq); }
function basename(path) {return path.replace(/.*\//, ''); }
function dirname(path) {return path.replace(/\/[^\/]*$/, ''); }
function str2dict(pat, str){
    var rexp = pat.replace(/\(\w+=(.*?)\)/g, '($1)');
    var keys = pat.match(/\((\w+)=.*?\)/g) || [];
    var m = null;
    keys = keys.map(function(i){return i.replace(/\((\w+)=.*?\)/, '$1');});
    m = str.match(rexp);
    return  m? dict(zip(['__self__'].concat(keys), m)): null;
}

//global environment
function log() { window.console &&  console.log.apply(window.console, arguments); }
function getUrl() { return window.location.pathname; }
function getQueryArgs(){ return parseQueryString(window.location.search.substring(1));}
function parseQueryString(query){ return dict(map(function(p) { return p.match(/([^=]+)=(.*)/).slice(1); }, filter(identity, query.split('&'))));}
function encodeQueryString(args){ return map(function(k){ return k + "=" + encodeURIComponent(args[k].toString()); },  listk(args)).join('&');}
function obj2QueryString(obj){return encodeQueryString(dict_map(repr, obj));}
function errorFormat(msg, url, lineno){ return repr([msg, url, lineno]);}
function exceptionFormat(e){ return e? e.toString() + '\n' + str(e.stack): "";}
function onerror(msg, url, lineno) { alert(errorFormat(msg, url, lineno)); return true;}
//window.onerror = onerror;

// DOM element operation
function $(id) {return document.getElementById(id); }
function $n(tag) {return document.createElement(tag); }
function $F(id) {return $(id).value; }
function $c(w, c) { return filter(function (x){ return x.className == c; }, w.childNodes); }
function $s(w, c) { return $c(w, c)[0]; }
function insertAfter(parent, node, referenceNode){ parent.insertBefore(node, referenceNode.nextSibling);}
function hide(w) { w.style.display = 'none'; }
function show(w) { w.style.display = 'block'; }
function isVisible(w) {return w.style.display != 'none'; }
function toggleVisible(w) { isVisible(w)?hide(w):show(w);}
function setHeight(w) {w.style.height = w.scrollHeight + "px";}
function scrollTo(w, top) {w.scrollTop = top;}
function textAreaGetCaret(textArea) {return textArea.selectionStart;}
function textAreaSetCaret(textArea, caret) {textArea.setSelectionRange(caret, caret);}

function selectNode(node){
    var select = window.getSelection();
    var range = document.createRange();
    range.selectNode(node);
    select.removeAllRanges();
    select.addRange(range);
}

// hot key/click related
function parseHotKey(key){
    var funcKeys = {backspace:8, tab:9, enter:13, pause:19, escape:27, space:32,
                   pageup:33, pagedown:34, end:35, home:36, left:37, up:38, right:39, down:40,
                   print:44, insert:45, del:46,
                   f1:112, f2:113, f3:114, f4:115, f5:116, f6:117, f7:118, f8:119, f9:120, f10:121, f11:122, f12:123,
                   numlock:144, scrolllock:145,};
    function km(pat){ var m = key.toLowerCase().match(pat); return m? m[0]: null;}
    function get_normal_key(){ var key = km(/\W[a-zA-Z]$/); return key?key[1]:null;}
    return {ctrl:km('ctrl'), alt:km('alt'), shift:km('shift'), button: km(/button[0-9]$/), wheel: km(/wheel$/),
            key: get_normal_key(), func: funcKeys[km(/\w+$/)]};
}

function isHotKey(e, key){
    var k = parseHotKey(key);
    return (!k.ctrl || e.ctrlKey) && (!k.alt || e.altKey) && (!k.shift || e.shiftKey)
        && (!k.key || k.key.toUpperCase() == String.fromCharCode(e.keyCode).toUpperCase())
        && (!k.func || k.func == e.which)
        && (!k.button || parseInt(k.button.substr(-1)) == e.button)
        && (k.key || k.func || k.button || k.wheel);
}

function getWheelDelta(e){ return e.wheelDelta != null? e.wheelDelta: 40*e.detail;}
function hotKeyType(key) { return key.match('wheel$')? 'mousewheel:DOMMouseScroll': key.match('button[0-9]$')? 'click': 'keydown'; }
function bindHotKey(w, key, handler){ map(function(type){ w.addEventListener(type, function(e){ isHotKey(e, key) && handler(e);}, false);}, hotKeyType(key).split(':')); }
function bindHotKeys(w, bindings){ for(var name in bindings)bindHotKey(w, name, bindings[name]); }

function http(url, content){
    var req = new XMLHttpRequest();
    req.open("POST", url, false);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    //req.setRequestHeader("Connection", "close");
    req.send(content);
    return req.responseText;
}

// use seq.map to makesure seq is an array instead of a string.
function mkTasks(seq, func){ return seq? seq.map(function(i){ return typeof(i)=='number'? [null, null, i]: [func, i, 0]; }): []; }
function taskFormat(t) {var func = t[0], arg = t[1], delay = t[2]; return func? arg: '#'+delay;}
function Scheduler(){}
Scheduler.prototype.cancel = function(){ clearTimeout(this.timer);}
Scheduler.prototype.execute = function(tasks, i){
    this.onExecute && this.onExecute(tasks,i);
    this.cancel();
    if(!tasks || tasks.length <= i)return;
    var func = tasks[i][0], arg = tasks[i][1], delay = tasks[i][2];
    if(func && !func(arg))return;
    self = this;
    this.timer = setTimeout(function(){return self.execute(tasks, i+1);}, delay);
}
