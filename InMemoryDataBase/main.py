from datetime import datetime

class Row:
    def __init__(self, row_id, column_values_map, column_types_map):
        self.row_id=row_id
        self.column_values_map=column_values_map
        self.column_types_map=column_types_map
        self.created_at=datetime.now()

    def get_column_values_map(self):
        return self.column_values_map
    
    def set_column_values_map(self, column_values_map):
        self.column_values_map = column_values_map

class Table:
    def __init__(self, table_name):
        self.table_name=table_name
        self.rows={}
        self.created_at=datetime.now()
        self.column_types_map={}
        self.indexes = {}
        self.row_id=0

    def add_column(self, column_name, column_type):
        self.column_types_map[column_name]=column_type
        self.indexes[column_name]={}
        print(f"{column_name} has been added")

    def insert_entry(self, columns_map):
        for column_name, value in columns_map.items():
            expected_type=self.column_types_map[column_name]
            if expected_type and not isinstance(value, expected_type):
                print("Type mismatch error. Value for column {column} is not expected type")
                return 
            
        if self.row_id in self.rows:
            print("Duplication error. Insertion Failed for row id {row_id}")
        else:
            row = Row(self.row_id, columns_map, self.column_types_map)
            self.rows[self.row_id]=row
            for column_name, value in columns_map.items():
                if column_name in self.indexes:
                    if value not in self.indexes[column_name]:
                        self.indexes[column_name][value]=[]
                    self.indexes[column_name][value].append(self.row_id)
            print("Successfully Inserted a row")
            inserted_id=self.row_id
            self.row_id+=1
        return inserted_id

    def update_entry(self, row_id, values_map):
        row = self.rows.get(row_id)
        if row:
            for column_name, new_value in values_map.items():
                old_value=row.get_column_values_map().get(column_name)
                if column_name in self.indexes:
                    if old_value in self.indexes[column_name]:
                        self.indexes[column_name][old_value].remove(row_id)
                        if not self.indexes[column_name][old_value]:
                            del self.indexes[column_name][old_value]
                    if new_value not in self.indexes[column_name]:
                        self.indexes[column_name][new_value]=[]
                    self.indexes[column_name][new_value].append(row_id)
            
            row.set_column_values_map({**row.get_column_values_map(), **values_map})
        else:
            print(f"Row with Id {row_id} not found")
        
    def delete_entry(self, row_id):
        if row_id in self.rows:
            row = self.rows.get(row_id)
            for column_name in row.get_column_values_map():
                value=row.get_column_values_map().get(column_name)
                if column_name in self.indexes:
                    if value in self.indexes[column_name]:
                        self.indexes[column_name][value].remove(row_id)
                        if not self.indexes[column_name][value]:
                            del self.indexes[column_name][value]
            del self.rows[row_id]
            print("Row successfully deleted")
        else:
            print(f"Row with ID {row_id} not found")

    def read_entry(self, row_id):
        if row_id in self.rows:
            print("Row is retrieved ")
            return self.rows[row_id].get_column_values_map()
        else:
            print(f"Row with ID {row_id} not found")

    def read_entry_by_index(self, column_name, value):
        if column_name in self.indexes and value in self.indexes[column_name]:
            row_ids = self.indexes[column_name][value]
            return {row_id: self.rows[row_id].get_column_values_map() for row_id in row_ids}
        else:
            print("No entries found for {column_name} and {value}")
            return None

    def read_all_entries(self):
        if not self.rows:
            print("No entries found in the table.")
        else:
            print("Reading all entries in the table")
            for row_id, row in self.rows.items():
                print(f" Row id: {row_id}, Data: {row.get_column_values_map()}")

class Database:
    def __init__(self, name):
        self.name=name
        self.table_hash_map={}
        self.created_at=datetime.now()

    def create_table(self, table_name):
        if table_name in self.table_hash_map:
            print(f" Table exists already {table_name}")
        else:
            table = Table(table_name)
            self.table_hash_map[table_name]=table
            print(f" Table has been created {table_name}")
            return self.table_hash_map[table_name]

    def delete_table(self, table_name):
        if table_name in self.table_hash_map:
           print(f"Table has been deleted {table_name}")
           del self.table_hash_map[table_name]
        else:
             print(f" Table not exist. Unable to delete {table_name}")
        



def run():
    database = Database("test_db")

    table = database.create_table("test_table")

    table.add_column("name", str)
    table.add_column("email", str)

    row1_data = {"name": "sreyas", "email":"sreyas@gmail.com"}
    row1_id = table.insert_entry(row1_data)
    print(row1_id)

    row1=table.read_entry(row1_id)
    print(row1)

    update_data = {"email": "sreyas1@gmail.com"}
    table.update_entry(row1_id, update_data)

    row2_data = {"name": "abhishek", "email":"abhishek@gmail.com"}
    row2_id = table.insert_entry(row2_data)

    row2=table.read_entry(row2_id)
    print(row2)

    row3_data = {"name": "sreyas", "email":23}
    row3_id = table.insert_entry(row3_data)
    print(row3_id)


    table.read_all_entries()

    print(table.read_entry_by_index("name", "sreyas"))

    table.delete_entry(row2_id)

    print(table.read_entry_by_index("name", "abhishek"))

    table.read_all_entries()

    database.delete_table("test_table")


if __name__=='__main__':
    run()