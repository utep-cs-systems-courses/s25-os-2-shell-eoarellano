#!/usr/bin/env python3

import os
import sys

def main():
    while 1:
        ps1 = os.environ.get('PS1', '$ ')
        sys.stdout.write(ps1)
        sys.stdout.flush()

        cmd = get_input()
        if not cmd:
            continue
        cmds = cmd.split()
        execute_command(cmds)

def get_input():
    try:
        return input().strip()
    except EOFError:
        sys.exit(0)

def execute_command(cmds):

    if cmds[0] == 'exit':
        sys.exit(0)

    elif cmds[0] == 'ls':
        os.system('ls')
        return
    
    elif cmds[0] == 'cd':
        change_directory(cmds[1:])

    if '|' in cmds:
        execute_pipe(cmds)
    else:
        execute_program(cmds)

def  change_directory(cmds):
    try:
        new_dir = cmds[1] if len(cmds) > 1 else os.environ['HOME']
        os.chdir(new_dir)
    except FileNotFoundError:
        print(f"cd: {new_dir}: No such file or directory")
        
def execute_pipe(cmds):
    cmds = " ".join(cmds).split('|') #split the command by pipe
    cmds = [c.strip().split() for c in cmds] #remove leading and trailing whitespaces

    pipe_read, pipe_write = os.pipe()

    pid1 = os.fork()
    if pid1 == 0:
        os.dup2(pipe_write, sys.stdout.fileno())
        os.close(pipe_read)
        execute_program(cmds[0].split())
        sys.exit(0)
        
    pid2 = os.fork()
    if pid2 == 0:
        os.dup2(pipe_read, sys.stdin.fileno())
        os.close(pipe_write)
        execute_program(cmds[1].split())
        sys.exit(0)

    os.close(pipe_read)
    os.close(pipe_write)
    os.waitpid(pid1, 0)
    os.waitpid(pid2, 0)

def execute_program(cmds):
    pid = os.fork()

    if pid < 0:
        os.write(2, "fork failed".encode())
        sys.exit(1)
    elif pid == 0:
        for dir in os.environ['PATH'].split(':'):
            program = f"{dir}/{cmds[0]}"
            try:
                os.execve(program, cmds, os.environ)
            except FileNotFoundError:
                pass
        os.write(2, f"{cmds[0]}: command not found\n".encode())
        sys.exit(1)
    else:
        os.wait()

if __name__ == '__main__':
    main()