import redis
from backend import settings
from share.metaclasses import Singleton


class RedisScriptsPool(metaclass=Singleton):
    """
    An object for accessing scripts added to redis db
    """
    redis_scripts_folder_address = '/scripts/redis/'

    def __init__(self):
        self._redis = redis.Redis(host=settings.REDIS_HOSTNAME)
        self.get_by_pattern = self.register_from_volume('get_by_pattern.lua')
        """
        Get values of all keys matching the specified pattern
        :param args[1]: maximum iterations of looking for keys.
                    1 iteration finds 10 or less corresponding keys.
        :param args[2]: keys pattern
        """

        self.update_records = self.register_from_volume('update_records.lua')
        """
        Get a json string that represents what has to be changed in given keys 
        array
        :param keys:    all the already known keys
        :param args[1]: the maximum number of live keys that have to be processed
        :param args[2]: pattern for the new keys
        :returns json object reply:
            reply.dropped_keys: array of keys that were deleted or expired and 
                                have to be deleted from known keys
            reply.new_records: object with key-value pairs that have to be added 
                               to known keys  
        """

    def register_from_volume(self, script_name: str):
        """
        Register a Lua script from /scripts volume to the Redis db
        and return script callable
        """
        script_address = self.redis_scripts_folder_address + script_name
        with open(script_address, 'r') as script_file:
            script = self._redis.register_script(script_file.read())
        return script
