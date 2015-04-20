try:
    import enum  # py >= 3.4
except ImportError:
    enum = None

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


Option = namedtuple('Option', ['name', 'type', 'description', 'data'])
Option.__new__.__defaults__ = ('', CHECKBOX_OPTION, '', {})

OPTIONS = {
    'Options' : [
        Option('P', CHECKBOX_OPTION, ''),
        Option('L', CHECKBOX_OPTION, ''),
        Option('H', CHECKBOX_OPTION, ''),
        Option('daystart', CHECKBOX_OPTION, ''),
        Option('depth', CHECKBOX_OPTION, ''),
        Option('ignore_readdir_race', CHECKBOX_OPTION, ''),
        Option('maxdepth', INT_INPUT_OPTION, ''),
        Option('mindepth', INT_INPUT_OPTION, ''),
        Option('mount', CHECKBOX_OPTION, ''),
        Option('noignore_readdir_race', CHECKBOX_OPTION, ''),
        Option('regextype', RADIO_BUTTON_OPTION, '', {
            'type' : ['emacs', 'posix-awk', 'posix-basic',
                      'posix-egrep', 'posix-extended']
        }),
        Option('xdev', CHECKBOX_OPTION, '')
    ],
    'Name' : [
        Option('ilname', PATH_INPUT_OPTION, ''),
        Option('iname', PATH_INPUT_OPTION, ''),
        Option('iregex', PATH_INPUT_OPTION, ''),
        Option('iwholename', PATH_INPUT_OPTION, ''),
        Option('lname', PATH_INPUT_OPTION, ''),
        Option('name', PATH_INPUT_OPTION, ''),
        Option('path', PATH_INPUT_OPTION, ''),
        Option('regex', PATH_INPUT_OPTION, ''),
        Option('samefile', PATH_INPUT_OPTION, '')
    ],
    'Perm' : [
        Option('executable', CHECKBOX_OPTION, ''),
        Option('gid', INT_INPUT_OPTION, ''),
        Option('group', TEXT_INPUT_OPTION, ''),
        Option('nogroup', CHECKBOX_OPTION, ''),
        Option('nouser', CHECKBOX_OPTION, ''),
        Option('perm', TEXT_INPUT_OPTION, ''),
        Option('readable', CHECKBOX_OPTION, ''),
        Option('uid', INT_INPUT_OPTION, ''),
        Option('user', TEXT_INPUT_OPTION, ''),
        Option('writable', CHECKBOX_OPTION, '')
    ],
    'Size' : [
        Option('empty', CHECKBOX_OPTION, ''),
        Option('size', TEXT_INPUT_OPTION, '')
    ],
    'Time' : [
        Option('amin', INT_INPUT_OPTION, ''),
        Option('anewer', PATH_INPUT_OPTION, ''),
        Option('atime', INT_INPUT_OPTION, ''),
        Option('cmin', INT_INPUT_OPTION, ''),
        Option('cnewer', PATH_INPUT_OPTION, ''),
        Option('ctime', INT_INPUT_OPTION, ''),
        Option('mmin', INT_INPUT_OPTION, ''),
        Option('mtime', INT_INPUT_OPTION, ''),
        Option('newer', PATH_INPUT_OPTION, ''),
        Option('used', INT_INPUT_OPTION, '')
    ],
    'Type' : [
        Option('fstype', TEXT_INPUT_OPTION, 'test_opt_radio_button_changed_clear2fafafafafafafafaf'),
        Option('type', RADIO_BUTTON_OPTION, 'aaaaaaaaaaaaafafasfasffffffffffffffffffffffffffffffff', {
            'type' : ['b', 'c', 'd', 'p', 'f', 'l', 's', 'D']
        }),
        Option('xtype', RADIO_BUTTON_OPTION, '', {
            'type' : ['b', 'c', 'd', 'p', 'f', 'l', 's', 'D']
        })
    ],
    'Others' : [
        Option('inum', INT_INPUT_OPTION, ''),
        Option('links', INT_INPUT_OPTION, ''),
        Option('true', CHECKBOX_OPTION, ''),
        Option('false', CHECKBOX_OPTION, '')
    ],
    'Actions' : [
        Option('delete', CHECKBOX_OPTION, ''),
        Option('exec', TEXT_INPUT_OPTION, ''),
        Option('execdir', TEXT_INPUT_OPTION, ''),
        Option('fls', PATH_INPUT_OPTION, ''),
        Option('fprint', PATH_INPUT_OPTION, ''),
        Option('fprint0', PATH_INPUT_OPTION, ''),
        Option('fprintf', PATH_INPUT_OPTION, ''),
        Option('ls', TEXT_INPUT_OPTION, ''),
        Option('ok', TEXT_INPUT_OPTION, ''),
        Option('okdir', TEXT_INPUT_OPTION, ''),
        Option('print', CHECKBOX_OPTION, ''),
        Option('print0', CHECKBOX_OPTION, ''),
        Option('printf', TEXT_INPUT_OPTION, ''),
        Option('prune', CHECKBOX_OPTION, ''),
        Option('quit', CHECKBOX_OPTION, '')
    ]
}

MENUS = [k for k in OPTIONS]

