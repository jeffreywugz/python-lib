// algorithmic
function dict(pairs){ var result = {}; for each([k,v] in pairs) result[k] = v;  return result;}
function dictMap(f, d){ return dict([k, f(v)] for each([k,v] in Iterator(d))); }

// string related
function repr(obj) {return JSON.stringify(obj);}
String.prototype.format = function() this.replace(/\{(\d+)\}/g, function(m,i) arguments[i])

//global environment
function getQueryArgs(){ return parseQueryString(location.search.substring(1));}
function parseQueryString(query){ return dict(p.match(/([^=]+)=(.*)/).slice(1) for each(p in query.split('&')) if(p));}
function encodeQueryString(args){ return [k + "=" + encodeURIComponent(args[k].toString()) for(k in args)].join('&');}
function obj2QueryString(obj){return encodeQueryString(dictMap(function(v)JSON.stringify(v), obj));}
function error_format(msg, url, lineno){ return repr([msg, url, lineno]);}
function onerror(msg, url, lineno) { alert(error_format(msg, url, lineno)); return true;}
window.onerror = onerror;

// DOM element operation
function $(id){ return document.getElementById(id);}
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

// hot key related
function hotKeyPressed(e, key){ return e.ctrlKey && e.altKey && String.fromCharCode(e.charCode).toUpperCase() == key.toUpperCase();}
function installHotKey(w, key, handler){ w.addEventListener("keypress", function(e) hotKeyPressed(e, key) && handler(w), false);}
function installHotKeys(w, bindings){ for(name in bindings) installHotKey(w, name, bindings[name]);}
function overrideEnterKey(w, handler){ w.addEventListener('keypress', function(e) e.which==13 && handler(w), false);}

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

function pyRpc(url){
    this.url = url || '/local/python-lib/bin/psh.cgi';
}

pyRpc.prototype.__noSuchMethod__ = function(name, args){
    args = args || [{}];
    return _pyRpc(this.url, name, args.slice(0,-1), args[args.length-1]);
}

// shell is intented for debug using
function shell(interp, panel, expr, result, error) {
    result.innerHTML = "";
    error.innerHTML = "";

    try{
        resultMsg = interp(expr);
        if(typeof(resultMsg) != "string")
            resultMsg = JSON.stringify(resultMsg);
        result.innerHTML = resultMsg;
    }catch(e){
        show(panel);
        errMsg = e.toString();
        if(e.stack != undefined)
            errMsg += "\n" + e.stack.toString();
        error.innerHTML = errMsg;
    }
}

function _installShell(interp, panel, input, output, error){
    installHotKeys(top, {'i': function(w) input.focus(), 'h': function(w) toggleVisible(panel)});
    overrideEnterKey(input, function(w) shell(interp, panel, input.value, output, error));
    input.focus();
    return function(expr)  input.value = expr && shell(interp, panel, expr, output, error);
}

function installShell(interp, panel) {
    panel.innerHTML = '<input type="text" class="input"/><pre class="error"></pre><pre class="output"></pre>';
    return _installShell(interp, panel, $s(panel, 'input'), $s(panel,'output'), $s(panel, 'error'));
}

function catInterp(expr){ alert(expr); return expr; }
