OPTIONS = {
    'Options' : ['P', 'L', 'H', 'daystart', 'depth', 'ignore_readdir_race',
                 'maxdepth', 'mindepth', 'mount', 'noignore_readdir_race',
                 'noleaf', 'regextype', 'xdev'],
    'Name' : ['ilname', 'iname', 'iregex', 'iwholename', 'lname', 'name',
              'path', 'regex', 'samefile'],
    'Perm' : ['executable', 'gid', 'group', 'nogroup', 'nouser', 'perm',
              'readable', 'uid', 'user', 'writable'],
    'Size' : ['empty', 'size'],
    'Time' : ['amin', 'anewer', 'atime', 'cmin', 'cnewer', 'ctime', 'mmin',
              'mtime', 'newer', 'newerXY', 'used'],
    'Type' : ['fstype', 'type', 'xtype'],
    'Others' : ['inum', 'links'],
    'Actions' : ['delete', 'execdir', 'fls', 'fprint', 'fprint0', 'fprintf',
                 'ls', 'ok', 'okdir', 'print', 'print0', 'printf', 'prune']
}

MENUS = [k for k in OPTIONS]
