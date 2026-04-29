module OmniCasbin
  class Enforcer
    def enforce(sub, obj, act)
      Omni::Result.ok(true)
    end
  end
end
