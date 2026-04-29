class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class AssetLicensing
  def self.verify_license(asset_id, license_key)
    if asset_id.nil? || license_key.nil?
      return OmniResult.new(error: "Asset ID and License Key required")
    end
    
    # Ruby business logic for 3D asset licensing in Holodeck
    is_valid = license_key.length > 8
    
    OmniResult.new(value: is_valid)
  end
end
