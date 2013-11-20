"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

"""
Utilities for dealing with C and C++ header files
"""

import os
import sys
import inspect


def _ctype2declaration(key, name):
    def get_arrays(rep):
        ## ctypes arrays are declared in reverse order to their C equivalent
        end = -1
        spec = ''
        while True:
            idx = rep.rfind('Array', 0, end)
            if idx < 0:
                break
            end = rep.find('_', idx+6)
            if end == -1:
                end = -2
            num = rep[idx+6:end]
            end = idx
            spec += '[' + num + ']'
        return spec
       
    if key == "<class 'ctypes.c_bool'>":
        return '_Bool ' + name
    elif key == "<class 'ctypes.c_char'>":
        return 'char ' + name
    elif key == "<class 'ctypes.c_wchar'>":
        return 'wchar_t ' + name
    elif key == "<class 'ctypes.c_byte'>":
        return 'char ' + name
    elif key == "<class 'ctypes.c_ubyte'>":
        return 'unsigned char ' + name
    elif key == "<class 'ctypes.c_short'>":
        return 'short ' + name
    elif key == "<class 'ctypes.c_ushort'>":
        return 'unsigned short ' + name
    elif key == "<class 'ctypes.c_int'>":
        return 'int ' + name
    elif key == "<class 'ctypes.c_uint'>":
        return 'unsigned int ' + name
    elif key == "<class 'ctypes.c_long'>":
        return 'long ' + name
    elif key == "<class 'ctypes.c_ulong'>":
        return 'unsigned long ' + name
    elif key == "<class 'ctypes.c_longlong'>":
        return 'long long ' + name
    elif key == "<class 'ctypes.c_ulonglong'>":
        return 'unsigned long long ' + name
    elif key == "<class 'ctypes.c_float'>":
        return 'float ' + name
    elif key == "<class 'ctypes.c_double'>":
        return 'double ' + name
    elif key == "<class 'ctypes.c_longdouble'>":
        return 'long double ' + name
    elif key == "<class 'ctypes.c_char_p'>":
        return 'char *' + name
    elif key == "<class 'ctypes.c_wchar_p'>":
        return 'wchar_t *' + name
    elif key == "<class 'ctypes.c_void_p'>":
        return 'void *' + name

    elif 'c_bool_Array' in key:
        return '_Bool ' + name + get_arrays(key)
    elif 'c_char_Array' in key:
        return 'char ' + name + get_arrays(key)
    elif 'c_wchar_Array' in key:
        return 'wchar_t ' + name + get_arrays(key)
    elif 'c_byte_Array' in key:
        return 'char ' + name + get_arrays(key)
    elif 'c_ubyte_Array' in key:
        return 'unsigned char ' + name + get_arrays(key)
    elif 'c_short_Array' in key:
        return 'short ' + name + get_arrays(key)
    elif 'c_ushort_Array' in key:
        return 'unsigned short ' + name + get_arrays(key)
    elif 'c_int_Array' in key:
        return 'int ' + name + get_arrays(key)
    elif 'c_uint_Array' in key:
        return 'unsigned int ' + name + get_arrays(key)
    elif 'c_long_Array' in key:
        return 'long ' + name + get_arrays(key)
    elif 'c_ulong_Array' in key:
        return 'unsigned long ' + name + get_arrays(key)
    elif 'c_longlong_Array' in key:
        return 'long long ' + name + get_arrays(key)
    elif 'c_ulonglong_Array' in key:
        return 'unsigned long long ' + name + get_arrays(key)
    elif 'c_float_Array' in key:
        return 'float ' + name + get_arrays(key)
    elif 'c_double_Array' in key:
        return 'double ' + name + get_arrays(key)
    elif 'c_longdouble_Array' in key:
        return 'long double ' + name + get_arrays(key)

    return key + ' ' + name


def _generate_header(filename, custom_types):
    hdr = open(filename, 'w')
    guard = os.path.basename(filename).replace('.', '_').upper()
    hdr.write('#ifndef ' + guard + '\n')
    hdr.write('#define ' + guard + '\n\n')
    for t in custom_types:
        hdr.write('struct ' + t.name + ' {\n')
        members = t._fields_
        for f in range(len(members)):
            field_id = members[f][0]
            full_type = repr(members[f][1])
            declaration = _ctype2declaration(full_type, field_id)
            comment = ''
            if hasattr(t, 'comments') and len(t.comments) <= f:
                comment = t.comments[f]
            hdr.write('  ' + declaration + ';')

            tablen = 3
            if len(declaration) > 20:
                tablen = 1
            elif len(declaration) > 12:
                tablen = 2
            if comment:
                hdr.write('\t' * tablen + comment)
            hdr.write('\n')
        hdr.write('};\n\n')
    hdr.write('#endif  // ' + guard + '\n')
    hdr.close()


def generate_module_header(module_path, target_path=None):
    def class_filter(member):
        return inspect.isclass and hasattr(member, '__module__') and \
            member.__module__ == modname
    modname = os.path.splitext(os.path.basename(module_path))[0]
    moddir = os.path.realpath(os.path.abspath(os.path.dirname(module_path)))
    if moddir not in sys.path:
        sys.path.insert(0, moddir)
    __import__(modname)
    module = sys.modules[modname]
    custom_types = [c for n, c in inspect.getmembers(module, class_filter)]
    if target_path is None:
        target_path = os.path.splitext(module_path)[0] + '.h'
    _generate_header(target_path, custom_types)


def generate_ctypes_header(argv=None):
    if argv is None:
        argv = sys.argv
    if not (len(argv) > 1 and len(argv) < 4):
        print('Usage: ' + os.path.basename(argv[0]) +
              ' <module> [<header>]')
        sys.exit()
    target = None
    if len(argv) > 2:
        target = argv[2]
    generate_module_header(argv[1], target)




def patch_c_only_header(filepath):
    orig = open(filepath, 'r')
    lines = orig.readlines()
    orig.close()
    shutil.move(filepath, filepath + '.orig')
    fixed = open(filepath, 'w')
    fixed.write('#ifdef __cplusplus\nextern "C" {\n#endif\n\n')
    for line in lines:
        fixed.write(line)
    fixed.write('\n#ifdef __cplusplus\n}\n#endif\n')
    fixed.close()



def get_header_version(hdr_file, define_val):
    '''
    Given a C header file and a define macro, extract a version string.
    '''
    f = open(hdr_file, 'r')
    for line in f:
        if define_val in line and '#define' in line:
            f.close()
            return line[line.rindex(define_val) + len(define_val):].strip()
    f.close()
    raise Exception('No version information (' + define_val +
                    ') in ' + hdr_file)




if __name__ == '__main__':
    generate_ctypes_header(sys.argv)
