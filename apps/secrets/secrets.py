__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import os
import sqlite3
from pegasusautomation import settings
from apps.vmm.models import VM
from cryptography.fernet import Fernet


class SecretsDB:

    def __init__(self):
        self.setup_database()
        self.key = Fernet.generate_key()  # this is your "key"

        self.cipher_suite = Fernet(self.key)

    def user(self):
        data = self.execute_cmd(cmd="select username from pegasus ")
        try:
            if 'Error' in data.keys():
                return None
            elif 'data' in data.keys():
                return data['data'][0]
        except Exception as e:
            return None

    def setup_database(self):
        self.create_table()

    def create_table(self):
        self.execute_cmd(cmd="CREATE TABLE IF NOT EXISTS pegasus "
                             "(id integer PRIMARY KEY AUTOINCREMENT, username text NOT NULL, password text, "
                             "passkey text );")
        return self.execute_cmd(cmd="CREATE TABLE IF NOT EXISTS credentials "
                             "(id integer PRIMARY KEY AUTOINCREMENT, username text NOT NULL, password text, "
                                    "passkey text );")

    def connectdb(self):
        return sqlite3.connect("secrets.db")

    def execute_cmd(self, cmd):
        connect = self.connectdb()
        cur = connect.cursor()
        try:
            cur.execute(cmd)
            if "insert" in cmd.lower():
                connect.commit()
            data = cur.fetchone()
            if data != None:
                return {'data': data}
            else:
                return {'status': '400'}
        except Exception as e:
            logger.debug("ERROR : {}".format(e))
            return {'Error', str(e)}

    def get_password(self, user):
        try:
            data = self.execute_cmd(cmd="select password, passkey from credentials where username='{user}' ".format(user=user))
            passwd = data['data'][0].encode('ascii')
            key = data['data'][1].encode('ascii')
            return self.decrypt(passwd, key).decode('ascii')
        except Exception as e:
            logger.debug("Password not found for user : {}.\nUse secrets.py to add this machine credentials in the SQLITE Database (secrets.db)".format(user))
            return None
        # return self.execute_cmd(cmd="select password from credentials where username='{user}'".format(user=user))

    def set_password(self, user, password):
        """ function to insert into table"""
        password = self.encrypt(password)

        cmd = """  INSERT into credentials(username, password, passkey) values (\'{username}\', \'{password}\', \'{passkey}\') """\
            .format(username=user, password=password.decode('ascii'), passkey=self.key.decode('ascii'))
        self.execute_cmd(cmd=cmd)
        return password
    
    def set_pegasus_password(self, user, password):
        """ function to insert into table"""
        password = self.encrypt(password)

        cmd = """  INSERT into pegasus(username, password, passkey) values (\'{username}\', \'{password}\', \'{passkey}\') """\
            .format(username=user, password=password.decode('ascii'), passkey=self.key.decode('ascii'))
        self.execute_cmd(cmd=cmd)
        return password
    
    def get_pegasus_password(self, user):
        try:
            data = self.execute_cmd(cmd="select password, passkey from pegasus where username='{user}' ".format(user=user))
            passwd = data['data'][0].encode('ascii')
            key = data['data'][1].encode('ascii')
            return self.decrypt(passwd, key).decode('ascii')
        except Exception as e:
            logger.debug("Password not found for user : {}.\nUse secrets.py to add this machine credentials in the SQLITE Database (secrets.db)".format(user))
            return None

    # function to encrypt your password
    def encrypt(self, pwd):
        encoded_text = self.cipher_suite.encrypt(pwd.encode())
        return encoded_text

    def decrypt(self, pwd, key):
        f = Fernet(key)
        return f.decrypt(pwd)

    def set_password_model(self, vm_obj, password):
        """ encrypt password and save in model VM"""

        # password = self.encrypt(password).decode('ascii')
        password = self.encrypt(password).decode('ascii')
        vm_obj.password = password
        vm_obj.passkey = self.key.decode('ascii')
        # vm_obj.passkey = self.key
        vm_obj.save()
        return vm_obj.password

    def get_password_model(self, vm):
        vm_obj = VM.objects.get(vm_name=vm)
        return self.decrypt(vm_obj.password.encode('ascii'), vm_obj.passkey.encode('ascii')).decode('ascii')
        # return self.decrypt(vm_obj.password, vm_obj.passkey)


if __name__ == "__main__":

    try:
        db = SecretsDB()    # SecretsDB class

        logger.debug("Add Peagasus Account Username and Password.\nPress ENTER if you have already saved the agent creds.")
        pegasus_user = input("Username:")
        pegasus_password = input("Password:")
        if pegasus_user and pegasus_password:
            db.set_password(user=pegasus_user, password=pegasus_password)
        # logger.debug(db.get_password(user=pegasus_user))

        for name in settings.vm_info:
            vm = name[0]
            logger.debug("Virtual Machine Information  : {}.\nAdd password".format(vm))
            logger.debug("{}".format(name[1]))
            password = input("Password:")
            db.set_password(user=vm, password=password)

    except Exception as e:
        logger.debug("Error : {}".format(e))


