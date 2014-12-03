# Verify that all dependencies have been installed
#
#  Required:
#   -> Python 2.7+ or Python 3.3+
#   -> pyparsing
#

from __future__ import print_function

import subprocess
import os
import sys
import distutils.spawn


def set_environment() :
    """Updates local PATH and PYTHONPATH to include additional component directories."""
    # Set PATH environment
    PATH = os.environ.get('PATH', [])
    if PATH :
        PATH = [PATH]
    PATH = os.pathsep.join( PATH + list(get_binary_paths()) )
    os.environ['PATH'] = PATH
    
    # Set PYTHONPATH environment
    sys.path += get_module_paths()
    
def get_binary_paths() :
    """Get a list of additional binary search paths."""
    binary_root = os.path.join(os.path.dirname(__file__), 'bin' )
    system = os.uname()[0].lower()  # Darwin, Linux, ?    
    return list(map(os.path.abspath,[ os.path.join(binary_root, system), binary_root ]))
    
def get_module_paths() :
    """Get a list of additional module search paths."""    
    binary_root = os.path.join(os.path.dirname(__file__), 'lib' )
    system = os.uname()[0].lower()  # Darwin, Linux, ?    
    python = 'python%s' % sys.version_info.major
    return list(map(os.path.abspath,[ os.path.join(binary_root, python, system), os.path.join(binary_root, python), binary_root ]))
    

def gather_info() :
    """Collect info about the system and its installed software."""
    
    system_info = {}
    
    system_info['root_path'] = os.path.join(os.path.dirname(__file__), '..')
    
    system_info['os'] = os.uname()[0]
    system_info['arch'] = os.uname()[-1]
    
    system_info['python_version'] = sys.version_info
    
    # Module pyparsing
    try :
        import pyparsing
        system_info['pyparsing'] = pyparsing.__version__
    except ImportError :
        pass

    # Yap
    try :
        test_program =  "prolog_flag(version,V), write(V), nl, (prolog_flag(system_options,tabling) -> write(1) ; write(0)), nl, halt."
        with open(os.devnull, 'w') as OUT_NULL :
            output = subprocess.check_output( ['yap', '-g', test_program ], stderr=OUT_NULL ).decode('utf-8').split('\n')
        system_info['yap_version'] = output[0].split()[1]
        system_info['yap_tabling'] = output[1].strip() == "1"
    except Exception :
        pass
        
    # SDD module
    try :
        import sdd
        system_info['sdd_module'] = True
    except ImportError :
        pass
        
    # DSharp
    system_info['dsharp'] = distutils.spawn.find_executable('dsharp') != None
    
    # c2d
    system_info['c2d'] = distutils.spawn.find_executable('cnf2dDNNF') != None
    return system_info

def build_sdd() :
    
    build_lib = get_module_paths()[0]
    build_dir = get_module_paths()[-1]
    
    lib_dir = os.path.abspath(os.path.join(build_dir, 'sdd', os.uname()[0].lower()))
    
    curr = os.curdir
    os.chdir(build_dir)
    
    from distutils.core import setup, Extension
    sdd_module = Extension('_sdd', sources=['sdd/sdd_wrap.c'], libraries=['sdd'], library_dirs=[lib_dir] )

    setup (name = 'sdd',
           version = '1.0',
           author      = "",
           description = """SDD Library""",
           ext_modules = [sdd_module],
           py_modules = ["sdd"],
           script_name = '',
           script_args = ['build_ext', '--build-lib', build_lib, '--rpath', lib_dir ]
    )
    
    os.chdir(curr)

def install() :
    info = gather_info()
    update = False
    
    if not info.get('sdd_module') :
        build_sdd()
        update = True
        
    if update :
        info = gather_info()    
    return info    
    
def system_info() :
    info = gather_info()
    
    ok = True
    s  = 'System information:\n'
    s += '------------------:\n'
    s += 'Operating system: %s\n' % info.get('os','unknown')
    s += 'System architecture: %s\n' % info.get('arch', 'unknown') 
    s += 'Python version: %s.%s.%s\n' % ( info['python_version'].major, info['python_version'].minor, info['python_version'].micro )
    s += '\n'
    s += 'ProbLog components:\n'
    s += '-------------------\n'
    

    # PrologFile, PrologString  => require pyparsing
    # SDD => requires sdd_library
    # NNF => requires dsharp or c2d
    
    # SemiringOther => requires NNF (or SDD with alternative evaluation)
    
    # pyparsing = info.get('pyparsing', 'NOT INSTALLED')
    # s += 'Module \'pyparsing\': %s\n' % pyparsing
    # if not pyparsing :
    #     s += '  ACTION: install the pyparsing module\n'
    # sdd = info.get('sdd_module', False)
    # if sdd :
    #     s += 'Module \'sdd\': INSTALLED\n'
    # else :
    #     s += 'Module \'sdd\': NOT INSTALLED\n'
    #     s += '  ACTION: run ProbLog installer\n'
    #
    return s

if __name__ == '__main__' :
    set_environment()
    info = install()
    print (info)
    