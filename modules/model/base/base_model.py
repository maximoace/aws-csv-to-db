from modules.database.db import Database

#This is a custom ORM database manager for basic CRUD
class BaseManager:
    cursor = Database().get_cursor()

    def __init__(self, model_class) -> None:
        self.model_class = model_class

    def select(self, *field_names, chunk_size = 2000):
        #Build SELECT query
        fields_format = ', '.join(field_names)
        query = f"SELECT {fields_format if fields_format else '*'} FROM {self.model_class.table_name}"

        #Execute query
        self.cursor.execute(query)

        # Fetch data obtained with the previous query execution
        # and transform it into `model_class` objects.
        # The fetching is done by batches of the determined `chunk_size` to
        # avoid running out of memory.
        model_objects = list()
        is_fetching_completed = False
        column_names = field_names if field_names else [header[0] for header in self.cursor.description]
        while not is_fetching_completed:
            result = self.cursor.fetchmany(size = chunk_size)
            for row_values in result:
                keys, values = column_names, row_values
                row_data = dict(zip(keys, values))
                model_objects.append(self.model_class(**row_data))
            is_fetching_completed = len(result) < chunk_size

        return model_objects

    def insert(self, rows):
        #Ensures data is always a list even if its a single dict data.
        rows = [rows] if not (isinstance(rows, list)) else rows

        field_names = rows[0].keys()
        assert all(row.keys() == field_names for row in rows[1:])  # confirm that all rows have the same fields

        #Build INSERT query.
        #Follows MariaDB sanitized input where '?' is a local variable
        #To be set as a parameter.
        fields_format = ", ".join(field_names)
        values_placeholder_format = ", ".join([f'({", ".join(["%s"] * len(field_names))})'] * len(rows))  # https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
        query = f"INSERT INTO {self.model_class.table_name} ({fields_format}) " \
                f"VALUES {values_placeholder_format}"

        params = list()
        for row in rows:
            row_values = [row[field_name] for field_name in field_names]
            params += row_values

        # Execute query
        self.cursor.execute(query, params)

    #Custom insert to add new values of the s3 bucket without duplicating entries
    def insert_no_duplicate(self, rows):
        #Ensures data is always a list even if its a single dict data.
        rows = [rows] if not (isinstance(rows, list)) else rows

        field_names = rows[0].keys()
        assert all(row.keys() == field_names for row in rows[1:])  # confirm that all rows have the same fields
        
        #Build INSERT query.
        #Follows MariaDB sanitized input where '?' is a local variable
        #To be set as a parameter.
        fields_format = ", ".join(field_names)
        values_placeholder_format = ", ".join([f'{", ".join(["%s"] * len(field_names))}'] * len(rows))  # https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
        query = f"INSERT IGNORE INTO {self.model_class.table_name} ({fields_format}) " \
                f"SELECT {values_placeholder_format}"

        params = list()
        for row in rows:
            row_values = [row[field_name] for field_name in field_names]
            params += row_values

        # Execute query
        self.cursor.execute(query, params)

    def update(self, data):
        pass

    def delete(self, data):
        pass

#Metaclass to add general base manager
class MetaModel(type):
    manager_class = BaseManager
    print("Reached meta class")

    def _get_manager(cls):
        return cls.manager_class(model_class=cls)

    @property
    def objects(cls):
        return cls._get_manager()


'''
This is the class that MUST be inherited, any custom database managing.
Any custom behavior should be created on a upper level class, overriding
base functions if necessary.
'''
class BaseModel(metaclass=MetaModel):
    table_name = ""

    #Add data as object attribute when called
    def __init__(self, **row_data) -> None:
        for field_name, value in row_data.items():
            setattr(self, field_name.lower(), value)

    #Defining representation and format when printed
    def __repr__(self) -> str:
        attrs_format = ", ".join([f"{field}={value}" for field, value in self.__dict__.items()])
        return f"<{self.__class__.__name__}: ({attrs_format})"