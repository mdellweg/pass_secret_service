import json
import os
import shutil
import subprocess
import uuid


class PassStore:
    PREFIX = "secret_service"

    def __init__(self, *args, **kwargs):
        self.store_path = os.path.expanduser(
            kwargs.get(
                "path", os.environ.get("PASSWORD_STORE_DIR", "~/.password-store")
            )
        )
        self.base_path = os.path.join(self.store_path, self.PREFIX)
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    # Aliases
    def get_aliases(self):
        try:
            with open(os.path.join(self.base_path, ".aliases"), "r") as fp:
                aliases = json.load(fp)
        except Exception:  # pragma: no cover
            aliases = {}
        return aliases or {}

    def save_aliases(self, aliases):
        with open(os.path.join(self.base_path, ".aliases"), "w") as fp:
            json.dump(aliases, fp, sort_keys=True)

    # Collections (Directories)
    def get_collections(self):
        return (entry.name for entry in os.scandir(self.base_path) if entry.is_dir())

    def create_collection(self, properties):
        while True:
            name = str(uuid.uuid4()).replace("-", "_")
            collection_path = os.path.join(self.base_path, name)
            if not os.path.exists(collection_path):  # check for clashes  # pragma: no branch
                break
        os.mkdir(collection_path)
        self.save_collection_properties(name, properties)
        return name

    def delete_collection(self, name):
        shutil.rmtree(os.path.join(self.base_path, name))

    def save_collection_properties(self, name, properties):
        with open(os.path.join(self.base_path, name, ".properties"), "w") as fp:
            json.dump(properties, fp, sort_keys=True)

    def get_collection_properties(self, name):
        try:
            with open(os.path.join(self.base_path, name, ".properties"), "r") as fp:
                properties = json.load(fp)
        except Exception:  # pragma: no cover
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
        return (entry.name[:-4] for entry in os.scandir(collection_path) if entry.is_file() and entry.name.endswith(".gpg"))

    def create_item(self, collection_name, password, properties):
        while True:
            name = str(uuid.uuid4()).replace("-", "_")
            item_path = os.path.join(self.base_path, collection_name, name)
            if not os.path.exists(item_path):  # check for clashes  # pragma: no branch
                break
        self.set_item_password(collection_name, name, password)
        self.save_item_properties(collection_name, name, properties)
        return name

    def delete_item(self, collection_name, name):
        os.remove(os.path.join(self.base_path, collection_name, name) + ".gpg")
        os.remove(os.path.join(self.base_path, collection_name, name) + ".properties")

    def __pass_cmd(
        self, subcmd: str, collection_name: str, name: str, **kwargs
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["pass", subcmd, os.path.join(self.PREFIX, collection_name, name)],
            check=True,
            env=dict(
                GIT_CONFIG_COUNT="2",
                GIT_CONFIG_KEY_0="user.email",
                GIT_CONFIG_VALUE_0="pass_secret_service@localhost",
                GIT_CONFIG_KEY_1="user.name",
                GIT_CONFIG_VALUE_1="pass_secret_service",
                PASSWORD_STORE_DIR=self.store_path,
            ),
            text=True,
            **kwargs,
        )

    def set_item_password(self, collection_name, name, password):
        self.__pass_cmd(
            "insert",
            collection_name,
            name,
            input="".join([f"{password}\n"]*2)
        )

    def get_item_password(self, collection_name, name):
        return self.__pass_cmd(
            "show",
            collection_name,
            name,
            capture_output=True,
        ).stdout.removesuffix("\n")

    def save_item_properties(self, collection_name, name, properties):
        with open(os.path.join(self.base_path, collection_name, name) + ".properties", "w") as fp:
            json.dump(properties, fp, sort_keys=True)

    def get_item_properties(self, collection_name, name):
        try:
            with open(os.path.join(self.base_path, collection_name, name) + ".properties", "r") as fp:
                properties = json.load(fp)
        except Exception:  # pragma: no cover
            properties = {}
        return properties or {}

    def update_item_properties(self, collection_name, name, new_properties):
        properties = self.get_item_properties(collection_name, name)
        properties.update(new_properties)
        self.save_item_properties(collection_name, name, properties)
        return properties
