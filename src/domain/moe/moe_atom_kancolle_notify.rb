# moe_atom_kancolle_notify.rb — Domain
# Layer: Domain — Atom Kancolle Notification Router
# Inspired by: atom-kancolle (Fleet girls' voice notifications)

module Omni
  module Domain
    class KancolleNotification
      attr_reader :ship_girl_id, :event_type, :audio_path

      # Maps IDE events to specific voice lines
      EVENT_MAP = {
        build_success: "success.wav",
        build_fail: "fail.wav",
        test_pass: "cheer.wav",
        startup: "greeting.wav"
      }.freeze

      def initialize(ship_girl_id)
        @ship_girl_id = ship_girl_id
        @base_path = "/assets/voices/kancolle/#{ship_girl_id}"
      end

      # Domain Rule: Route the IDE event to the correct media asset
      def generate_notification(event_type)
        file_name = EVENT_MAP[event_type.to_sym]
        raise ArgumentError, "Unknown IDE event type: #{event_type}" unless file_name

        @audio_path = "#{@base_path}/#{file_name}"
        
        {
          character: @ship_girl_id,
          event: event_type,
          audio_uri: @audio_path,
          timestamp: Time.now.to_i
        }
      end
    end
  end
end
