function repr(obj) {
    return JSON.stringify(obj);
}

function error_format(msg, url, lineno){
    return repr([msg, url, lineno]);
}

function onerror(msg, url, lineno) {
    alert(error_format(msg, url, lineno));
    return true;
}

// window.onerror = onerror;

String.prototype.format = function(){
    var args = arguments;
    return this.replace(/\{(\d+)\}/g,               
        function(m,i){
            return args[i];
        });
}

function q(id) {
    return document.getElementById(id);
}

function getQueryArgs(){
    var query = location.search.substring(1);
    return parseQueryString(query);
}

function parseQueryString(query){
    var args = {};
    var pairs = query.split("&");
    for(var i in pairs){
        var pos = pairs[i].indexOf("=");
        var argname = pairs[i].substring(0,pos);
        var value = pairs[i].substring(pos+1);
        args[argname] = decodeURIComponent(value);
    }
    return args;
}

function encodeQueryString(args){
    var newArgs = []
    for(var k in args){
        newArgs.push(k + "=" + encodeURIComponent(args[k].toString()));
    }
    return newArgs.join('&');
}

function HotKeyManager(bindings) {
    this.keyMap = {};
    for(name in bindings) this.keyMap[name.toUpperCase()] = bindings[name];
}

HotKeyManager.prototype.install = function(element) {
    var hotKeyManager = this;
    function handler(event) { return hotKeyManager.handler(event); }
    element.addEventListener("keypress", handler, false);
}

HotKeyManager.prototype.handler = function(event) {
    if(!event.ctrlKey)return;
    var key = String.fromCharCode(event.charCode).toUpperCase();
    handler = this.keyMap[key];
    if(handler)handler();
}

function httpRawAsyncCall(url, args, handler, faultHandler){
    var http = new XMLHttpRequest();
    if(!faultHandler) faultHandler = function(http){throw http.responseText;};
    http.onreadystatechange = function(){
        if(ajaxReq.readyState != 4)return;
        if(http.status == 200)
            return handler(http);
        else
            return faultHandler(http);
    }
    args = encodeQueryString(args);
    url += "?" + args;
    http.open("GET", url, false);
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.setRequestHeader("Content-length", args.length);
    http.setRequestHeader("Connection", "close");
    http.send(args);
}

function httpAsyncCall(url, args, handler, faultHandler){
    var newArgs = {};
    for (var k in args){
        newArgs[k] = JSON.stringify(args[k]);
    }
    function newHandler(http) {
        handler(JSON.parse(http.responseText));
    }
    httpAsyncRawCall(url, newArgs, handler, faultHandler);
}

function httpRawCall(url, args){
    var http = new XMLHttpRequest();
    args = encodeQueryString(args);
    url += "?" + args;
    http.open("GET", url, false);
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.setRequestHeader("Content-length", args.length);
    http.setRequestHeader("Connection", "close");
    http.send(args);
    if(http.status == 200)
        return http.responseText;
    else
        throw http.responseText;
}

function httpCall(url, args){
    var newArgs = {};
    for (var k in args){
        newArgs[k] = JSON.stringify(args[k]);
    }
    return JSON.parse(httpRawCall(url, newArgs));
}

var http = httpRawCall;
var rpc = httpCall;
function python(expr){
    var results = httpCall('/psh', {'expr':expr});
    var result = results[0];
    var exception = results[1];
    var traceback = results[2];
    if(exception != null)throw traceback;
    return result;
}
function bash(cmd){ return python('popen("{0}")'.format(cmd)); }

function hide(w){ w.style.display = 'none';}
function show(w){ w.style.display = 'block';}
function isVisible(w){ return w.style.display != 'none'; }
function toggleVisible(w){ isVisible(w)?hide(w):show(w);}
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

function catInterp(expr){ alert(expr); return expr; }
function installShell(interp, panel, input, output, error){
    var hotKeyManager = new HotKeyManager({'x': function(){input.focus();}, 'c': function(){toggleVisible(panel)}});
    hotKeyManager.install(top);
    input.addEventListener('keypress',
                           function(event){
                               if(event.which==13)shell(interp, panel, input.value, output, error);
                           },
                           false);
    input.focus();
    return function(expr){
        input.value = expr;
        shell(interp, panel, expr, output, error);
    }
}

function makeHttpCallProxy(url) {
    return function(args){
        return httpCall(url, args);
    }
}

function joinPath(base, path){
    return base + '/' + path;
}

function HttpObj(url, methods){
    this.url = url;
    this.methods = methods;
    for (var i in methods){
        var m = methods[i];
        this[m] = makeHttpCallProxy(joinPath(url, m));
    }
}
