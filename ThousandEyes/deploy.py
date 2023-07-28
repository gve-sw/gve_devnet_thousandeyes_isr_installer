"""
Orchestration of Deploy
"""
import time
import xmltodict
from ncclient.operations import RPCError
from .verify import Verify
import sys
from paramiko import SSHClient
import paramiko


class Deploy:
    """
    Parameters
    ----------
    obj : object
        Thousandeyes Class Instance
    Returns
    -------
    bool
        If successful or failed
    """

    @staticmethod
    def hardware(obj):
        """ Check hardware on device """
        __filter = """
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <device-hardware-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-device-hardware-oper">
            <device-hardware>
                <device-inventory>
                <part-number>
                </part-number>
                </device-inventory>
            </device-hardware>
            </device-hardware-data>
        </filter>
        """
        data = xmltodict.parse(obj.device_api.get(filter=__filter))
        return Verify.hardware(data=data)

    @staticmethod
    def version(obj):
        """ Check version on device """
        __filter = """
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <install-oper-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-install-oper">
            <install-location-information>
            <install-version-state-info>
            <version>
            </version>
            </install-version-state-info>
            </install-location-information>
            </install-oper-data>
        </filter>
        """
        data = xmltodict.parse(obj.device_api.get(filter=__filter))
        return Verify.version(data=data)

    @staticmethod
    def iox(obj):
        """ Check IOX sevice on device """
        __filter = """
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <iox>
            </iox>
            </native>
        </filter>
        """
        data = xmltodict.parse(obj.device_api.get(filter=__filter))
        print(data)
        if Verify.iox(data=data) is False:
            config = """
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                <iox>
                </iox>
                </native>
            </config>
            """
            if obj.device_api.config(config=config) is True:
                # Wait until IOX is ready
                print("Waiting until IOX is ready...")
                time.sleep(300)
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def apps(obj):
        """ Check existing apps hosted on device """
        __filter = """
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <app-hosting-oper-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-app-hosting-oper">
            <app>
            </app>
            </app-hosting-oper-data>
        </filter>
        """
        data = xmltodict.parse(obj.device_api.get(filter=__filter))
        return Verify.apps(data=data)

    @staticmethod
    def install(obj):
        te_flash_url = f"flash:{obj.cfg.te_filename}"

        """ Install Thousand Eyes Agent on device """
        copy_rpc = f'<copy xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">\
    <source-drop-node-name>{obj.cfg.download_url}</source-drop-node-name>\
    <destination-drop-node-name>flash:</destination-drop-node-name>\
  </copy>'

        rpc = f"""<app-hosting xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">
            <install>
              <appid>{obj.cfg.appid}</appid>
              <package>flash:{obj.cfg.te_filename}</package>
            </install>
          </app-hosting>
        """
        data = xmltodict.parse(obj.device_api.rpc(rpc=copy_rpc))
        data = xmltodict.parse(obj.device_api.rpc(rpc=rpc))
        print(data)
        if Verify.app_status_deploy(data=data, appid=obj.cfg.appid) is True:
            max_retry = 10
            retry = 0
            while True:
                if Deploy.apps(obj) is False or retry == max_retry:
                    return True
                retry += 1
                time.sleep(15)
            return False
        else:
            return False

    @staticmethod
    def config(obj):
        """ Configure Thousand Eyes Agent on device """
        app_hosting_config = f"""
        <app-hosting-cfg-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-app-hosting-cfg">
            <apps>
                <app xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="replace">
                    <application-name>{obj.cfg.appid}</application-name>
                    <docker-resource>true</docker-resource>
                    <application-network-resource>
                        <vnic-gateway-0>0</vnic-gateway-0>
                        <virtualportgroup-guest-interface-name-1 nc:operation="replace">0</virtualportgroup-guest-interface-name-1>
                        <virtualportgroup-guest-ip-address-1>10.100.152.120</virtualportgroup-guest-ip-address-1>
                        <virtualportgroup-guest-ip-netmask-1>255.255.255.0</virtualportgroup-guest-ip-netmask-1>
                        <virtualportgroup-application-default-gateway-1>10.100.152.100</virtualportgroup-application-default-gateway-1>
                        <nameserver-0>8.8.8.8</nameserver-0>
                        <virtualportgroup-guest-interface-default-gateway-1>0</virtualportgroup-guest-interface-default-gateway-1>
                    </application-network-resource>
                    <run-optss>
                        <run-opts nc:operation="replace">
                            <line-index>1</line-index>
                            <line-run-opts nc:operation="replace">-e TEAGENT_ACCOUNT_TOKEN={obj.cfg.token}</line-run-opts>
                        </run-opts>
                        <run-opts nc:operation="merge">
                            <line-index>2</line-index>
                            <line-run-opts nc:operation="merge">--hostname Cisco-Docker</line-run-opts>
                        </run-opts>
                    </run-optss>
                    <prepend-pkg-opts>true</prepend-pkg-opts>
                    <start>true</start>
                </app>
            </apps>
        </app-hosting-cfg-data>
        """
        #TODO I removed the following line: <start>true</start>, if needed, add it back. The final step should call <start> so it shouldnt be needed
        nat_config = f"""
        <ios:native xmlns:ios="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <ios:ip>
                <ios-nat:nat xmlns:ios-nat="http://cisco.com/ns/yang/Cisco-IOS-XE-nat">
                    <ios-nat:inside>
                        <ios-nat:source>
                            <ios-nat:list>
                                <ios-nat:id>NAT</ios-nat:id>
                                <ios-nat:interface>
                                    <ios-nat:name>GigabitEthernet1</ios-nat:name>
                                    <ios-nat:overload/>
                                </ios-nat:interface>
                            </ios-nat:list>
                        </ios-nat:source>
                    </ios-nat:inside>
                </ios-nat:nat>
                <ios:access-list>
                    <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
                        <name>NAT</name>
                        <access-list-seq-rule>
                            <sequence>10</sequence>
                            <ace-rule>
                                <action>permit</action>
                                <protocol>ip</protocol>
                                <ipv4-address>10.100.152.0</ipv4-address>
                                <mask>0.0.0.255</mask>
                                <dst-any/>
                            </ace-rule>
                        </access-list-seq-rule>
                    </extended>
                </ios:access-list>
            </ios:ip>
        </ios:native>
            """
        config = f"""
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                    <interface>
                        <VirtualPortGroup>
                            <name>0</name>
                            <ip>
                                <address>
                                    <primary>
                                        <address>{obj.cfg.vpgip}</address>
                                        <mask>255.255.255.0</mask>
                                    </primary>
                                </address>
                                <nat xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-nat">
                                    <inside></inside>
                                </nat>
                            </ip>
                        </VirtualPortGroup>
                    </interface>
                    <interface>
                        <GigabitEthernet>
                            <name>1</name>
                            <ip>
                                <nat xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-nat">
                                    <outside></outside>
                                </nat>
                            </ip>
                        </GigabitEthernet>
                    </interface>
                </native>
                {nat_config}
                {app_hosting_config}
            </config>
        """
        print(config)
        try:
            return obj.device_api.config(config=config)
        except RPCError as e:
            print(f"XML Response: {e.xml}")
            print(e.__dict__)
            print(e)

    @staticmethod
    def activate(obj):
        """ Activate Thousand Eyes Agent on device """
        rpc = f"""
        <app-hosting xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">
            <activate>
                <appid>{obj.cfg.appid}</appid>
            </activate>
        </app-hosting>
        """
        data = xmltodict.parse(obj.device_api.rpc(rpc=rpc))
        return Verify.app_status_deploy(data=data, appid=obj.cfg.appid)

    @staticmethod
    def start(obj):
        """ Start Thousand Eyes Agent on device """
        rpc = f"""
        <app-hosting xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">
            <start>
                <appid>{obj.cfg.appid}</appid>
            </start>
        </app-hosting>
        """
        data = xmltodict.parse(obj.device_api.rpc(rpc=rpc))
        return Verify.app_status_deploy(data=data, appid=obj.cfg.appid)
