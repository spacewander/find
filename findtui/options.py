try:
    import enum  # py >= 3.4
except ImportError:
    enum = None

import platform
import textwrap
from collections import namedtuple


if enum is None:
    CHECKBOX_OPTION = 0 # L, readable, delete, ...
    RADIO_BUTTON_OPTION = 1 # type, ...
    PATH_INPUT_OPTION = 2 # name, ...
    TEXT_INPUT_OPTION = 3 # execdir, ...
    INT_INPUT_OPTION = 4 # maxdepth, ...
else:
    class OptionType(enum.IntEnum):
        CHECKBOX_OPTION = 0
        RADIO_BUTTON_OPTION = 1
        PATH_INPUT_OPTION = 2
        TEXT_INPUT_OPTION = 3
        INT_INPUT_OPTION = 4

    globals().update(OptionType.__members__)

GNU_FIND = False
BSD_FIND = False
current_os = platform.system()

if current_os == 'Linux' or current_os.startswith('CYGWIN'):
    GNU_FIND = True
else:
    BSD_FIND = True # have not support find(1) on other posix system yet :)

Option = namedtuple('Option', ['name', 'type', 'description', 'data', 'example'])
Option.__new__.__defaults__ = ('', CHECKBOX_OPTION, '', {}, """""")

OPTIONS = {
    'Options' : [
        Option('H', CHECKBOX_OPTION,
               'only follow symlinks when resolving command-line arguments'),
        Option('L', CHECKBOX_OPTION, 'follow symlinks'),
        Option('P', CHECKBOX_OPTION, 'never follow symlinks'),
        Option('depth', CHECKBOX_OPTION,
               'process contents before the directory itself',
               example="""
               $ find .
               .
               ./a
               ./b

               $ find . -depth
               ./a
               ./b
               .
               """),
        Option('ignore_readdir_race', CHECKBOX_OPTION, 'ignore stat file failure'),
        Option('maxdepth', INT_INPUT_OPTION, 'apply at most n levels',
               example="""
               $ find . -maxdepth 0
               .

               $ find . -maxdepth 2
               .
               ./1
               ./1/2
               """),
        Option('mindepth', INT_INPUT_OPTION, 'do not apply at levels less than n',
               example="""
               $ find . -mindepth 2
               ./1/2
               """),
        Option('mount', CHECKBOX_OPTION, 'do not apply on other filesystems'),
        Option('noignore_readdir_race', CHECKBOX_OPTION, 'turn off -ignore_readdir_race')
    ],
    'Name' : [
        Option('ilname', PATH_INPUT_OPTION,
               'is a symbolic link matched given pattern, case insensitive',
               example="""
               $ find . -ilname 'f*'
               ./lsdiff
               $ file lsdiff
               lsdiff: symbolic link to `filterdiff'`
               """),
        Option('iname', PATH_INPUT_OPTION,
               'basename matches pattern given, case insensitive',
               example="""
               $ find . -iname 'ls*'
               ./lsdiff
               $ find . -iname '*ls*'
               ./lsdiff
               ./hwloc-ls
               """),
        Option('iregex', PATH_INPUT_OPTION,
               'name matches regular expression pattern given, case insensitive',
               example="""
               $ find . -iregex 'ls.*' # use re
               $ find . -iregex './ls.*' # match path instead of basename
               ./lsdiff
               """),
        Option('iwholename', PATH_INPUT_OPTION,
               'name matches pattern given, case insensitive',
               example="""
               $ find . -iwholename './ls*' # match path
               ./lsdiff
               """),
        Option('lname', PATH_INPUT_OPTION,
               'is a symbolic link matched given pattern',
               example="""
               $ find . -lname 'f*'
               ./lsdiff
               $ file lsdiff
               lsdiff: symbolic link to `filterdiff'`
               """),
        Option('name', PATH_INPUT_OPTION, 'basename matches pattern given',
               example="""
               $ find . -name 'ls*'
               ./lsdiff
               $ find . -name '*ls*'
               ./lsdiff
               ./hwloc-ls
               """),
        Option('path', PATH_INPUT_OPTION, 'pathname matches pattern given',
               example="""
               $ find . -path './ls*' # match path
               ./lsdiff
               """),
        Option('regex', PATH_INPUT_OPTION,
               'name matches regular expression pattern given',
               example="""
               $ find . -iregex 'ls.*' # use re
               $ find . -iregex './ls.*' # match path instead of basename
               ./lsdiff
               """),
        Option('samefile', PATH_INPUT_OPTION, 'refers to the same inode as name given'),
    ],
    'Perm' : [
        Option('group', TEXT_INPUT_OPTION, 'belongs to group given',
               example="""
               $ find . -group root
               ./files_owned_by_root_group
               """),
        Option('nogroup', CHECKBOX_OPTION, "no group corresponds to file's numeric group ID"),
        Option('nouser', CHECKBOX_OPTION, "no user corresponds to file's numeric user ID"),
        Option('perm', TEXT_INPUT_OPTION,
               'the permission bits mode are set for the file',
               example="""
               # find files writable by their owner and group
               $ find . -perm -220
               $ find . -perm -g+w,u+w
               # find files writable by their owner or group
               $ find . -perm /220
               $ find . -perm /g+w,u+w
               $ find . -perm 222 # find files only writable(can't read or execute)
               """),
        Option('user', TEXT_INPUT_OPTION, 'is owned by user given',
               example="""
               $ find . -user root
               ./files_owned_by_root
               """),
    ],
    'Size' : [
        Option('empty', CHECKBOX_OPTION,
               'is empty and is a regular file or directory',
               example="""
               $ find . -empty
               ./.git/branches
               $ ls ./.git/branches # empty directory
               """),
        Option('size', TEXT_INPUT_OPTION, 'uses n units[b|c|w|k|M|G] of space',
               example="""
               $ find . +20k # files > 20k
               $ find . 20k # files == 20k
               $ find . -20k # files < 20k
               """)
    ],
    'Time' : [
        Option('amin', TEXT_INPUT_OPTION, 'accessed n minutes ago',
               example="""
               $ find . -amin +20 # now - atime > 20 minutes
               $ find . -amin 20 # now - atime == 20 minutes
               $ find . -amin -20 # now - atime < 20 minutes
               """),
        Option('anewer', PATH_INPUT_OPTION,
               'accessed more recently than given file was modified',
               example="""$ find . -anewer this_file"""),
        Option('cmin', TEXT_INPUT_OPTION, "status was changed n minutes ago",
               example="""
               $ find . -cmin +20 # now - ctime > 20 minutes
               $ find . -cmin 20 # now - ctime == 20 minutes
               $ find . -cmin -20 # now - ctime < 20 minutes
               """),
        Option('cnewer', PATH_INPUT_OPTION,
               "status was changed more recently than given file was modified",
               example="""$ find . -cnewer this_file"""),
        Option('mmin', TEXT_INPUT_OPTION, 'modified n minutes ago',
               example="""
               $ find . -mmin +20 # now - mtime > 20 minutes
               $ find . -mmin 20 # now - mtime == 20 minutes
               $ find . -mmin -20 # now - mtime < 20 minutes
               """),
        Option('newer', PATH_INPUT_OPTION,
               'modified more recently than file given',
               example="""$ find . -newer this_file"""),
        Option('used', TEXT_INPUT_OPTION,
               'accessed n days after its status was last changed',
               example="""
               $ find . -used +20 # atime - ctime > 20 days
               $ find . -used 20 # atime - ctime == 20 days
               $ find . -used -20 # atime - ctime < 20 days
               """),
    ],
    'Type' : [
        Option('fstype', TEXT_INPUT_OPTION, 'is on a filesystem of given type',
               example="""$ find . -fstype ext4"""),
        Option('type', RADIO_BUTTON_OPTION, 'is of type chosen', {
                'type' : ['b', 'c', 'd', 'p', 'f', 'l', 's']
                },
                example="""
                $ find . -type f # file
                $ find . -type d # directory
                $ find . -type l # symbolic link
                $ find . -type s # socket
                """),
    ],
    'Others' : [
        Option('inum', INT_INPUT_OPTION, 'has inode number n'),
        Option('links', TEXT_INPUT_OPTION, 'has n links'),
        Option('true', CHECKBOX_OPTION, 'always true'),
        Option('false', CHECKBOX_OPTION, 'always false'),
    ],
    'Actions' : [
        Option('delete', CHECKBOX_OPTION, 'delete files',
               example="""
               $ find . -name trash -delete # delete trash
               """),
        Option('exec', TEXT_INPUT_OPTION, 'execute command',
               example="""
               $ find . -name trash* -exec rm {} \;
               # rm trash0; rm trash1
               $ find . -name trash* -exec rm {} +
               # rm trash0 trash1
               """),
        Option('execdir', TEXT_INPUT_OPTION,
               'execute command from the subdirectory containing matched file'),
        Option('ls', TEXT_INPUT_OPTION,
               'list current file with ls -dils',
               example="""
               $ find . -name match -ls
               4129127    4 drwxrwxr-x   3 ...
               """),
        Option('ok', TEXT_INPUT_OPTION, 'like -exec but ask user first'),
        Option('okdir', TEXT_INPUT_OPTION, 'like -execdir but ask user first'),
        Option('print', CHECKBOX_OPTION, 'print full file name'),
        Option('print0', CHECKBOX_OPTION, 'print full file name, followed by a null character'),
        Option('prune', CHECKBOX_OPTION, 'if the file is a directory, do not descend into it'),
    ]
}

