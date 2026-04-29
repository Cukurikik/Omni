# hackingBuddyGPT — Pentest Report Routes
class HackingBuddyRoutes
  MAX_TARGETS = 50
  MAX_REPORT_SIZE = 1_000_000

  def self.create_target(params)
    return { ok: false, error: "Missing target IP" } unless params[:ip]
    return { ok: false, error: "Missing target name" } unless params[:name]
    { ok: true, value: { id: SecureRandom.uuid, ip: params[:ip], name: params[:name] } }
  end

  def self.generate_report(target_id, findings)
    return { ok: false, error: "Missing target ID" } unless target_id
    return { ok: false, error: "No findings" } if findings.nil? || findings.empty?
    return { ok: false, error: "Findings exceed limit" } if findings.length > 10000
    { ok: true, value: { target_id: target_id, finding_count: findings.length } }
  end
end
