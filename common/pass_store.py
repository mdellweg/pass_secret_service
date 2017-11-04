import os
import shutil
import uuid
import simplejson as json
from pypass import PasswordStore

class PassStore:
    PREFIX = 'secret_service'

    def __init__(self, *args, **kwargs):
        self._store = PasswordStore(*args, **kwargs)
        self.base_path = os.path.join(self._store.path, self.PREFIX)

    # Aliases
    def get_aliases(self):
        try:
            with open(os.path.join(self.base_path, '.aliases'), 'r') as fp:
                aliases = json.load(fp)
        except:  # pragma: no cover
            aliases = {}
        return aliases or {}

    def save_aliases(self, aliases):
        with open(os.path.join(self.base_path, '.aliases'), 'w') as fp:
            json.dump(aliases, fp, sort_keys=True)

    # Collections (Directories)
    def get_collections(self):
        return ( entry.name for entry in os.scandir(self.base_path) if entry.is_dir() )

    def create_collection(self, properties):
        name = str(uuid.uuid4()).replace('-', '_')  # TODO: check for crashes
        os.mkdir(os.path.join(self.base_path, name))
        self.save_collection_properties(name, properties)
        return name

    def delete_collection(self, name):
        shutil.rmtree(os.path.join(self.base_path, name))

    def save_collection_properties(self, name, properties):
        with open(os.path.join(self.base_path, name, '.properties'), 'w') as fp:
            json.dump(properties, fp, sort_keys=True)

    def get_collection_properties(self, name):
        try:
            with open(os.path.join(self.base_path, name, '.properties'), 'r') as fp:
                properties = json.load(fp)
        except:
            properties = {}
        return properties or {}

    def update_collection_properties(self, name, new_properties):
        properties = self.get_collection_properties(name)
        properties.update(new_properties)
        self.save_collection_properties(name, properties)
        return properties

    # Items
    def get_items(self, collection_name):
        collection_path = os.path.join(self.base_path, collection_name)
        return ( entry.name[:-4] for entry in os.scandir(collection_path) if entry.is_file() and entry.name.endswith('.gpg') )

    def create_item(self, collection_name, password , properties):
        name = str(uuid.uuid4()).replace('-', '_')  # TODO: check for crashes
        self.set_item_password(collection_name, name, password)
        self.save_item_properties(collection_name, name, properties)
        return name

    def delete_item(self, collection_name, name):
        os.remove(os.path.join(self.base_path, collection_name, name) + '.gpg')
        os.remove(os.path.join(self.base_path, collection_name, name) + '.properties')

    def set_item_password(self, collection_name, name, password):
        self._store.insert_password(os.path.join(self.PREFIX, collection_name, name), password)

    def get_item_password(self, collection_name, name):
        return self._store.get_decypted_password(os.path.join(self.PREFIX, collection_name, name))
        # use the next line as soon, as this typo is fixed
        # return self._store.get_decrypted_password(os.path.join(self.PREFIX, collection_name, name))

    def save_item_properties(self, collection_name, name, properties):
        with open(os.path.join(self.base_path, collection_name, name) + '.properties', 'w') as fp:
            json.dump(properties, fp, sort_keys=True)

    def get_item_properties(self, collection_name, name):
        try:
            with open(os.path.join(self.base_path, collection_name, name) + '.properties', 'r') as fp:
                properties = json.load(fp)
        except:
            properties = {}
        return properties or {}

    def update_item_properties(self, collection_name, name, new_properties):
        properties = self.get_item_properties(collection_name, name)
        properties.update(new_properties)
        self.save_item_properties(collection_name, name, properties)
        return properties

#  vim: set tw=160 sts=4 ts=8 sw=4 ft=python et noro norl cin si ai :