if GNU_FIND:
    PLATFORM_SPECIFIC_OPTIONS = {
        'Options' : [
            Option('daystart', CHECKBOX_OPTION, 'measure times from the beginning of today rather than from 24 hours ago'),
            Option('regextype', RADIO_BUTTON_OPTION, 'change the regular expression syntax',
                   {
                    'type' : ['emacs', 'posix-awk', 'posix-basic',
                            'posix-egrep', 'posix-extended']
                   }
            ),
            Option('xdev', CHECKBOX_OPTION, 'do not apply on other filesystems')
        ],
        'Name' : [],
        'Perm' : [
            Option('readable', CHECKBOX_OPTION, 'is readable'),
            Option('writable', CHECKBOX_OPTION, 'is writable'),
            Option('executable', CHECKBOX_OPTION, 'is executable'),
            Option('gid', TEXT_INPUT_OPTION, 'numeric group ID is n',
                   example="""
                   $ find . -gid 1000 # gid == 1000
                   $ find . -gid -1000 # gid < 1000
                   $ find . -gid +1000 # gid > 1000
                   """),
            Option('uid', TEXT_INPUT_OPTION, 'numeric user ID is n',
                   example="""
                   $ find . -uid 1000 # uid == 1000
                   $ find . -uid -1000 # uid < 1000
                   $ find . -uid +1000 # uid > 1000
                   """),
        ],
        'Size' : [],
        'Time' : [
            Option('atime', TEXT_INPUT_OPTION, 'accessed n*24 hours ago',
               example="""
               $ find . -atime +20 # now - atime > 20 days
               $ find . -atime 20 # now - atime == 20 days
               $ find . -atime -20 # now - atime < 20 days
               """),
            Option('ctime', TEXT_INPUT_OPTION,
                   'status was changed n*24 hours ago',
                   example="""
                   $ find . -ctime +20 # now - ctime > 20 days
                   $ find . -ctime 20 # now - ctime == 20 days
                   $ find . -ctime -20 # now - ctime < 20 days
                   """),
            Option('mtime', TEXT_INPUT_OPTION, 'modified n*24 hours ago',
               example="""
               $ find . -mtime +20 # now - mtime > 20 daya
               $ find . -mtime 20 # now - mtime == 20 days
               $ find . -mtime -20 # now - mtime < 20 days
               """),
        ],
        'Type' : [
            Option('xtype', RADIO_BUTTON_OPTION, 'same as -type, but for symbolic link, it checks the type of file',
                   {
                       'type' : ['b', 'c', 'd', 'p', 'f', 'l', 's']
                   }
            )
        ],
        'Others' : [],
        'Actions' : [
            Option('fls', PATH_INPUT_OPTION, 'like -ls but wirte to file like -fprint'),
            Option('fprint', PATH_INPUT_OPTION, 'print full file name into file'),
            Option('fprint0', PATH_INPUT_OPTION, 'like -print0 but write to file like -fprintf'),
            Option('fprintf', PATH_INPUT_OPTION, 'like -printf but write to file like -fprint'),
            Option('printf', TEXT_INPUT_OPTION,
                   'print format on the standard output',
                   example="""
                   $ find . -name find -printf "%p size:%s\n"
                   ./build/lib.linux-x86_64-2.7/find size:4096
                   """),
            Option('quit', CHECKBOX_OPTION, 'exit immediately')
        ]
    }
