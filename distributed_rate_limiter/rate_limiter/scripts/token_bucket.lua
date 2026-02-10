-- Token Bucket (Redis + Lua)
-- KEYS[1] bucket key
-- ARGV[1] now_ms
-- ARGV[2] rate_per_sec
-- ARGV[3] burst
-- ARGV[4] cost
-- ARGV[5] ttl_seconds
--
-- Hash fields: tokens (float), ts_ms (int)
-- Return: {allowed(1/0), tokens_remaining(float), retry_after_ms(int)}

local key = KEYS[1]
local now_ms = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local burst = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])
local ttl = tonumber(ARGV[5])

local data = redis.call('HMGET', key, 'tokens', 'ts_ms')
local tokens = tonumber(data[1])
local last_ms = tonumber(data[2])

if tokens == nil or last_ms == nil then
  tokens = burst
  last_ms = now_ms
end

local delta_ms = now_ms - last_ms
if delta_ms < 0 then delta_ms = 0 end

local refill = (delta_ms / 1000.0) * rate
tokens = tokens + refill
if tokens > burst then tokens = burst end

local allowed = 0
local retry_after_ms = 0

if tokens >= cost then
  allowed = 1
  tokens = tokens - cost
else
  allowed = 0
  local deficit = cost - tokens
  retry_after_ms = math.ceil((deficit / rate) * 1000.0)
end

redis.call('HSET', key, 'tokens', tokens, 'ts_ms', now_ms)
redis.call('EXPIRE', key, ttl)

return {allowed, tokens, retry_after_ms}
