from common import *
from extra import *
from render import *

def job_run(jobs):
    jobs = ds_updated_by_sub(jobs, expanded_cmd='$job_cmd')
    return ds_updated_by_popen(jobs,  result='$job_run_cmd')

def job_view(jobs):
    return ds_updated_by_popen(jobs, result='$job_view_cmd')

job_attr = {
    'job_run_cmd':'[ -d $log_dir ] || mkdir $log_dir; ( $job_cmd )> $log_dir/$log_file 2>&1 &',
    'job_view_cmd':'tail -n 40 $log_dir/$log_file',
    }
cluster_job_attr = {
    'log_dir': '/tmp/$cluster_job_dir',
    'log_file': '$host.log',
    'job_cmd':'$cluster_job_cmd',
    'cluster_job_cmd':'sshpass -p $passwd scp -r $cluster_job_dir $user@$host:; sshpass -p $passwd ssh $user@$host "cd $cluster_job_dir; $cluster_host_cmd"',
    '_cols_to_render_': ['host', 'expanded_cmd', 'result'],
    }

def make_cluster_job(profile, dir, cmd, hosts=None):
    if hosts != None:
        profile = filter(lambda x: x['host'] in hosts, profile)
    return ds_updated(profile, dict_merge(job_attr, cluster_job_attr), cluster_job_dir=dir, cluster_host_cmd=cmd)

def cprun(profile, dir, cmd, hosts=None, host_mapping=None):
    if hosts:
        hosts = hosts.split(',')
    if host_mapping:
        ranges = gen_list(*hosts)
        hosts = [host_mapping[i] for i in ranges]
    return make_cluster_job(profile, dir, cmd, hosts)

check_list_attrs = ('checktype', 'checkcmd')
check_attr = {
    'log_dir': '/tmp/check',
    'log_file': '$host.$checktype',
    'job_cmd': '$checkcmd',
    '_cols_to_zip_': ['host', 'checktype', '$result'],
    }

def check(profile, check_list, term='txt'):
    return dc_map(dict_merge, profile, [job_attr], ds_make(check_list_attrs, check_list), [check_attr])
    
def gen_makefile_cmds(dir):
    makefile = os.path.join(dir, 'Makefile')
    def get_value(str, key):
        match = re.search('^%s = (.+?)\n'%(key), str, re.M)
        if not match: return ""
        else: return match.group(1)
    def get_value_from_file(path, key):
        return get_value(safe_read(path), key)
    make_flags = get_value_from_file(makefile, 'make-flags')
    exported_targets = get_value_from_file(makefile, 'exported').split()
    local_exported_targets = get_value_from_file(makefile, 'local-exported').split()
    exported_cmds = ["me cprun :$_profile $_dir 'make %s %s' / job_run / render_ds"%(t, make_flags) for t in exported_targets]
    local_exported_cmds = ["make -C $_dir %s >/tmp/$_dir.local 2>&1 &"%(t) for t in local_exported_targets]
    view_cmd = "me cprun :$_profile $_dir 'view' / job_view / render_ds"
    local_view_cmd = "cat /tmp/$_dir.local"
    all_exported = ['view', 'local_view'] + exported_targets + local_exported_targets
    return [('view', view_cmd), ('local_view', local_view_cmd)] + zip(exported_targets, exported_cmds) + zip(local_exported_targets, local_exported_cmds)
