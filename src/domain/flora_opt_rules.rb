module Omni
  module FloraOpt
    def self.validate_flora(params)
      if params.empty?
        return { status: 'error', msg: 'Params empty' }
      end
      { status: 'ok', data: true }
    end
  end
end
