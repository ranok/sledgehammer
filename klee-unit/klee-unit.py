#!/usr/bin/env python

#########################################################################################
# KLEE-Unit
# Author: Jacob Torrey
# Date: 3/15/2016
#
# Script to auto-generate test harness and execute symbolically with KLEE for a passed C
# file
#########################################################################################

import sys
import os
import shutil
import re
import subprocess
from pycparser import c_parser, c_ast
from ctags import CTags, TagEntry

def collect_klee_runs():
    '''Navigates all KLEE output directories and performs basic triage'''

def run_klee(filename):
    '''Runs KLEE on a given file'''
    return subprocess.call(['klee', '--libc=uclibc', '--posix-runtime', filename])

def generate_c(filename, func):
    '''Generates a test harness and temp C file for a passed function'''
    # Copy to duplicate safe to trash
    newfn = filename[:-2] + "_" + func[0] + '.c'
    shutil.copyfile(filename, newfn)

    # Rename main() to something not conflicting
    f = open(newfn, 'r')
    c = f.read()
    f.close()
    c = re.sub(r' main\s?\(', ' not_main(', c)
    c = c + "\r\n\r\n"

    # Generate our own main() using symbolic variables for every function argument
    main = "int main(int argc, char **argv) {\r\n"
    i = 0
    fc = func[0] + "("
    for f in func[1][1]:
        vn = 'var' + str(i)
        fc += vn + ", "
        vl = f + " " + vn + ";\r\n"
        vl += "klee_make_symbolic(&" + vn + ", sizeof(" + f + "), \"" + vn + "\");\r\n"
        i += 1
        main += vl
    fc = fc[:-2] + ");\r\n"
    main += fc
    main += "return 0;\r\n}\r\n"
    c += main
    # Inject into temp file
    f = open(newfn, 'w')
    f.write(c)
    f.close()

    # Return temp file name
    return newfn

def compile_c(filename, outname = 'kleeunit.bc'):
    '''Compiles for execution with KLEE'''
    ret = subprocess.call(['clang', '-g', '-emit-llvm', '-c', filename, '-o', outname])
    #os.remove(filename)
    return ret

def run_ctags(filename):
    '''Executes the ctags command on the passed filename to generate the tags file'''
    return subprocess.call(['ctags', filename])

def parse_pattern(pattern):
    '''Parses a ctags pattern string'''
    pattern = pattern[2:-2] + ";"
    parser = c_parser.CParser()
    try:
        node = parser.parse(pattern, filename = '<stdin>')
    except c_parser.ParseError:
        print "Unable to parse pattern: " + pattern
        sys.exit(-1)
    return (node.ext[-1].name, _explain_type(node.ext[-1])) 
    
def _explain_type(decl):
    '''Recursively explains a type decl node'''
    typ = type(decl)
    
    if typ == c_ast.TypeDecl:
        quals = ' '.join(decl.quals) + ' ' if decl.quals else ''
        return quals + _explain_type(decl.type)
    elif typ == c_ast.Typename or typ == c_ast.Decl:
        return _explain_type(decl.type)
    elif typ == c_ast.IdentifierType:
        return ' '.join(decl.names)
    elif typ == c_ast.PtrDecl:
        quals = ' '.join(decl.quals) + ' ' if decl.quals else ''
        return quals + _explain_type(decl.type) + "*"
    elif typ == c_ast.ArrayDecl:
        arr = 'array'
        if decl.dim: arr += '[%s]' % decl.dim.value
        
        return arr + " of " + _explain_type(decl.type)
    
    elif typ == c_ast.FuncDecl:
        if decl.args:
            params = [_explain_type(param) for param in decl.args.params]
        else:
            params = []
        return [_explain_type(decl.type), params]

def parse_ctags():
    '''Returns a list of all the functions and their arguments found by ctags'''
    try:
        tf = CTags('tags')
    except:
        print "Unable to find tags file!"
        sys.exit(-1)
    entry = TagEntry()
    l = []
    if 0 == tf.first(entry):
        return []
    while True:
        l.append(parse_pattern(entry['pattern']))
        if 0 == tf.next(entry):
            break
    return l

def controller():
    '''Main handler that dispatches calls for KLEE-unit'''
    if len(sys.argv) != 2:
        print "KLEE-Unit: Usage: " + sys.argv[0] + " file_to_analyze.c"
        sys.exit(-1)
    filename = sys.argv[1]
    run_ctags(filename)
    funcs = parse_ctags()

    for f in funcs:
        if f[0] == 'main':
            continue
        fn = generate_c(filename, f)
        compile_c(fn, fn + '.bc')
        run_klee(fn + '.bc')

    collect_klee_runs()
        
if __name__ == "__main__":
    controller()
