## Underlay. OSPF

## Цель
Настроить OSPF для Underlay сети.

## Описание/Пошаговая инструкция выполнения домашнего задания:
1. Настроить OSPF в Underlay сети, для IP связанности между всеми сетевыми устройствами.
2. Зафиксировать в документации - план работы, адресное пространство, схему сети, конфигурацию устройств.
3. Убедиться в наличии IP связанности между устройствами в OSFP домене.

## Топология
Используем топологию и адресное пространство из предыдущего задания:
![](../lab01/lab1-topology.png)

## Настройка OSPF
Для запуска OSPF на каждом устройстве достаточно сделать следующее:
1. Включить маршрутизацию: ```ip routing```
2. Включить процесс OSPF: ```router ospf 1```
3. Указать минимальные настройки для интерфейсов p2p: ```ip ospf area 0```  ```ip ospf network point-to-point```
4. Указать минимальные настройки для инетрфейсов loopback: ```ip ospf area 0``` 

## Автоматизация настроек
В скрипт [listswitches.py](../lab01/listswitches.py) из предыдущего задания была добавлена обработка конфигурации ospf. В файл конфигурации [lab2.yaml](lab2.yaml) помимо настроек ip-адресов из предыдущего задания были добавлены настройки ospf. Все настройки однотипные, ниже пример для leaf1:
```
leaf1:
  ip_routing: yes
  ospf: 1
  interfaces:
    Lo0:
      ip: 10.73.0.101/32
      description: "leaf1 loopback"
      ospf_area: 0
    Et1:
      ip: 10.73.1.0/31
      description: "leaf1 to spine1"
      ospf_area: 0
      ospf_network: point-to-point
    Et2:
      ip: 10.73.2.0/31
      description: "leaf1 to spine2"
      ospf_area: 0
      ospf_network: point-to-point
    Et3:
      ip: 10.73.3.0/31
      description: "leaf1 to spine3"
      ospf_area: 0
      ospf_network: point-to-point
```
Демонстрация применения конфига:
```
jst@evelab:~/otus-labs/lab02$ ../lab01/listswitches.py config lab2.yaml
found telnet ports [32769, 32770, 32771, 32772, 32773, 32774, 32775, 32776]
port 32769 hostname spine1 time 0.321
port 32770 hostname spine2 time 0.333
port 32771 hostname spine3 time 0.322
port 32772 hostname leaf1 time 0.318
port 32773 hostname leaf2 time 0.319
port 32774 hostname leaf3 time 0.321
port 32775 hostname leaf4 time 0.322
port 32776 hostname leaf5 time 0.334
will apply config to node at 32769:
{'ip_routing': True, 'ospf': 1, 'interfaces': {'Lo0': {'ip': '10.73.1.100/32', 'description': 'spine1 loopback', 'ospf_area': 0}, 'Et1': {'ip': '10.73.1.1/31', 'description': 'spine1 to leaf1', 'ospf_area': 0, 'ospf_network': 'point-to-point'}, 'Et2': {'ip': '10.73.1.3/31', 'description': 'spine1 to leaf2', 'ospf_area': 0, 'ospf_network': 'point-to-point'}, 'Et3': {'ip': '10.73.1.5/31', 'description': 'spine1 to leaf3', 'ospf_area': 0, 'ospf_network': 'point-to-point'}, 'Et4': {'ip': '10.73.1.7/31', 'description': 'spine1 to leaf4', 'ospf_area': 0, 'ospf_network': 'point-to-point'}, 'Et5': {'ip': '10.73.1.9/31', 'description': 'spine1 to leaf5', 'ospf_area': 0, 'ospf_network': 'point-to-point'}}}

Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.

spine1#ena
ena
spine1#conf t
conf t
spine1(config)#ip routing
ip routing
spine1(config)#router ospf 1
router ospf 1
spine1(config-router-ospf)#exit
exit
spine1(config)#interface Lo0
interface Lo0
spine1(config-if-Lo0)#no switchport
no switchport
% Incomplete command
spine1(config-if-Lo0)#ip address 10.73.1.100/32
ip address 10.73.1.100/32
spine1(config-if-Lo0)#description spine1 loopback
description spine1 loopback
spine1(config-if-Lo0)#ip ospf area 0
ip ospf area 0
spine1(config-if-Lo0)#exit
exit
spine1(config)#interface Et1
interface Et1
spine1(config-if-Et1)#no switchport
no switchport
spine1(config-if-Et1)#ip address 10.73.1.1/31
ip address 10.73.1.1/31
spine1(config-if-Et1)#description spine1 to leaf1
description spine1 to leaf1
spine1(config-if-Et1)#ip ospf area 0
ip ospf area 0
spine1(config-if-Et1)#ip ospf network point-to-point
ip ospf network point-to-point
spine1(config-if-Et1)#exit
exit
spine1(config)#interface Et2
interface Et2
spine1(config-if-Et2)#no switchport
no switchport
spine1(config-if-Et2)#ip address 10.73.1.3/31
ip address 10.73.1.3/31
spine1(config-if-Et2)#description spine1 to leaf2
description spine1 to leaf2
spine1(config-if-Et2)#ip ospf area 0
ip ospf area 0
spine1(config-if-Et2)#ip ospf network point-to-point
ip ospf network point-to-point
spine1(config-if-Et2)#exit
exit
spine1(config)#interface Et3
interface Et3
spine1(config-if-Et3)#no switchport
no switchport
spine1(config-if-Et3)#ip address 10.73.1.5/31
ip address 10.73.1.5/31
spine1(config-if-Et3)#description spine1 to leaf3
description spine1 to leaf3
spine1(config-if-Et3)#ip ospf area 0
ip ospf area 0
spine1(config-if-Et3)#ip ospf network point-to-point
ip ospf network point-to-point
spine1(config-if-Et3)#exit
exit
....... и так далее для всех интерфейсов всех устройств .......
```
## Проверка связности
Для автоматизации проверки связности между всеми устройствами в скрипт [listswitches.py](../lab01/listswitches.py) была добавлена функция test.
 - cначала для каждого устройства определяется адрес интерфейса Lo0
 - затем выполняется пинг каждого устройства с каждого устройства
