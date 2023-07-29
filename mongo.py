from pymongo.collection import Collection
from config import client, database_name, collection_name

class UsersDB:
    def __init__(self):
        self.files_col = Collection(client[collection_name], database_name)
        
    def find(self, data):
        return self.files_col.find_one(data)
    
    def full(self):
        return list(self.files_col.find())
    
    def range(self, offset, limit):
        return list(self.files_col.find().skip(offset).limit(limit))
    
    def rando(self, sample_size):
        pipeline = [
            { "$sample": { "size": sample_size } }
        ]
        return list(self.files_col.aggregate(pipeline))

    def count(self):
        return self.files_col.count_documents({})

    def add(self, data):
        try:
            self.files_col.insert_one(data)
        except:
            pass

    def remove(self, data):
        self.files_col.delete_one(data)

class SettingsDB:
    def __init__(self):
        self.files_col = Collection(client[collection_name], f"{database_name}_settings")
        
    def find(self, data):
        return self.files_col.find_one(data)
    
    def full(self):
        return list(self.files_col.find())

    def add(self, data):
        try:
            self.files_col.insert_one(data)
        except:
            pass

    def remove(self, data):
        self.files_col.delete_one(data)

    def modify(self, search_dict, new_dict):
        try:
            self.files_col.find_one_and_update(search_dict, {'$set': new_dict})
        except Exception as e:
            print(f"Exception in SettingsDB -> modify\n\n{e}")

class ClientDB:
    def __init__(self):
        self.files_col = Collection(client[collection_name], f"{database_name}_Clients")
        
    def find(self, data):
        return self.files_col.find_one(data)
    
    def full(self):
        return list(self.files_col.find())

    def add(self, data):
        try:
            self.files_col.insert_one(data)
        except:
            pass

    def count(self):
        return self.files_col.count_documents({})
    
    def remove(self, data):
        self.files_col.delete_one(data)

    def modify(self, search_dict, new_dict):
        try:
            a = self.files_col.find_one_and_update(search_dict, {'$set': new_dict})
            if a == None:
                return False
            else:
                return True
        except Exception as e:
            print(f"Exception in ClientDB -> modify\n\n{e}")

class ForceReqDB:
    def __init__(self):
        self.files_col = Collection(client[collection_name], f"{database_name}_forced_req")
        
    def find(self, data):
        return self.files_col.find_one(data)
    
    def full(self):
        return list(self.files_col.find())

    def add(self, data):
        try:
            self.files_col.insert_one(data)
        except:
            pass

    def remove(self, data):
        self.files_col.delete_one(data)

    def modify(self, search_dict, new_dict):
        try:
            self.files_col.find_one_and_update(search_dict, {'$set': new_dict})
        except Exception as e:
            print(f"Exception in SettingsDB -> modify\n\n{e}")
