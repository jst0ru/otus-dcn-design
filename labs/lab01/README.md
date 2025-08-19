## Проектирование адресного пространства

## Цели
 - Собрать схему CLOS;
 - Распределить адресное пространство.

## Описание/Пошаговая инструкция выполнения домашнего задания
1.  Соберете топологию CLOS.
2.  Распределите адресное пространство для Underlay сети.
3.  Зафиксируете в документации план работ, адресное пространство, схему сети, настройки.

## Топология
В эмуляторе EVE-NG CE была собрана следующая топология:
![](lab1-topology.png)

## Распределение адресов
Был выбран следующий шаблон адресации p2p-линков для underlay-сети:
|**10.73.s.l/31**|
|:-:|
 - 73 - код ЦОД 
 - _s_ - номер spine
 - _l_ - (номер leaf * 2) - 1 для spine и (номер leaf * 2) - 2 для leaf
 - /31 - префикс сети на 2 адреса

Таблица распределения адресов на портах устройств:

|Device1|Port|Address|Description|...|Device2|Port|Address|Description|
|--|--|--|--|--|--|--|--|--|
|spine1|Et1|10.73.1.1/31|spine1 to leaf1|...|leaf1|Et1|10.73.1.0/31|leaf1 to spine1|
|spine1|Et2|10.73.1.3/31|spine1 to leaf2|...|leaf2|Et1|10.73.1.2/31|leaf2 to spine1|
|spine1|Et3|10.73.1.5/31|spine1 to leaf3|...|leaf3|Et1|10.73.1.4/31|leaf3 to spine1|
|spine1|Et4|10.73.1.7/31|spine1 to leaf4|...|leaf4|Et1|10.73.1.6/31|leaf4 to spine1|
|spine1|Et5|10.73.1.9/31|spine1 to leaf5|...|leaf5|Et1|10.73.1.8/31|leaf5 to spine1|
|spine2|Et1|10.73.2.1/31|spine2 to leaf1|...|leaf1|Et1|10.73.2.0/31|leaf1 to spine2|
|spine2|Et2|10.73.2.3/31|spine2 to leaf2|...|leaf2|Et1|10.73.2.2/31|leaf2 to spine2|
|spine2|Et3|10.73.2.5/31|spine2 to leaf3|...|leaf3|Et1|10.73.2.4/31|leaf3 to spine2|
|spine2|Et4|10.73.2.7/31|spine2 to leaf4|...|leaf4|Et1|10.73.2.6/31|leaf4 to spine2|
|spine2|Et5|10.73.2.9/31|spine2 to leaf5|...|leaf5|Et1|10.73.2.8/31|leaf5 to spine2|
|spine3|Et1|10.73.3.1/31|spine3 to leaf1|...|leaf1|Et1|10.73.3.0/31|leaf1 to spine3|
|spine3|Et2|10.73.3.3/31|spine3 to leaf2|...|leaf2|Et1|10.73.3.2/31|leaf2 to spine3|
|spine3|Et3|10.73.3.5/31|spine3 to leaf3|...|leaf3|Et1|10.73.3.4/31|leaf3 to spine3|
|spine3|Et4|10.73.3.7/31|spine3 to leaf4|...|leaf4|Et1|10.73.3.6/31|leaf4 to spine3|
|spine3|Et5|10.73.3.9/31|spine3 to leaf5|...|leaf5|Et1|10.73.3.8/31|leaf5 to spine3|

## Автоматизация настроек
Не хотелось выполнять однотипную операцию 30 раз, поэтому для применения настроек был разработан скрипт [listswitches.py](listswitches.py).
Скрипт выполняет следующие функции на машине с eve-ng:
1. При запуске без параметров: поиск запущенных экземпляров quemu и их открытых портов telnet, логин  в каждый и определение hostname. Выполняется команда show hostname.
2. При запуске с параметром hostname: конфигурирование hostname для экземпляра, отвечающего на определенном порту. Выполняются команды: enable, conf t, hostname, wri mem.
3. При запуске c параметром config: конфигурирование интерфейсов согласно указанному файлу yaml с настройками. Выполняются команды: enable, conf t, interface, no switchport, ip address, description, exit, wri mem.

Ниже примеры запуска скрипта.

Список экземпляров:

```jst@evelab:~$ ./listswitches.py
[sudo] password for jst:
found telnet ports [32769, 32770, 32771, 32772, 32773, 32774, 32775, 32776]
port 32769 hostname spine1 time 0.343
port 32770 hostname spine2 time 0.34
port 32771 hostname spine3 time 0.326
port 32772 hostname leaf1 time 0.341
port 32773 hostname leaf2 time 0.353
port 32774 hostname leaf3 time 0.339
port 32775 hostname leaf4 time 0.341
port 32776 hostname localhost time 0.327
jst@evelab:~$```

Установка hostname:

```jst@evelab:~$ ./listswitches.py hostname 32776 leaf5
found telnet ports [32769, 32770, 32771, 32772, 32773, 32774, 32775, 32776]
will set leaf5 on 32776
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
localhost#ena
ena
localhost#conf t
conf t
localhost(config)#hostname leaf5
hostname leaf5
leaf5(config)#wr mem
wr mem
Copy completed successfully.
leaf5(config)#exit
===== done, took 0.999 seconds```
