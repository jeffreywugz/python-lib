var _clusterJob = 'job.py {usr}:{passwd}@{hosts}:{dir} {cmd} -/';
var clusterJob = {
    usr:'ans42', passwd:'a', hosts: 'hosts', dir:'base', action: 'bg',
    args: '(?:(?:(hosts=[^:]*):)(dir=[^#]*)#)?(cmd=.*)',
    seq:[_clusterJob + '{action}', 1000, _clusterJob + 'view', 2000, _clusterJob + 'view', 3000, _clusterJob + 'view']
};
