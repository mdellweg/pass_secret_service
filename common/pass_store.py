import os
import shutil
import uuid
import simplejson as json
from pypass import PasswordStore

class PassStore(PasswordStore):
    PREFIX = 'secret_service'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.base_path = os.path.join(self.path, self.PREFIX)

    def get_aliases(self):
        try:
            with open(os.path.join(self.base_path, '.aliases'), 'r') as fp:
                aliases = json.load(fp)
        except:
            aliases = {}
        return aliases or {}

    def save_aliases(self, aliases):
        with open(os.path.join(self.base_path, '.aliases'), 'w') as fp:
            json.dump(aliases, fp)

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
            json.dump(properties, fp)

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
