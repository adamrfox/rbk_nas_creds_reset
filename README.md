# rbk_nas_creds_reset
A script to reset SMB NAS credentials on Rubrik clusters

This was built for a particular customer use case but others may find the code useful.  Feel free to file issues for updates or fork the cdoe and contribute!

The concept is to scan a set of Rubrik clusters and bulk replace the SMB user (not the API user) for NAS hosts.  This can be helpful if a password had changed or if reconfiguring is needed.

The script assume that all Rubrik clusters have the same creds for API access.  That could be updated in the future, but it could get tedious trying to do that in a secure manner.  Ideas welcome.

Note the -c flag is not secure.  It's mostly there to make development easier.  Use at your own risk.

Usage:

<pre>
Usage: rbk_nas_creds_reset.py [-hDH] [-i input_file] [-c cluster_creds] [rubrik,rubrik,...,rubrik]
-h | --help : Prints this message
-H | --hosts_only : Don't erase share over-ride creds
-D | --debug : Print debug info
-i | --input : Get rubrik cluster from a text file.  This replaces listing them on the CLI
-c | --creds : Specify cluster creds on CLI.  This is not secure.
rubrik, ..., rubrik : List rubrik clusters on the CLI.  Use this if not using -i
</pre>

Note:  The script is intended to be run on either Python 2 or 3.  The 'rubrik-cdm' package needs to be installed via pip/pip3.
