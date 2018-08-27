import paramiko
import re
import csv
import argparse

def main(server,port=22,user=None,pwd=None,key=None):
    if(port == None):
        port = 22
    if(server == None):
        server = 'localhost'
    try:
        # Create an ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        if key is not None:
            ssh.connect(server,user,key)
        else:
            ssh.connect(server,port,user,pwd)

        # Get the available disk space
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("df -h")
        df_lines = ssh_stdout.readlines()
        available_header_location = None
        if 'Avail' in df_lines[0]:
            available_header_location = df_lines[0].split().index('Avail')
        if 'Available' in df_lines[0]:
            available_header_location = df_lines[0].split().index('Available')
        available_diskspace = df_lines[1].split()[available_header_location-1]
        print(available_diskspace)

        # Get the dns server
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("grep nameserver /etc/resolv.conf")
        nameserver_lines = ssh_stdout.readlines()
        dns_ips = []
        for nm in nameserver_lines:
            dns_ips.append(nm.split()[1])
        print(dns_ips)

        # Get the kernel version
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("uname -r")
        kernel_version = ssh_stdout.readlines()[0].split()[0]
        print(kernel_version)

        # Get the memory usage
        s = 'page size of (.*) bytes'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("vm_stat")
        # Get the size of the page
        out = ssh_stdout.readlines()
        page_size = re.search(s,out[0])
        # calculate memory usage
        free_memory = int(out[1].split()[2].replace(".","")) * float(int(page_size.group(1))/ 1048576)
        inactive_memory = int(out[2].split()[2].replace(".","")) * float(int(page_size.group(1))/ 1048576)
        active_memory = int(out[3].split()[2].replace(".","")) * float(int(page_size.group(1))/ 1048576)
        print(free_memory)
        print(inactive_memory)
        print(active_memory)
        ssh.close()

        # write to a csv
        with open('system_stats.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['Available Diskspace','DNS servers','Kernel Version','Free Memeory','Inactive Memory','Active Memory'])
            spamwriter.writerow([available_diskspace,dns_ips[0],kernel_version,str(float(free_memory))+'Mi',str(float(inactive_memory))+'Mi',str(float(active_memory))+'Mi'])
            if len(dns_ips) > 1:
                for x in range(1, len(dns_ips)):
                    spamwriter.writerow([None,dns_ips[x],None,None,None,None])
    finally:
        print(' error connecting, wrong credentials or not enough permissions')
        print('')
        ssh.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print machine stats')
    parser.add_argument('-H', metavar='hostname', type=str, nargs='?',
                   help='ssh hostname')
    parser.add_argument('-p', metavar='port', type=int, nargs='?',
                   help='ssh port')
    parser.add_argument('-u', metavar='username', type=str, nargs='?',
                   help='ssh username')
    parser.add_argument('-P', metavar='password', type=str, nargs='?',
                   help='ssh password')
    parser.add_argument('-k', metavar='key', type=str, nargs='?',
                   help='ssh private key')
    args = parser.parse_args()

    main(args.H,args.p,args.u,args.P)
