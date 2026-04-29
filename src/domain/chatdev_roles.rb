module Omni
  module ChatDev
    def self.assign_role(role)
      if role.empty?
        return { status: 'error', msg: 'Role empty' }
      end
      { status: 'ok', data: role }
    end
  end
end
