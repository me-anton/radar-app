--[[
    Get a json string that represents what has to be changed in given KEYS array
    :param KEYS:    all the already known keys
    :param ARGV[1]: the maximum number of live keys that have to be processed
    :param ARGV[2]: pattern for the new keys
    :returns json object reply:
        reply.dropped_keys: array of keys that were deleted or expired and
                            have to be deleted from known keys
        reply.new_records: object with key-value pairs that have to be added to
                           known keys
]]
local reply = {}
reply.dropped_keys = {}
reply.new_records = {}
local max_relevant_keys = tonumber(ARGV[1])
local keys_to_add = max_relevant_keys - #KEYS

-- find all the dropped keys
for _, key in ipairs(KEYS) do
    if redis.call("EXISTS", key) == 0 then
        table.insert(reply.dropped_keys, key)
        keys_to_add = keys_to_add + 1
    end
end

-- if there is a need to add more keys - find them
if keys_to_add > 0 then
    local full = false
    local cursor = 0
    local records_count = 0
    local more_keys = {}

    -- create a "set" for KEYS for fast contains() functionality
    local known_keys_contain = {}
    for _, key in ipairs(KEYS) do
        known_keys_contain[key] = true
    end

    -- search for new keys and add them to reply.new_keys
    repeat
        cursor, more_keys = unpack(redis.call("SCAN", cursor,
                                              "MATCH", ARGV[2],
                                              "COUNT", max_relevant_keys))
        for _, key in ipairs(more_keys) do
            if not known_keys_contain[key] then
                reply.new_records[key] = redis.call("GET", key)
                records_count = records_count + 1
                if records_count == keys_to_add then
                    full = true
                    break
                end
            end
        end
    until full or cursor == "0"
end

return cjson.encode(reply)
