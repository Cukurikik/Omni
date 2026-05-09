# @omni-layer Business | @omni-source Yachay-AI/byt5-geotagging | @omni-lang Ruby
# @omni-description Geolocation service: domain layer for coordinate prediction
# tracking, region classification, and prediction accuracy analytics.

module OmniGeoService
  class OmniResult
    attr_reader :data, :error
    def initialize(data: nil, error: nil); @data = data; @error = error; end
    def ok?; @error.nil?; end
  end

  class GeoRegion
    attr_accessor :name, :min_lat, :max_lat, :min_lon, :max_lon
    def initialize(name:, bounds:)
      @name = name
      @min_lat, @max_lat = bounds[:lat]
      @min_lon, @max_lon = bounds[:lon]
    end

    def contains?(lat, lon)
      lat >= @min_lat && lat <= @max_lat && lon >= @min_lon && lon <= @max_lon
    end
  end

  class GeoPrediction
    attr_accessor :text, :latitude, :longitude, :confidence, :region, :timestamp
    def initialize(text:, lat:, lon:, confidence:, region: nil)
      @text = text; @latitude = lat; @longitude = lon
      @confidence = confidence; @region = region; @timestamp = Time.now
    end
  end

  class GeoLocationService
    REGIONS = [
      GeoRegion.new(name: "North America", bounds: { lat: [15, 72], lon: [-170, -50] }),
      GeoRegion.new(name: "Europe", bounds: { lat: [35, 72], lon: [-25, 45] }),
      GeoRegion.new(name: "East Asia", bounds: { lat: [18, 55], lon: [100, 150] }),
      GeoRegion.new(name: "South America", bounds: { lat: [-56, 15], lon: [-82, -34] }),
      GeoRegion.new(name: "Africa", bounds: { lat: [-35, 37], lon: [-18, 52] }),
      GeoRegion.new(name: "Oceania", bounds: { lat: [-50, 0], lon: [110, 180] }),
    ].freeze

    def initialize
      @predictions = []
    end

    def record_prediction(text:, lat:, lon:, confidence:)
      region = REGIONS.find { |r| r.contains?(lat, lon) }&.name || "Unknown"
      pred = GeoPrediction.new(text: text, lat: lat, lon: lon, confidence: confidence, region: region)
      @predictions << pred
      OmniResult.new(data: { text: text, lat: lat, lon: lon, region: region, confidence: confidence })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def accuracy_report(ground_truths)
      errors = []
      @predictions.each_with_index do |pred, i|
        next unless ground_truths[i]
        gt = ground_truths[i]
        dist = haversine(pred.latitude, pred.longitude, gt[:lat], gt[:lon])
        errors << dist
      end
      return OmniResult.new(error: "No predictions") if errors.empty?
      OmniResult.new(data: {
        n_predictions: errors.size,
        mean_error_km: errors.sum / errors.size,
        median_error_km: errors.sort[errors.size / 2],
        accuracy_100km: errors.count { |e| e < 100 }.to_f / errors.size,
        accuracy_500km: errors.count { |e| e < 500 }.to_f / errors.size,
      })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def region_distribution
      dist = @predictions.group_by(&:region).transform_values(&:size)
      OmniResult.new(data: dist)
    end

    private

    def haversine(lat1, lon1, lat2, lon2)
      r = 6371.0
      dlat = (lat2 - lat1) * Math::PI / 180
      dlon = (lon2 - lon1) * Math::PI / 180
      a = Math.sin(dlat/2)**2 + Math.cos(lat1*Math::PI/180) * Math.cos(lat2*Math::PI/180) * Math.sin(dlon/2)**2
      r * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    end
  end
end
