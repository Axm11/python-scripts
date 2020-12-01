#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# howToUse: ./createZabbixHost.py  /path/to/hosts
# https://www.zabbix.com/documentation/4.0/zh/manual/api

from pyzabbix import ZabbixAPI
from sys import argv
import random

class CreateHost():
    def __init__(self):
        self.zabUrl = 'http://192.168.10.10/zabbix'
        self.zabUser = 'Admin'
        self.zabPass = 'zabbix'
        self.proxyName = ('zabbix_proxy01', 'zabbix_proxy02')    #若没有代理则注释该行，多个代理情况下为随机选取其中一个
        self.templateName = 'LinuxTemplate'
        self.groupsName = 'LinuxGroup'

    def loginZab(self):
        zapi = ZabbixAPI(self.zabUrl)
        zapi.session.auth = (self.zabUser, self.zabPass)
        zapi.session.verify = False
        zapi.timeout = 30
        # Login (in case of HTTP Auth, only the username is needed, the password, if passed, will be ignored)
        zapi.login(self.zabUser, self.zabPass)
        return zapi

    #随机选取一个proxy进行批量添加主机
    def getZabProxy(self):
        zapi = self.loginZab()
        # proxyId = [ p['proxyid'] for p in zapi.proxy.get() if p['host'] in self.proxyName ]
        proxyId = zapi.proxy.get(filter={"host": self.proxyName})
        proxyId = [ h['proxyid'] for h in proxyId ]
        return random.choice(proxyId)

    #暂为只绑定一个主机模板，若有需求可修改
    def getZabTemplate(self):
        zapi = self.loginZab()
        templateId = zapi.template.get(filter={"host": self.templateName}, limit=1)
        return templateId[0]['templateid']

    def getZabGroup(self):
        zapi = self.loginZab()
        groupId = zapi.hostgroup.get(filter={"name": self.groupsName})
        return groupId[0]['groupid']

    def creZabHost(self):
        zapi = self.loginZab()
        with open(argv[1]) as files:
            hostInfo = [ f.strip() for f in files.readlines() ]
        for primaryIp in hostInfo:
            createData = {
                "host": primaryIp,
                "interfaces": [
                    {
                        "type": 1,       #接口类型：1.agent,2.snmp,3.ipmi,4.jmx
                        "main": 1,       #是否为默认接口,0表示否
                        "useip": 1,      #是否允许通过ip进行连接，0表示使用主机DNS名称连接
                        "ip": primaryIp,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": self.getZabGroup()
                    }
                ],
                "templates": [
                    {
                        "templateid": self.getZabTemplate()
                    }
                ],
                # "inventory_mode": 0,        #主机资产清单模式：1.自动，0.手动(默认),-1.禁用
                "proxy_hostid": self.getZabProxy()
            }
            print(createData)
            zapi.host.create(createData)

if __name__ == '__main__':
    CreateHost().creZabHost()