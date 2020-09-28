#!/usr/bin/python
from __future__ import print_function
import rubrik_cdm
import sys
import getpass
import getopt
import urllib3
urllib3.disable_warnings()

def usage():
    sys.stderr.write("Usage: rbk_nas_creds_reset.py [-hDH] [-i input_file] [-c cluster_creds] [rubrik,rubrik,...,rubrik]\n")
    sys.stderr.write("-h | --help : Prints this message\n")
    sys.stderr.write("-H | --hosts_only : Don't erase share over-ride creds\n")
    sys.stderr.write("-D | --debug : Print debug info\n")
    sys.stderr.write("-i | --input : Get rubrik cluster from a text file.  This replaces listing them on the CLI\n")
    sys.stderr.write("-c | --creds : Specify cluster creds on CLI.  This is not secure.\n")
    sys.stderr.write("rubrik, ..., rubrik : List rubrik clusters on the CLI.  Use this if not using -i\n")
    exit(0)

def dprint(message):
    if DEBUG:
        print(message)

def get_clusters_from_file(file):
    clusters = []
    with open(file) as fp:
        for n, line in enumerate(fp):
            line = line.rstrip()
            if line == "" or line.startswith('#'):
                continue
            clusters.append(line)
    fp.close()
    return (clusters)

def python_input(message):
    if (int(sys.version[0]) > 2):
        value = input(message)
    else:
        value = raw_input(message)
    return(value)

def get_hostname_from_id(host_ids, id):
    hostname = ""
    for hostname in host_ids:
        if host_ids[hostname] == id:
            break
    return(hostname)

if __name__ == "__main__":
    rubrik_clusters = []
    rubrik_user = ""
    rubrik_password = ""
    smb_user = ""
    smb_password = ""
    DEBUG = False
    HOSTS_ONLY = False
    input_file = ""
    skipped_shares = []

    optlist, args = getopt.getopt(sys.argv[1:], 'hDi:c:H', ['--help', '--debug', '--input', '--creds', '--hosts_only'])
    for opt, a in optlist:
        if opt in ('-h', '--help'):
            usage()
        if opt in ('-D', '--debug'):
            DEBUG = True
        if opt in ('-i', '--input'):
            input_file = a
        if opt in ('-c', '--creds'):
            (rubrik_user, rubrik_password) = a.split(':')
        if opt in('-H', '--hosts_only'):
            HOSTS_ONLY = True
    if not input_file:
        try:
            rubrik_clusters = args[0].split(',')
        except IndexError:
            pass
    else:
        rubrik_clusters = get_clusters_from_file(input_file)
    if not rubrik_clusters:
        usage()
    if not rubrik_user:
        rubrik_user = python_input("Rubrik User: ")
    if not rubrik_password:
        rubrik_password = getpass.getpass("Rubrik Password: ")
    smb_user_data = python_input("SMB User [user@domain]: ")
    (smb_user, smb_domain) = smb_user_data.split('@')
    done = False
    while not done:
        smb_password = getpass.getpass("SMB Password: ")
        smb_pw2 = getpass.getpass("Re-enter SMB Password: ")
        if smb_password == smb_pw2:
            done = True
        else:
            print("Passwords do not match")
    for rubrik_host in rubrik_clusters:
        host_ids = {}
        rubrik = rubrik_cdm.Connect(rubrik_host, rubrik_user, rubrik_password)
        print("Scanning " + rubrik_host)
        host_data = rubrik.get('v1', '/host?operating_system_type=NONE', timeout=60)
        for host in host_data['data']:
            host_ids[host['hostname']] = host['id']
        dprint("HOSTS:" + str(host_ids))
        for host in host_ids:
            print("   Updating " + host)
            payload = {'hostId': str(host_ids[host]), 'username': smb_user, 'password': smb_password, 'domain': smb_domain}
            try:
                update = rubrik.post('internal', '/host/share_credential', payload, timeout=60)
            except rubrik_cdm.exceptions.APICallException as e:
                sys.stderr.write("Share Update Failed: " + str(e))
                skipped_shares.append(rubrik_host + ":" + host)
        if not HOSTS_ONLY:
            share_data = rubrik.get('internal', '/host/share?share_type=SMB', timeout=60)
            dprint("SHARE_DATA: " + str(share_data))
            for sh in share_data['data']:
                if 'username' in sh.keys():
                    hostname = get_hostname_from_id(host_ids, sh['hostId'])
                    print("   Deleting user for share: " + hostname + ":" + sh['exportPoint'])
                    payload = {'exportPoint': sh['exportPoint'], 'username': ""}
                    dprint("PAYLOAD: " + str(payload))
                    try:
                        update = rubrik.patch('internal', '/host/share/' + str(sh['id']), payload, timeout=60)
                    except rubrik_cdm.exceptions.APICallException as e:
                        sys.stderr.write("Share Update Failed: " + str(e) + "\n")
                        skipped_shares.append(rubrik_host + ":" + host + ":" + sh['exportPoint'])

    if skipped_shares:
        print("The following hosts/shares were not updated due to error:")
        for sh in skipped_shares:
            print(sh)
    else:
        print("All hosts/shares were updated")



