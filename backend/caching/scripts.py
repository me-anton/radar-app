import redis
from backend import settings
from share.metaclasses import Singleton


class RedisScriptsPool(metaclass=Singleton):
    """
    An object for accessing scripts added to redis db
    """
    redis_scripts_folder_address = '/scripts/redis/'

    def __init__(self):
        self.r = redis.Redis(host=settings.REDIS_HOSTNAME)
        self.get_by_pattern = self.register_from_volume('get_by_pattern.lua')

    def register_from_volume(self, script_name: str):
        """
        Register a Lua script from /scripts volume to the Redis db
        and return script callable
        """
        script_address = self.redis_scripts_folder_address + script_name
        with open(script_address, 'r') as script_file:
            script = self.r.register_script(script_file.read())
        return script
