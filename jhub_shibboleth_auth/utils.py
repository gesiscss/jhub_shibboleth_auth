import pwd
import grp
from os import mkdir, chown


def add_system_user(user_name, notebooks_folder):
    # create notebooks folder in home dir and change owner:group to this user
    mkdir(notebooks_folder)
    uid = pwd.getpwnam(user_name).pw_uid
    gid = grp.getgrnam(user_name).gr_gid
    chown(notebooks_folder, uid, gid)
