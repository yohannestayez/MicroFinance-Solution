#!/usr/bin/python3
""" console """

import cmd
import models
from models.base_model import BaseModel
from BackEnd.models.user import User
from models.Account import Account
from models.Loan import Loan
from BackEnd.models.Repayment import Repayment
from models.Transaction import Transaction
import shlex  # for splitting the line along spaces except in double quotes
from sqlalchemy.exc import IntegrityError

classes = {"BaseModel": BaseModel, "User": User,
                                                "Account" : Account,  "Admin" : Admin,
           "Customer" : Customer, "Loan" : Loan,
                                                "Repayment" : Repayment, "Transaction" : Transaction}


class HBNBCommand(cmd.Cmd):
    """ Micro Finance Solution console """
    prompt = '(MFS) '

    def do_EOF(self, arg):
        """Exits console"""
        return True

    def emptyline(self):
        """ Overwriting the emptyline method """
        return False

    def do_quit(self, arg):
        """Quit command to exit the program"""
        return True

    def _key_value_parser(self, args):
        """Creates a dictionary from a list of strings"""
        new_dict = {}
        for arg in args:
            if "=" in arg:
                kvp = arg.split('=', 1)
                key = kvp[0]
                value = kvp[1]
                if value[0] == value[-1] == '"':  # Handle string values
                    value = shlex.split(value)[0].replace('_', ' ')
                elif value.lower() == 'true':  # Handle boolean True
                    value = True
                elif value.lower() == 'false':  # Handle boolean False
                    value = False
                else:
                    try:
                        value = int(value)  # Handle integer values
                    except ValueError:
                        try:
                            value = float(value)  # Handle float values
                        except ValueError:
                            continue
                new_dict[key] = value
        return new_dict

    def do_create(self, arg):
        """Creates a new instance of a class"""
        args = arg.split()
        if len(args) == 0:
            print("** class name missing **")
            return False
        if args[0] in classes:
            new_dict = self._key_value_parser(args[1:])
            try:
                instance = classes[args[0]](**new_dict)
                instance.save()
                print(instance.id)
            except IntegrityError as e:
                print(f"Error: {e.orig}")  # Print a specific error message
                print("** failed to create instance due to integrity error **")
        else:
            print("** class doesn't exist **")
            return False

    def do_show(self, arg):
        """Prints an instance as a string based on the class and id"""
        args = shlex.split(arg)
        if len(args) == 0:
            print("** class name missing **")
            return False
        if args[0] in classes:
            if len(args) > 1:
                key = args[0] + "." + args[1]
                if key in models.storage.all():
                    print(models.storage.all()[key])
                else:
                    print("** no instance found **")
            else:
                print("** instance id missing **")
        else:
            print("** class doesn't exist **")

    def do_destroy(self, arg):
        """Deletes an instance based on the class and id"""
        args = shlex.split(arg)
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] in classes:
            if len(args) > 1:
                key = args[0] + "." + args[1]
                if key in models.storage.all():
                    models.storage.all().pop(key)
                    models.storage.save()
                else:
                    print("** no instance found **")
            else:
                print("** instance id missing **")
        else:
            print("** class doesn't exist **")

    def do_all(self, arg):
        """Prints string representations of instances"""
        args = shlex.split(arg)
        obj_list = []
        if len(args) == 0:
            obj_dict = models.storage.all()
        elif args[0] in classes:
            obj_dict = models.storage.all(classes[args[0]])
        else:
            print("** class doesn't exist **")
            return False
        for key in obj_dict:
            obj_list.append(str(obj_dict[key]))
        print("[", end="")
        print(", ".join(obj_list), end="")
        print("]")

    def do_update(self, arg):
        """Update an instance based on the class name, id, attribute & value"""
        args = shlex.split(arg)
        integers = ["number_rooms", "number_bathrooms", "max_guest",
                    "price_by_night"]
        floats = ["latitude", "longitude"]
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] in classes:
            if len(args) > 1:
                k = args[0] + "." + args[1]
                if k in models.storage.all():
                    if len(args) > 2:
                        if len(args) > 3:
                            if args[0] == "Place":
                                if args[2] in integers:
                                    try:
                                        args[3] = int(args[3])
                                    except ValueError:
                                        args[3] = 0
                                elif args[2] in floats:
                                    try:
                                        args[3] = float(args[3])
                                    except ValueError:
                                        args[3] = 0.0
                            setattr(models.storage.all()[k], args[2], args[3])
                            models.storage.all()[k].save()
                        else:
                            print("** value missing **")
                    else:
                        print("** attribute name missing **")
                else:
                    print("** no instance found **")
            else:
                print("** instance id missing **")
        else:
            print("** class doesn't exist **")

if __name__ == '__main__':
    HBNBCommand().cmdloop()
