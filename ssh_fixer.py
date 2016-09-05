import os, subprocess, sys, re, stat

from storm.parsers import ssh_config_parser
import pexpect


config = ssh_config_parser.ConfigParser()
config_dict = config.load()

def test_ssh(host_title):
  command_line = 'ssh {host_title} exit'.format(host_title=host_title)

  try:
    proc = pexpect.spawn(command_line)
    proc.expect('Are you sure you want to continue connecting (yes/no)?')
    proc.sendline('yes')
  except pexpect.exceptions.EOF:
    pass
  proc.close()
  output_text = re.sub('Permission denied \(publickey\).', '', proc.before).strip()
  if output_text:
    print output_text
  return proc.exitstatus == 0

def test_filenames(dirname, filenames):
  for filename in filenames:
    if filename.startswith('.') or filename in {'known_hosts', 'config'}:
      continue
    path = os.path.join(dirname, filename)
    with open(path) as f:
      text = f.read()
    if not text.startswith('-----BEGIN RSA PRIVATE KEY-----'):
      continue
    # print 'perms:', oct(os.stat(path)[stat.ST_MODE])[-3:]
    os.chmod(path, 0o600)
    path = re.sub('^' + os.path.expanduser('~'), '~', path)
    print '  trying key:', path
    config.update_host(host_title, options={'identityfile': [path]})
    config.write_to_ssh_config()
    if test_ssh(host_title):
      print '  there we go'
      break

for host_dict in config_dict:
  host_title = host_dict['host']
  print 'testing:', host_title
  if test_ssh(host_title):
    print '  working'
    continue
  print '  not working'

  for dirname, dirnames, filenames in os.walk(os.path.expanduser('~/.ssh')):
    test_filenames(dirname, filenames)
  else:
    print '  none of the keys worked :('
