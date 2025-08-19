#!/usr/bin/env python3
import subprocess
import pexpect
import re
import time
import sys
import yaml

def get_telnet_ports():
  result = subprocess.check_output(
    ["sudo", "netstat", "-tnlp"], text=True
  )
  ports = []
  for line in result.splitlines():
    if "qemu" in line and "LISTEN" in line:
#      print(line)
      m = re.search(r":(\d{5,})\b", line)
      if m:
        ports.append(int(m.group(1)))
  return sorted(ports)

def get_hostname(port):
  start = time.time()
  child = pexpect.spawn(f"telnet 127.0.0.1 {port}", encoding="utf-8", timeout=5)
#  child.logfile = sys.stdout
  try:
    child.sendline("")
    i = child.expect([r"login:", r"Username:", r">", r"#"])
    if i in [0,1]:
      child.sendline("admin")
      child.expect([r">", r"#"])
    child.sendline("show hostname")
    child.expect([r">", r"#"])
    output = child.before
    m = re.search(r"Hostname:\s+(\S+)", output)
    hostname = m.group(1) if m else "UNKNOWN"
  except pexpect.TIMEOUT:
    hostname = "TIMEOUT"
  finally:
    child.close()
  elapsed = time.time() - start
  return hostname, round(elapsed, 3)

def get_ports_hostnames(ports):
  host_ports={}
  for port in ports:
    hostname, t = get_hostname(port)
    print("port",port,"hostname",hostname,"time",t)
    if hostname and hostname not in ("UNKNOWN","TIMEOUT"):
      host_ports[hostname]=port
  return host_ports

def configure_node(port,config):
  print(f"will apply config to node at {port}:")
  print(config)
  start = time.time()
  child = pexpect.spawn(f"telnet 127.0.0.1 {port}", encoding="utf-8", timeout=10)
  child.logfile = sys.stdout
  try:
    child.sendline("")
    i = child.expect([r"login:", r"Username:", r">", r"#"])
    if i in [0,1]:
      child.sendline("admin")
      child.expect([r">", r"#"])
    child.sendline("ena")
    child.expect([r">", r"#"])
    child.sendline("conf t")
    child.expect(r"\(config\)#")
    for iface, cfg in config.get("interfaces", {}).items():
      child.sendline(f"interface {iface}")
      child.expect(r"\(config-if(?:-[^)]+)?\)#")
      child.sendline("no switchport")
      child.expect(r"\(config-if(?:-[^)]+)?\)#")
      if "ip" in cfg:
        child.sendline(f"ip address {cfg['ip']}")
        child.expect(r"\(config-if(?:-[^)]+)?\)#")
      if "description" in cfg:
        child.sendline(f"description {cfg['description']}")
        child.expect(r"\(config-if(?:-[^)]+)?\)#")
      child.sendline("exit")
      child.expect(r"\(config\)#")
    child.sendline("wr mem")
    child.expect([r">", r"#"])
    child.sendline("exit")
  except pexpect.TIMEOUT:
    print("TIMEOUT")
  finally:
    child.close()
    elapsed = round(time.time() - start,3)
    print(f"=== config of {port} took {elapsed} seconds")

def main():
  args = sys.argv[1:]
  ports=get_telnet_ports()
  print("found telnet ports",ports)
  if not args:
    get_ports_hostnames(ports)
    return

  if args[0]=="hostname":
    if len(args)!=3:
      print("Usage: listswitches.py hostname <port> <hostname>")
      sys.exit(1)
    port=int(args[1])
    new_name=args[2]
    print(f"will set {new_name} on {port}")
    start = time.time()
    child = pexpect.spawn(f"telnet 127.0.0.1 {port}", encoding="utf-8", timeout=10)
    child.logfile = sys.stdout
    try:
      child.sendline("")
      i = child.expect([r"login:", r"Username:", r">", r"#"])
      if i in [0,1]:
        child.sendline("admin")
        child.expect([r">", r"#"])
      child.sendline("ena")
      child.expect([r">", r"#"])
      child.sendline("conf t")
      child.expect(r"\(config\)#")
      child.sendline(f"hostname {new_name}")
      child.expect(r"\(config\)#")
      child.sendline("wr mem")
      child.expect([r">", r"#"])
      child.sendline("exit")
    except pexpect.TIMEOUT:
      print("TIMEOUT")
    finally:
      child.close()
      elapsed = round(time.time() - start,3)
      print(f"===== done, took {elapsed} seconds")
    return

  if args[0]=="config":
    if len(args) != 2:
      print("Usage: listswitches.py config <file.yaml>")
      sys.exit(1)
    cstart = time.time()
    yamlname = args[1]
    host_ports = get_ports_hostnames(ports)
    with open(yamlname) as f:
      plan = yaml.safe_load(f)
    for host, cfg in plan.items():
      port = host_ports.get(host)
      if port:
        configure_node(port, cfg)
      else:
        print(f"Warning: host {host} not found in yaml")
    celapsed = round(time.time() - cstart,3)
    print(f"======= all done, took {celapsed} seconds")
    return

  print("Unknown command")
  sys.exit(1)

if __name__ == "__main__":
  main()
