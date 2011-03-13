class Task:
    def __init__(self, task_dir):
        self.dir, self.task_file, self.output = task_dir, '%s/task.txt'%(task_dir), '%s/output.txt'%(task_dir)
        self.status = KVFile(self.task_file)

    def valid(self):
        return os.path.exists(self.task_file)
        
    def execute(self, cmd):
        def end_with(status):
            self.status.update(end_time=time.time(), status=status)
            return status
        setprocname('task-executer')
        p = bg(cmd, self.output)
        if not p: return end_with('failed')
        self.status.update(status='running', pid=p.pid, start_time=time.time())
        p.wait()
        if p.returncode != 0: return end_with('failed')
        else: return end_with('done')
        
    def start(self, res, cmd, tid, allocator=None):
        mkdir(self.dir)
        self.status.lock()
        status = self.status.get('status')
        if status != None: return status
        self.status.update(id=tid, cmd=cmd, res=res, status='allocating', submit_time=time.time())
        #allocator(self, res)
        self.status.update(status='allocated')
        daemon(self.execute, cmd)
        self.status.unlock()

    def res_refed(self):
        pass
    
    def wait(self, interval=1):
        print 'wait for %s'% self.dir
        while True:
            status = self.status.get('status')
            if status == 'done' or status == 'failed':
                return status
            time.sleep(interval)

    def __str__(self):
        return sub('$cmd # $id :: $status', self.status.load())

def list_tasks(top_dir):
    return filter(lambda t: t.valid(), [Task('%s/%s'%(top_dir, d)) for d in os.listdir(top_dir)])

class ResMan:
    def __init__(self, top_dir):
        self.top_dir, self.defs_file = top_dir, '%s/res.txt'%(top_dir)
        self.defs = KVFile(self.defs_file)
        
    def view(self):
        return [(),()]
        defs = [(k,v.split()) for k,v in self.defs.load()]
        usages = [(t, res_refed()) for t in list_tasks(self.top_dir)]
        return defs, filter(lambda t, res: res, usages)

    def alloc(self, task, spec):
        with open(usages_file, 'rw') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            defs, usages = self.view()
            used = list_merge(*[res for tid, res in usages])
            frees = [(type, filter(lambda x: x not in used, list)) for type,list in defs]
            result = [(type,alloc(frees, type, count)) for type,count in spec]
            if [(type,list) for type,list in result if list == None]:
                fcntl.flock(f, fcntl.LOCK_UN)
                return None

    def __str__(self):
        view = '''
Res View: Defs
--------------------------------------------------------------------------------
$defs

Res View: Usages
--------------------------------------------------------------------------------
$usages
'''
        defs, usages = self.view()
        defs = '\n'.join(['%s: %s'%(type, list) for type,list in defs])
        usages = '\n'.join(['%s: %s'%(task, holds) for task,holds in usages])
        return sub(view, defs=defs, usages=usages)
    
class TaskTracker:
    def __init__(self, top):
        self.top_dir, self.config_file, self.queue_file = top, top + '/config.txt', top + '/queue.txt'
        self.config = KVFile(self.config_file)
        self.interval = int(self.config.get('interval', '1'))
        self.res_man = ResMan(top)

    def get_inqueue_tasks(self):
        def parse_task(str):
            m = re.match('([^#]+)(?:#(.*))?', str)
            if not m:return None
            cmd, tid = m.groups()
            if not tid: res = []
            else: tid, res = tid.strip(), [(res_type, int(count)) for res_type, count in re.findall('(\w+)\s*=\s*(\d+)', tid)]
            if re.match('^\s*$', cmd): return None
            return res, cmd, tid
        content = safe_read(self.queue_file)
        return filter(None, map(parse_task, content.split('\n')))

    def get_submitted_tasks(self):
        return list_tasks(self.top_dir)
    
    def get_task_dir(self, tid):
        return self.top_dir + '/' + tid

    def get_task(self, tid):
        return Task(self.get_task_dir(tid))
    
    def start(self, res, cmd, tid=None):
        cmd = cmd.strip()
        if not tid: tid = cmd.replace('/', '\\').replace(' ', '+')
        tid = tid.strip()
        task = self.get_task(tid)
        print '%s: start...'% tid
        task.start(res, cmd, tid, self.res_man.alloc)
        print '%s: wait...'% tid
        task.wait(self.interval)
        print '%s: done.'% tid

    def wait(self, tid):
        return self.get_task(tid).wait(self.interval)
        
    def fifo(self):
        queue = self.get_inqueue_tasks()
        [self.start(res, cmd, tid) for res, cmd, tid in queue]
        return [(tid,self.wait(tid)) for res,cmd,tid in queue]
                
    def view(self):
        inqueue_tasks = [dict(res=res, cmd=cmd, tid=tid, stage='inqueue') for res,cmd, tid in self.get_inqueue_tasks()]
        submitted_tasks = map(lambda x: x.load(), self.get_submitted_tasks())
        return inqueue_tasks, submitted_tasks, self.res_man.view()

    def __str__(self):
        view = '''
Inqueue Tasks:        
--------------------------------------------------------------------------------
$inqueue

Submitted Tasks:
--------------------------------------------------------------------------------
$submitted

$res_view
'''
        inqueue = '\n'.join(['%s # %s'%(cmd, tid) for res,cmd,tid in self.get_inqueue_tasks()])
        submitted = '\n'.join([str(t) for t in self.get_submitted_tasks()])
        return sub(view, inqueue=inqueue, submitted=submitted, res_view=str(self.res_man))
    
    def query(self, tid=None):
        if tid: return str(Task(self.get_task_dir(tid)))
        else: return str(self)
