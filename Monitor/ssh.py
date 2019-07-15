#!/usr/bin/python3
#-*- coding: utf-8 -*-
import paramiko


def ssh(host, username, pw, cmd='qstat'):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, 22, username, pw, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read())
        print('%s OK\n' % host)
        ssh.close()
    except :
        print('%s Error\n' % host)


if __name__ == '__main__':
    host = 'rigi'
    username = 'shch'
    pw = 'csf0223'
    ssh(host, username, pw)
