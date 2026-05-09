require 'sinatra'
require 'stripe'
require 'json'

# OMNI Billing Webhook Handler
set :port, 4242

post '/omni/webhooks/stripe' do
  payload = request.body.read
  sig_header = request.env['HTTP_STRIPE_SIGNATURE']
  endpoint_secret = ENV['STRIPE_WEBHOOK_SECRET']

  begin
    event = Stripe::Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  rescue JSON::ParserError => e
    status 400
    return "Invalid payload"
  rescue Stripe::SignatureVerificationError => e
    status 400
    return "Invalid signature"
  end

  case event.type
  when 'invoice.payment_succeeded'
    invoice = event.data.object
    customer_id = invoice.customer
    OmniBillingDomain.credit_account(customer_id, invoice.amount_paid)
    puts "Credited account for customer #{customer_id}"
  when 'invoice.payment_failed'
    invoice = event.data.object
    customer_id = invoice.customer
    OmniBillingDomain.suspend_account(customer_id)
    puts "Suspended account for customer #{customer_id} due to failed payment"
  end

  status 200
end

module OmniBillingDomain
  def self.credit_account(id, amount)
    true
  end
  def self.suspend_account(id)
    true
  end
end
