from __future__ import print_function

import os
import re
import stat
import subprocess
import sys

import pexpect
from storm.parsers import ssh_config_parser

config = ssh_config_parser.ConfigParser()
config_dict = config.load()

print(config_dict)

def test_ssh(host_title):
  if host_title is not None:
    command_line = 'ssh {} exit'.format(host_title)
  else:
    return False

  try:
    proc = pexpect.spawn(command_line)
    proc.expect('Are you sure you want to continue connecting (yes/no)?')
    proc.sendline('yes')
  except pexpect.exceptions.EOF:
    pass
  proc.close()
  output_text = re.sub('Permission denied \(publickey\).', '', proc.before).strip()
  if output_text:
    print(output_text)
  return proc.exitstatus == 0

def test_filenames(dirname, filenames):
  for filename in filenames:
    if filename == 'known_hosts':
      continue
    path = os.path.join(dirname, filename)
    with open(path) as f:
      text = f.read()
    if not re.match('-----BEGIN .* PRIVATE KEY-----', text):
      continue
    os.chmod(path, 0o600)
    path = re.sub('^' + os.path.expanduser('~'), '~', path)
    print('  trying key:', path)
    config.update_host(host_title, options={'identityfile': [path]})
    config.write_to_ssh_config()
    if test_ssh(host_title):
      print('  there we go')
      break

for host_dict in config_dict:
  if host_dict['type'] != 'comment' and host_dict['type'] != 'empty_line':
    host_title = host_dict['host'].split()[0]
  else:
    continue
  print('testing:', host_title)
  if test_ssh(host_title):
    print('  working')
    continue
  print('  not working')

  for dirname, dirnames, filenames in os.walk(os.path.expanduser('~/.ssh')):
    test_filenames(dirname, filenames)
  else:
    print('  none of the keys worked :(')
