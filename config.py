nodes = ['glnode04', 'glnode05', 'gmnode14', 'gmnode15']
# nodes = ['ga29', 'ganode002', 'ganode003', 'ganode016', 'ganode017', 'gbnode04', 'genode005', 'ginode07', 'glnode04', 'glnode05', 'gmnode14', 'gmnode15']
hi ={
    'gc03vm3': {'ip': '10.10.103.133', 'passwd': '111111'},
    'ganode002': {'ip': '10.10.101.2', 'passwd': '111111'},
    'ganode003': {'ip': '10.10.101.3', 'passwd': '111111'},
    'ganode016': {'ip': '10.10.101.16', 'passwd': '111111'},
    'ganode017': {'ip': '10.10.101.17', 'passwd': '111111'},
    'ga20': {'ip': '10.10.101.20', 'passwd': '111111'},
    'ga21': {'ip': '10.10.101.21', 'passwd': '111111'},
    'ga22': {'ip': '10.10.101.22', 'passwd': '111111'},
    'ga23': {'ip': '10.10.101.23', 'passwd': '111111'},
    'ga27': {'ip': '10.10.101.27', 'passwd': '111111'},
    'ga28': {'ip': '10.10.101.28', 'passwd': '111111'},
    'ga29': {'ip': '10.10.101.29', 'passwd': '111111'},
    
    # 'gbnode01': {'ip': '10.10.102.1', 'passwd': '111111'},
    # 'gbnode02': {'ip': '10.10.102.2', 'passwd': '111111'},
    'gbnode03': {'ip': '10.10.102.3', 'passwd': '111111'},
    'gbnode04': {'ip': '10.10.102.4', 'passwd': '111111'},
    'gbnode07': {'ip': '10.10.102.7', 'passwd': '111111'},
    'gbnode08': {'ip': '10.10.102.8', 'passwd': '111111'},
    'gbnode09': {'ip': '10.10.102.9', 'passwd': '111111'},
    
    'genode005': {'ip': '10.10.105.5', 'passwd': 'dcosdcos'},
    # 'genode006': {'ip': '10.10.105.6', 'passwd': 'dcosdcos'},
    
    'ginode07': {'ip': '10.10.108.7', 'passwd': '111111'},
    'ginode08': {'ip': '10.10.108.8', 'passwd': '111111'},
    
    'glnode04': {'ip': '10.10.111.4', 'passwd': '111111'},
    'glnode05': {'ip': '10.10.111.5', 'passwd': '111111'},
    
    'gmnode14': {'ip': '10.10.113.14', 'passwd': '111111'},
    'gmnode15': {'ip': '10.10.113.15', 'passwd': '111111'},
    }
rootprofile = [{'host':host, 'user':'root', 'passwd':hi[host]['passwd']} for host in nodes]
userprofile = [{'host':host, 'user':'ans42', 'passwd':'a'} for host in nodes]
allnodes = sorted(hi.keys())

ct = {
    'raw': '$cmd',
    'sputpass': 'sshpass -p $passwd scp -r $path $user@$host:',
    'sshpass': 'sshpass -p $passwd ssh $user@$host $cmd',
    'raw_install':'(sshpass -p $passwd scp -r $pkg_dir $user@$host: ; sshpass -p $passwd ssh $user@$host make -C $pkg_name ) >$log_dir/console.$host 2>&1 &',
    
    'ssh': 'ssh $user@$host "cd $work_dir; $cmd"',
    'tty': 'ssh -t $user@$host "cd $work_dir; $cmd"',
    'bg': 'ssh $user@$host "cd $work_dir; $cmd" 1>$log_dir/console.$host 2>&1 &',
    'rbg': 'ssh $user@$host "cd $work_dir; [ -d $log_dir ] || mkdir -p $log_dir; $cmd 1>$log_dir/console.$host 2>&1 &"',
    'install':'(scp -r $pkg_dir $user@$host: ; ssh $user@$host make -C $pkg_name ) >$log_dir/console.$host 2>&1 &',
    
    'get': 'scp -r $user@$host:$remote/* $local',
    'put': 'scp -r $local $user@$host:$remote',
    'cat': 'ssh $user@$host cat "$file"',
    }
