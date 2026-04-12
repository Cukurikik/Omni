-- ==========================================
-- 🌍 OMNI EDGE CDN Lua Proxy (Phase 25)
-- ==========================================
-- Digunakan untuk mem-bypass Node.js/Go dan langsung mem-serve
-- AST Response Statik dari level Nginx / OpenResty.

local redis = require "resty.redis"
local cjson = require "cjson"

local function serve_from_cache()
    local red = redis:new()
    red:set_timeout(100) -- 100ms timeout
    
    local ok, err = red:connect("127.0.0.1", 6379)
    if not ok then
        -- Redis mati, teruskan ke Golang Telepathy Router
        ngx.log(ngx.WARN, "Redis down, fallback to OMNI Go Core")
        return ngx.exit(ngx.DECLINED)
    end

    local cache_key = "omni_ast_cache:" .. ngx.var.request_uri
    local res, err = red:get(cache_key)
    
    if res == ngx.null then
        -- Miss, proxy ke backend
        ngx.ctx.cache_key = cache_key
        return ngx.exit(ngx.DECLINED)
    else
        -- Hit! Bypass 15 bahasa, langsung serve dari memory.
        ngx.header.content_type = "application/json"
        ngx.header["X-Omni-Edge"] = "HIT-LUA"
        ngx.say(res)
        
        red:set_keepalive(10000, 100)
        return ngx.exit(ngx.OK)
    end
end

-- Eksekusi Utama
serve_from_cache()
