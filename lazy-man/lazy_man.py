#!/usr/bin/env python

from util import *
import os
from subprocess import *

success_target = '<success_target>'

class LMException(Exception):
    def __init__(self, msg, obj):
        self.msg, self.obj = msg, obj
    
    def __str__(self):
        return "LMException: %s: %s"%(self.msg, self.obj)

def nil_action(env, target, deps, all_deps, log):
    pass

class Rule:
    def __init__(self, target=None, depends=None, action=None):
        self.target, self.depends, self.action = target, depends, action
        if type(self.action) == str: self.action = [self.action]
        if type(self.depends) == str:
            self.depends = [self.depends]

    def get_deps(self, target):
        return None

    def do(self, lm, target, all_deps, log):
        deps = self.get_deps(target)
        if self._need_update(target, deps, all_deps):
            if callable(self.action):
                self.action(lm, target, deps, all_deps, log)
            elif type(self.action) == list:
                lm.sh(self.action, log, target=target, deps=deps,all_deps=all_deps)
            else:
                raise LMException("Wrong Action", self.action)

    def __str__(self):
        return "%s <= %s"%(self.target, self.depends)

    @staticmethod
    def _need_update(target, deps, all_deps):
        if not os.path.exists(target):
            return True
        mtime = os.path.getmtime(target)
        for dep in all_deps:
            if not os.path.exists(dep):
                continue
            if os.path.getmtime(dep) > mtime:
                return True
        return False
    
class ExistFileRule(Rule):
    def __init__(self):
        Rule.__init__(self, action=nil_action)

    def get_deps(self, target):
        if os.path.exists(target):
            return [success_target]
        return None

class StaticRule(Rule):
    def __init__(self, target, depends=[success_target], action=nil_action):
        Rule.__init__(self, target, depends, action)

    def get_deps(self, target):
        if target == self.target:
            return self.depends
        return None

class RegexpRule(Rule):
    def __init__(self, target, depends=[success_target], action=nil_action):
        Rule.__init__(self, target, depends, action)

    def get_deps(self, target):
        if not re.match(self.target, target):
            return None
        return [re.sub(self.target, dep, target) for dep in self.depends]
    
class LazyMan(Env):
    def __init__(self, name='default', env={}, rules=[], log=BlockStream()):
        Env.__init__(self, env)
        self.name, self.env, self.rules, self.log = name, env, rules, log
        self.add(ExistFileRule())

    def add(self, *rules):
        self.rules.extend(list_(rules))

    def sh(self, cmd_list, log, **args):
        cmd_list = list_(cmd_list)
        env = dict(self, **args)
        expanded_cmd = [sub(cmd, env) for cmd in cmd_list]
        for item in expanded_cmd:
            log<< "LazyMan $ %s"% (item,)
            if self.dry_run: continue
            err = call(item, shell=True)
            if err: raise LMException("Task Fail", item)

    def do(self, target, log=None):
        if target == success_target:
            return
        if log==None: log=self.log
        if self.verbose:
            log<< "%s =>"%target
        rules, all_deps = self._select_rule(target)
        if not rules: raise LMException("No Rule", target)
        for dep in all_deps:
            self.do(dep, log.new())
        for rule in rules:
            rule.do(self, target, all_deps, log)

    def _select_rule(self, target):
        rules_deps = [(rule,rule.get_deps(target)) for rule in self.rules]
        rules_deps = [(rule, deps) for rule, deps in rules_deps if deps]
        rules = [rule for rule, dep in rules_deps]
        deps = [dep for rule, dep in rules_deps]
        all_deps = list_(deps)
        deps_set =set()
        new_deps = []
        for dep in all_deps:
            if deps_set.issuperset(set([dep])):
                continue
            deps_set.add(dep)
            new_deps.append(dep)
        return rules, new_deps
        
    def do_task(self, target=['default']):
        target = list_(target)
        if not target: target = ["default"]
        for t in target:
            try:        
                self.do(t)
            except LMException,e:
                print "LM: %s" % e
                
    def __str__(self):
        return "LazyMan: %s\nrules:\n%s\n"%(self.name, '\n'.join([str(rule) for rule in self.rules]))
    