elif BSD_FIND:
    PLATFORM_SPECIFIC_OPTIONS = {
        'Options' : [
            Option('E', CHECKBOX_OPTION, 'use extended regular expressions'),
            Option('X', CHECKBOX_OPTION, 'safely use find with xargs(1)'),
            Option('f', TEXT_INPUT_OPTION, 'specify a file hierarchy to traverse'),
            Option('s', CHECKBOX_OPTION, 'traverse file hierarchies in lexicographical order'),
            Option('x', CHECKBOX_OPTION, 'do not apply on directories have a different device number'),
        ],
        'Name' : [
            Option('ipath', PATH_INPUT_OPTION, 'pathname matches pattern given, case insensitive'),
        ],
        'Perm' : [
            Option('gid', TEXT_INPUT_OPTION, 'same as -group gname',
               example="""
               $ find . -group root
               ./files_owned_by_root_group
               """),
            Option('flags', TEXT_INPUT_OPTION, 'with or without specific flags'),
        ],
        'Size' : [],
        'Time' : [
            Option('Bmin', TEXT_INPUT_OPTION, "file's inode created n minutes ago"),
            Option('Bnewer', PATH_INPUT_OPTION, "file's inode created more recently than given file was modified"),
            Option('Btime', TEXT_INPUT_OPTION, "file's inode created n units[s|m|h|d|w] ago, the default unit is d"),
            Option('atime', TEXT_INPUT_OPTION,
                   'accessed n units[s|m|h|d|w] ago, the default unit is d',
                   example="""
                   $ find . -atime +20 # now - atime > 20 days
                   $ find . -atime 20 # now - atime == 20 days
                   $ find . -atime -20 # now - atime < 20 days
                   """),
            Option('ctime', TEXT_INPUT_OPTION,
                   'status changed n units[s|m|h|d|w] ago, the default unit is d',
                   example="""
                   $ find . -ctime +20 # now - ctime > 20 days
                   $ find . -ctime 20 # now - ctime == 20 days
                   $ find . -ctime -20 # now - ctime < 20 days
                   """),
            Option('mtime', TEXT_INPUT_OPTION,
                   'modified n units[s|m|h|d|w] ago, the default unit is d',
                   example="""
                   $ find . -mtime +20 # now - mtime > 20 days
                   $ find . -mtime 20 # now - mtime == 20 days
                   $ find . -mtime -20 # now - mtime < 20 days
                   """),
        ],
        'Type' : [
            Option('xattr', CHECKBOX_OPTION, 'has any extended attributes'),
            Option('xattrname', TEXT_INPUT_OPTION, 'has an extended attribute with specified name')
        ],
        'Others' : [
            Option('acl', TEXT_INPUT_OPTION, 'lcoate files with extended ACLs')
        ],
        'Actions' : []
    }
else:
    PLATFORM_SPECIFIC_OPTIONS = {}

for k in OPTIONS:
    OPTIONS[k] += PLATFORM_SPECIFIC_OPTIONS.get(k, [])
    # format example, remove indents
    for idx, opt in enumerate(OPTIONS[k]):
        if opt.example != '':
            # namedtuple is immutable
            OPTIONS[k][idx] = Option(opt.name, opt.type, opt.description,
                    opt.data, textwrap.dedent(opt.example))
    OPTIONS[k].sort()

# MENUS : ['Actions', ... 'Type']
MENUS = sorted([k for k in OPTIONS])

# OPTION_NAMES : [..., '-mtime', ...]
# OPTION_DATA : {..., '-mtime' : '-mtime -- blahblah', ...}
OPTION_NAMES = []
OPTION_DATA = {}
for k in OPTIONS:
    OPTION_NAMES.extend(['-' + opt.name for opt in OPTIONS[k]])
    for opt in OPTIONS[k]:
        OPTION_DATA['-'+opt.name] = "-%s -- %s" % (opt.name, opt.description)

# ACTION_OPTIONS : delete, ls, print
ACTION_OPTIONS = set(opt.name for opt in OPTIONS['Actions'])

