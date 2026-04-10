# SKILL: BUSINESS LAYER — GraphQL, C#, Ruby, PHP
**File:** `languages/SKILL_layer_business.md`  
**Layer:** Languages  
**Bahasa:** GraphQL · C# · Ruby · PHP

---

## Peran Domain

Business Layer menangani semua logika bisnis, kontrak data API, aturan domain, dan routing. Ini adalah otak dari aplikasi — tempat semua keputusan bisnis dibuat.

| Bahasa | Keunggulan | Kapan Digunakan |
|--------|-----------|-----------------|
| **GraphQL** | Schema-first, type-safe query, introspection | API contract, data federation, mobile-friendly API |
| **C#** | DDD pattern, CQRS, enterprise-grade OOP | Domain aggregate, command handler, event sourcing |
| **Ruby** | Expressive DSL, convention-over-config, routing | REST routing, config DSL, admin panel |
| **PHP** | Web lifecycle, legacy bridge, WordPress-compatible | CMS backend, legacy integration, web hooks |

---

## GraphQL — Idiom OMNI

```omni
// Schema sebagai kontrak data — single source of truth
@schema
type Order {
  id: UUID!
  customer: Customer!
  line_items: [LineItem!]!
  total: Money!
  status: OrderStatus!
  created_at: DateTime!
}

type Query {
  order(id: UUID!): Order
  orders(
    customer_id: UUID,
    status: OrderStatus,
    limit: Int = 20,
    offset: Int = 0
  ): [Order!]!
}

type Mutation {
  create_order(input: CreateOrderInput!): Result_Order_OrderError!
  cancel_order(id: UUID!, reason: String): Result_Order_OrderError!
}

// Subscription untuk real-time update
type Subscription {
  order_status_changed(customer_id: UUID!): Order!
}
```

---

## C# — Idiom OMNI (DDD + CQRS)

```omni
// Domain Aggregate — jaga invariant bisnis
cs::domain class Order {
  private id: UUID
  private items: List<OrderItem>
  private status: OrderStatus

  // Constructor private — hanya bisa dibuat via factory
  static fn create(customer: CustomerId, items: Vec<OrderItem>)
    -> Result<Order, OrderError> {
    if items.is_empty() {
      return Err(OrderError::EmptyOrder)
    }
    Ok(Order { id: UUID::new(), items, status: OrderStatus::Draft })
  }

  // Command — ubah state dengan validasi
  fn confirm() -> Result<OrderConfirmed, OrderError> {
    match self.status {
      OrderStatus::Draft => {
        self.status = OrderStatus::Confirmed
        Ok(OrderConfirmed { order_id: self.id })
      }
      _ => Err(OrderError::InvalidTransition(self.status))
    }
  }
}

// Command Handler
cs::domain fn handle_confirm_order(
  cmd: ConfirmOrderCommand,
  repo: &OrderRepository
) -> Result<(), OrderError> {
  let order = repo.get(cmd.order_id)?
  let event = order.confirm()?
  repo.save(order)?
  emit_event(event)
}
```

---

## Ruby — Idiom OMNI (Routing DSL)

```omni
// Declarative routing — bersih dan ekspresif
rb::route "/api/v1" {
  resources :orders {
    get    "/"           -> cs::domain::OrderQuery::list
    get    "/:id"        -> cs::domain::OrderQuery::find
    post   "/"           -> cs::domain::OrderCommand::create
    put    "/:id/confirm" -> cs::domain::OrderCommand::confirm
    delete "/:id"        -> cs::domain::OrderCommand::cancel
  }

  scope "/admin" {
    middleware :authenticate_admin
    get "/dashboard" -> AdminQuery::dashboard_stats
    get "/users"     -> AdminQuery::list_users
  }
}

// DSL untuk konfigurasi fitur
rb::config feature_flags {
  enable :new_checkout_flow if env("ENABLE_NEW_CHECKOUT") == "true"
  enable :ai_recommendations if env("AI_SERVICE_URL").present?
  disable :legacy_payment_gateway
}
```

---

## PHP — Idiom OMNI (Web Lifecycle & Legacy Bridge)

```omni
// Web request handler
php::web fn handle_webhook(req: HttpRequest) -> HttpResponse {
  let signature = req.headers.get("X-Signature")?
  verify_webhook_signature(signature, req.body)?

  let payload = json::parse::<WebhookPayload>(req.body)?
  match payload.event_type {
    "payment.success" => process_payment_success(payload.data),
    "payment.failed"  => process_payment_failed(payload.data),
    _                 => Ok(()),
  }?

  HttpResponse::ok("Webhook processed")
}

// Bridge ke CMS legacy
php::web fn sync_product_from_cms(product_id: i64) -> Result<Product, SyncError> {
  let legacy = php::wordpress::get_post(product_id)?
  Ok(Product {
    id:    UUID::from_int(legacy.ID),
    name:  legacy.post_title,
    price: Money::from_str(&legacy.meta["price"])?,
  })
}
```

---

## Aturan Business Layer

1. Domain aggregate DILARANG berkomunikasi langsung dengan database — harus melalui Repository pattern
2. GraphQL schema adalah kontrak — jangan ubah tipe field yang sudah ada, hanya tambah field baru (API evolution)
3. Ruby routing HANYA boleh berisi routing — tidak ada business logic di dalam blok route
4. PHP HANYA untuk web request lifecycle — jangan gunakan PHP untuk komputasi CPU-intensive

---

*ANTIGRAVITY Skills — languages/SKILL_layer_business.md*
