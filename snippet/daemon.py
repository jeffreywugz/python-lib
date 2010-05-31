def daemonize(stdout_file, stderr_file):
    # os.setsid()
    # os.chdir('/')
    os.umask(0)
    stdin_fd = os.open('/dev/zero', os.O_RDONLY)
    stdout_fd = os.open(stdout_file, os.O_WRONLY|os.O_CREAT)
    stderr_fd = os.open(stderr_file, os.O_WRONLY|os.O_CREAT)
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(stdin_fd, 0)
    os.dup2(stdout_fd, 1)
    os.dup2(stderr_fd, 2)

class Daemon:
    def __init__(self, cmd, log_dir):
        self.cmd, self.log_dir = cmd, log_dir
        mkdir(log_dir)
        self.host = get_hostname()
        self.pid_file = self.gen_name('pid')

    def gen_name(self, name):
        return gen_name(os.path.join(self.log_dir, name), self.host)
    
    def start(self):
        pid = self.get_pid()
        if pid == -1:
            stdout_file = self.gen_name('stdout')
            stderr_file = self.gen_name('stderr')
            print "Daemon start process: %s"%(self.cmd)
            daemonize(stdout_file, stderr_file)
            p=subprocess.Popen(self.cmd, shell=True)
            self.set_pid(p.pid)
        else:
            print "Daemon already started!:%d"% pid
        
    def stop(self):
        pid = self.get_pid()
        if pid == -1:
            print "Daemon: no running process found!"
        else:
            print "Daemon: kill process %d!"%(pid)
            os.kill(pid, 9)

    def restart(self):
        self.stop()
        self.start()

    def set_pid(self, pid):
        f = open(self.pid_file, 'w')
        f.write(str(pid))
        f.close()

    def get_pid(self):
        try:
            f = open(self.pid_file, 'r')
            pid = f.read()
            f.close()
        except exceptions.IOError:
            return -1
        if os.path.exists(os.path.join('/proc', pid)):
            return int(pid)
        else:
            return -1
