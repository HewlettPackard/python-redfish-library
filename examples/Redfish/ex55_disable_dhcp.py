 # Copyright 2016 Hewlett Packard Enterprise Development, LP.
 #
 # Licensed under the Apache License, Version 2.0 (the "License"); you may
 # not use this file except in compliance with the License. You may obtain
 # a copy of the License at
 #
 #      http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 # License for the specific language governing permissions and limitations
 # under the License.

import sys
from _redfishobject import RedfishObject
from redfish.rest.v1 import ServerDownOrUnreachableError

def ex55_disable_dhcp(redfishobj, dhcp_enabled):
    sys.stdout.write("\nEXAMPLE ##: Disable DHCPv4 for iLO\n")
    instances = redfishobj.search_for_type("Manager.")
    selected_nic_uri = None

    for instance in instances:
        tmp = redfishobj.redfish_get(instance["@odata.id"])  
        response = redfishobj.redfish_get(tmp.dict["EthernetInterfaces"]\
                                                                ["@odata.id"])
        
        for entry in response.dict["Members"]:
            nic = redfishobj.redfish_get(entry["@odata.id"])

            if redfishobj.typepath.defs.isgen9:
                oemhpdict = nic.dict["Oem"]["Hp"]
            else:
                oemhpdict = nic.dict["Oem"]["Hpe"]
            try:
                if (oemhpdict["SupportsFlexibleLOM"] == True and \
                                                            dhcp_enabled == False):
                    selected_nic_uri = nic.dict["links"]["self"]["href"]
                    break
            except KeyError:
                pass
    
            try:
                if (oemhpdict["SupportsLOM"] == True and \
                                                            dhcp_enabled == False):
                    selected_nic_uri = nic.dict["links"]["self"]["href"]
                    break
            except KeyError:
                pass
    
            if not dhcp_enabled:
                selected_nic_uri = entry["@odata.id"]
                break
            elif not selected_nic_uri:
                sys.stderr.write("\tShared NIC is not supported\n")
                break
    
        if selected_nic_uri:
            if redfishobj.typepath.defs.isgen9:
                body = {"Oem": {"Hp": {"DHCPv4": {"Enabled": dhcp_enabled}}}}
            else:
                body = {"Oem": {"Hpe": {"DHCPv4": {"Enabled": dhcp_enabled}}}}
            sys.stdout.write("\n\n" + str(selected_nic_uri) + "\n\n")
            response = redfishobj.redfish_patch(selected_nic_uri, body)
            redfishobj.error_handler(response)

if __name__ == "__main__":
    # When running on the server locally use the following commented values
    # iLO_https_url = "blobstore://."
    # iLO_account = "None"
    # iLO_password = "None"

    # When running remotely connect using the iLO secured (https://) address, 
    # iLO account name, and password to send https requests
    # iLO_https_url acceptable examples:
    # "https://10.0.0.100"
    # "https://ilo.hostname"
    iLO_https_url = "https://10.0.0.100"
    iLO_account = "admin"
    iLO_password = "password"
    
    # Create a REDFISH object
    try:
        REDFISH_OBJ = RedfishObject(iLO_https_url, iLO_account, iLO_password)
    except ServerDownOrUnreachableError as excp:
        sys.stderr.write("ERROR: server not reachable or doesn't support " \
                                                                "RedFish.\n")
        sys.exit()
    except Exception as excp:
        raise excp

    ex55_disable_dhcp(REDFISH_OBJ, False)
    REDFISH_OBJ.redfish_client.logout()