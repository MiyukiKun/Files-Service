from config import client, database_name, collection_name

class BaseDB:
    def __init__(self, collection_suffix):
        self.client = client
        self.db = self.client[collection_name]
        if collection_suffix == None:
            self.collection = self.db[f"{database_name}"]
        else:
            self.collection = self.db[f"{database_name}_{collection_suffix}"]

    async def find(self, data):
        return await self.collection.find_one(data)

    async def full(self):
        cursor = self.collection.find()
        return await cursor.to_list(length=None)

    async def add(self, data):
        try:
            await self.collection.insert_one(data)
        except Exception as e:
            print(f"Exception in {self.__class__.__name__} -> add\n\n{e}")

    async def remove(self, data):
        await self.collection.delete_one(data)

    async def modify(self, search_dict, new_dict):
        try:
            await self.collection.find_one_and_update(search_dict, {'$set': new_dict})
        except Exception as e:
            print(f"Exception in {self.__class__.__name__} -> modify\n\n{e}")

    async def range(self, offset, limit):
        cursor = self.collection.find().skip(offset).limit(limit)
        return await cursor.to_list(length=None)

    async def rando(self, sample_size):
        pipeline = [{"$sample": {"size": sample_size}}]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def count(self):
        return await self.collection.count_documents({})

class UsersDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix=None)


class SettingsDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix="settings")


class ClientDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix="Clients")


class ForceReqDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix="forced_req")

    async def modify(self, filter_data, update_data):
        try:
            await self.collection.update_one(filter_data, update_data, upsert=True)
        except Exception as e:
            print(f"Exception in ForceReqDB -> modify\n\n{e}")