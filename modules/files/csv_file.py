import csv
import unicodedata

class CsvFile:
    
    def __init__(self, bucket_file) -> None:
        self.data = list()
        csv_list = bucket_file['Body'].read().decode('latin1').split('\r\n')
        lines = csv.DictReader(csv_list, delimiter=';')
        for line in lines:
            self.data.append(line)

    #Filter desired data based on a list of dict keys.
    def filter_data(self, keys:list):
        new_data = list()
        for dict_object in self.data:
            new_dict = dict()
            for key, value in dict_object.items():
                if key in keys:
                    new_dict[key] = value
            new_data.append(new_dict)
        self.data = new_data

    #Format data to be SQL insert compatible
    def format_data(self):
        new_data = list()
        for dict_object in self.data:
            new_dict = dict()
            for key, value in dict_object.items():
                new_key = self.format_key(key)
                value = self.format_value(value)
                new_dict[new_key] = value
            new_data.append(new_dict)
        self.data = new_data

    #Format dict keys to 'key_name' pattern
    def format_key(self, key:str):
        if 'id' == key.lower():
            key = f"{key} externo"
        if "r$" in key.lower():
            key = key.lower().replace(' r$','')
            key = f"Valor {key}"
        key = key.replace(' #', '').replace(' ', '_').replace('/','_')
        key = unicodedata.normalize('NFD', key).encode('ascii', 'ignore').decode('utf-8')
        return key

    #Format dict values to desirable pattern
    def format_value(self, value:str):
        value = value.replace('-', '').replace(',', '.')
        #Checks if it is a date format
        if len(value.split('/')) == 3:
            #Checks if the first part is day or year.
            if len(value.split('/')[0]) == 2:
                day, month, year = value.split('/')
            else:
                year, month, day = value.split('/')
            value = f"{year}-{month}-{day}"
        else:
            value = value.replace('/', '')
        #Keep the '.' if its decimal value.
        if len(value.split('.')) != 2:
            value = value.replace('.', '')

        value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('utf-8')
        return value