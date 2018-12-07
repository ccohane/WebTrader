#!/usr/bin/env python3
import sqlite3

#programmer defined types

class Database():

    def __init__(self):
        self.connection=sqlite3.connect("Terminal_Trader.db",check_same_thread=False)
        self.c=self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val,exc_tb):
        if self.connection:
            self.connection.commit()
            self.connection.close()
