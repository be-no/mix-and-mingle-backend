from peewee import *

# create db instance
db = SqliteDatabase('mix.db')

# create model
class Output(Model):
    # BlobField stores binary data like content in xslx
    file_data = BlobField()
    name = CharField(default='output.xlsx')

    class Meta:
        # assigns db to model?
        database = db

def create_output_table():
    with db:
        if Output.table_exists():
            Output.drop_table()
            print("Table has been dropped successfully.")
        
        if not Output.table_exists():
            Output.create_table()
            print("Table has been recreated successfully.")

db.connect()
create_output_table()
db.close()