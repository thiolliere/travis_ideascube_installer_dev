from . import systemd
import json

# machine must provide write_file and exec_cmd functions
def run(machine, name, timezone, wifi_pwd, kalite, zim_install):
    # machine.write_file("/etc/systemd/system.conf", systemd.system_conf)
    # machine.write_file("/etc/systemd/user.conf", systemd.user_conf)

    machine.exec_cmd("sudo apt-get update")
    machine.exec_cmd("sudo apt-get install -y python-pip git python-dev libffi-dev libssl-dev gnutls-bin")

    machine.exec_cmd("sudo pip install ansible==2.1.2 markupsafe")
    machine.exec_cmd("sudo pip install cryptography --upgrade")

    ansiblecube_url = "https://github.com/thiolliere/ansiblecube.git"
    ansiblecube_path = "/var/lib/ansible/local"

    machine.exec_cmd("sudo mkdir --mode 0755 -p %s" % ansiblecube_path)
    machine.exec_cmd("sudo git clone {url} {path}".format(url=ansiblecube_url, path=ansiblecube_path))
    machine.exec_cmd("sudo mkdir --mode 0755 -p /etc/ansible")
    machine.exec_cmd("sudo cp %s/hosts /etc/ansible/hosts" % ansiblecube_path)

    hostname = name.replace("_", "-")

    machine.exec_cmd("sudo hostname %s" % hostname)

    package_management = [{"name": x, "status": "present"} for x in zim_install]
    device_list = {hostname: {
        "kalite": {
            "activated": str(kalite != None),
            "version": "0.16.9",
            "language": kalite or [],
        },
        "idc_import": {
            "activated": "False",
            "content_name": [],
        },
        "package_management": package_management,
        "portal": {
            "activated": "True",
        }
    }}

    facts_dir = "/etc/ansible/facts.d"
    facts_path = facts_dir + "/device_list.fact"

    machine.exec_cmd("sudo mkdir --mode 0755 -p %s" % facts_dir)
    machine.write_file(facts_path, json.dumps(device_list, indent=4))

    extra_vars = "ideascube_project_name=%s" % name
    extra_vars += " timezone=%s" % timezone
    if wifi_pwd:
        extra_vars += " wpa_pass=%s" % wifi_pwd
    extra_vars += " git_branch=oneUpdateFile"
    extra_vars += " own_config_file=True"
    extra_vars += " managed_by_bsf=False"

    ansible_pull_cmd = "sudo /usr/local/bin/ansible-pull"
    ansible_pull_cmd += " --checkout oneUpdateFile"
    ansible_pull_cmd += " --directory /var/lib/ansible/local"
    ansible_pull_cmd += " --inventory hosts"
    ansible_pull_cmd += " --url https://github.com/thiolliere/ansiblecube.git"
    ansible_pull_cmd += " --tags master,custom"
    ansible_pull_cmd += " --extra-vars \"%s\"" % extra_vars
    ansible_pull_cmd += " main.yml"

    machine.exec_cmd(ansible_pull_cmd)
