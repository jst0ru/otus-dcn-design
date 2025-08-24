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

def get_lo0addr(port):
  child = pexpect.spawn(f"telnet 127.0.0.1 {port}", encoding="utf-8", timeout=5)
#  child.logfile = sys.stdout
  try:
    child.sendline("")
    i = child.expect([r"login:", r"Username:", r">", r"#"])
    if i in [0,1]:
      child.sendline("admin")
      child.expect([r">", r"#"])
    child.sendline("ena")
    child.expect([r">", r"#"])
    child.sendline("sho run int Lo0")
    child.expect([r">", r"#"])
    output = child.before
    m = re.search(r"ip address (\d+\.\d+\.\d+\.\d+)", output)
    addr = m.group(1) if m else "UNKNOWN"
  except pexpect.TIMEOUT:
    addr = "TIMEOUT"
  finally:
    child.close()
  return addr

def get_ports_hostnames(ports):
  host_ports={}
  for port in ports:
    hostname, t = get_hostname(port)
    print("port",port,"hostname",hostname,"time",t)
    if hostname and hostname not in ("UNKNOWN","TIMEOUT"):
      host_ports[hostname]=port
  return host_ports

def get_hosts_ports_addrs(ports):
  hosts={}
  for port in ports:
    hostname, t = get_hostname(port)
    address = get_lo0addr(port)
    print("port",port,"hostname",hostname,"address",address,"time",t)
    if hostname and hostname not in ("UNKNOWN","TIMEOUT"):
      if address and address not in ("UNKNOWN","TIMEOUT"):
        hosts[hostname]= {
          "port":port,
          "addr":address
        }
  return hosts

def test_avg_ping(source_port,dest_ip):
  child = pexpect.spawn(f"telnet 127.0.0.1 {source_port}", encoding="utf-8", timeout=5)
  #child.logfile = sys.stdout
  try:
    child.sendline("")
    i = child.expect([r"login:", r"Username:", r">", r"#"])
    if i in [0,1]:
      child.sendline("admin")
      child.expect([r">", r"#"])
    child.sendline(f"ping {dest_ip} repeat 5")
    child.expect([r">", r"#"])
    output = child.before
    m = re.search(r"= ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", output)
    if m:
      return float(m.group(2))
    else:
      return None
  except pexpect.TIMEOUT:
    return None
  finally:
    child.close()

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
    if "ip_routing" in config:
      if config['ip_routing']:
        child.sendline("ip routing")
      else:
        child.sendline("no ip routing")
      child.expect(r"\(config\)#")  
    if "ospf" in config:
      child.sendline(f"router ospf {config['ospf']}")
      child.expect(r"\(config-router-ospf\)#")  
      child.sendline("exit")
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
      if "ospf_area" in cfg:
        child.sendline(f"ip ospf area {cfg['ospf_area']}") 
        child.expect(r"\(config-if(?:-[^)]+)?\)#")
      if "ospf_network" in cfg:
        child.sendline(f"ip ospf network {cfg['ospf_network']}") 
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

  if args[0]=="test":
    hosts=get_hosts_ports_addrs(ports)
    hostnames=list(hosts.keys())
    header="| src \\ dst | " + " | ".join(hostnames) + " |"
    separator="|" + "-----------|" * (len(hostnames) + 1)
    rows=[header, separator]
    for src in hostnames:
      row=[src]
      src_port=hosts[src]["port"]
      for dst in hostnames:
        dst_ip=hosts[dst]["addr"]
        try:
          avg_rtt=test_avg_ping(src_port, dst_ip)
        except:
          avg_rtt=None
          pass  
        cell=f"{avg_rtt:.2f} ms" if avg_rtt is not None else "FAIL"
        print("ping",src_port, dst_ip,"result",cell)
        row.append(cell)
      rows.append("| " + " | ".join(row) + " |")
    table="\n".join(rows)
    print(table)
    return
    
#    for src,src_data in hosts.items():
#      for dst,dst_data in hosts.items():
#        print("will ping switch",dst,"addr",dst_data['addr'],"from switch",src,"port",src_data['port'])



  print("Unknown command")
  sys.exit(1)

if __name__ == "__main__":
  main()