Скрипт строит матрицу связности и выводит ее в формате markdown для удобства вставки сюда.
Процесс:
```
jst@evelab:~/otus-labs/lab02$ ../lab01/listswitches.py test
found telnet ports [32769, 32770, 32771, 32772, 32773, 32774, 32775, 32776]
port 32769 hostname spine1 address 10.73.1.100 time 0.312
port 32770 hostname spine2 address 10.73.2.100 time 0.34
port 32771 hostname spine3 address 10.73.3.100 time 0.317
port 32772 hostname leaf1 address 10.73.0.101 time 0.315
port 32773 hostname leaf2 address 10.73.0.102 time 0.323
port 32774 hostname leaf3 address 10.73.0.103 time 0.273
port 32775 hostname leaf4 address 10.73.0.104 time 0.322
port 32776 hostname leaf5 address 10.73.0.105 time 0.29
ping 32769 10.73.1.100 result 0.10 ms
ping 32769 10.73.2.100 result 9.97 ms
ping 32769 10.73.3.100 result 10.40 ms
ping 32769 10.73.0.101 result 5.51 ms
..... остальные 60 строк удалены .....
```
Результат:
| src \ dst | spine1 | spine2 | spine3 | leaf1 | leaf2 | leaf3 | leaf4 | leaf5 |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| spine1 | 0.10 ms | 9.97 ms | 10.40 ms | 5.51 ms | 4.57 ms | 5.15 ms | 5.63 ms | 5.16 ms |
| spine2 | 14.14 ms | 0.07 ms | 9.20 ms | 7.80 ms | 4.82 ms | 12.13 ms | 6.62 ms | 6.02 ms |
| spine3 | 10.40 ms | 10.22 ms | 0.07 ms | 4.89 ms | 5.35 ms | 4.43 ms | 4.53 ms | 4.38 ms |
| leaf1 | 7.96 ms | 5.07 ms | 5.92 ms | 0.06 ms | 11.67 ms | 9.30 ms | 12.15 ms | 9.24 ms |
| leaf2 | 5.11 ms | 4.93 ms | 5.02 ms | 10.99 ms | 0.05 ms | 8.63 ms | 9.19 ms | 14.54 ms |
| leaf3 | 6.08 ms | 5.69 ms | 4.58 ms | 11.23 ms | 8.96 ms | 0.05 ms | 8.85 ms | 9.55 ms |
| leaf4 | 4.45 ms | 5.51 ms | 5.86 ms | 11.21 ms | 9.39 ms | 11.08 ms | 0.08 ms | 9.44 ms |
| leaf5 | 4.45 ms | 4.85 ms | 5.87 ms | 9.03 ms | 9.84 ms | 9.73 ms | 8.87 ms | 0.04 ms |
