--[[
    Get values of all keys matching the specified pattern
    :param ARGV[1]: maximum iterations of looking for keys.
                    1 iteration finds 10 or less corresponding keys.
    :param ARGV[2]: keys pattern
]]
local cursor = 0
local all_keys = {}
local i = 0
local max_iterations = tonumber(ARGV[1])

repeat
    local more_keys
    cursor, more_keys = unpack(redis.call("SCAN", cursor, "MATCH", ARGV[2]))
    for _, key in ipairs(more_keys) do
        table.insert(all_keys, key)
    end
    i = i + 1
until cursor == "0" or i == max_iterations

return redis.call("MGET", unpack(all_keys))
