# SIUDES - API & Database Contract

## 1. Database Schemas (Isolated)

### A. db_siudes_unit (Laravel 13)
- `unit_tariffs`: `id`(PK), `unit_type`(UNIQUE: AIR | SAMPAH | ALSINTAN), `unit_name`(Varchar), `tariff_rate`(NUMERIC(14,2)), `unit_measure`(Varchar: m3, bulan, jam), `timestamps`
- `customers`: `id`(PK), `customer_code`(UNIQUE: PLG-001), `name`(Varchar), `address`(Text), `phone`(Varchar), `timestamps`
- `usage_records`: `id`(PK), `event_id`(UUID, UNIQUE), `customer_id`(FK), `unit_type`(Varchar), `usage_amount`(NUMERIC(10,2)), `tariff_rate`(NUMERIC(14,2)), `total_amount`(NUMERIC(14,2)), `recorded_at`(TIMESTAMPTZ), `timestamps`

### B. db_siudes_finance (FastAPI)
-`invoices`: `id`(PK), `invoice_code`(UNIQUE: INV-202611-0001), `event_id`(UUID, UNIQUE), `customer_code`(Varchar), `unit_type`(Varchar), `usage_amount`(NUMERIC(10,2)), `tariff_rate`(NUMERIC(14,2)), `total_amount`(NUMERIC(14,2)), `status`(Varchar: UNPAID / PAID), `issued_at`(TIMESTAMPTZ), `paid_at`(TIMESTAMPTZ, NULLABLE)
- `payment_logs`: `id`(PK), `invoice_id`(FK, UNIQUE), `paid_by_role`(Varchar), `amount_paid`(NUMERIC(14,2)), `paid_at`(TIMESTAMPTZ)

## 2. REST API Endpoints (Via Nginx Port 8081)

### Unit Service (/api/unit/*)”- `GET - /api/unit/master` [Role: ADMIN_UNIT, KASIR, KEPALA_DESA]
  Response: `{"success":true,"data":{"tariffs":[...],"customers":[...]},"error":null}`
- `POST /api/unit/usage` [Role: ADMIN_UNIT]
  Body: `{"customer_code":"PLG-001","unit_type":"AIR","usage_amount":15.5}`
  Response (201): `{"success":true,"data":{"event_id":"...","total_amount":38750.00},"error":null}`

### Finance Service (/api/finance/*)”- `GET - /api/finance/invoices` [Role: KASIR, KEPALA_DETA - query: ?status=UNPAID]
  Response: `{"success":true,"data":[...],"error":null}`
- `POST - /api/finance/invoices/{invoice_code}/pay` [Role: KASIR]
  Response: (200): `{"success":true,"data":{"invoice_code":"INV-...","status":"PAID","paid_at":"..."},"error":null}`
  Error (409): `{"success":false,"data":null,"error":{"code":"ALREADY_PAID","message":"Tagihan sudah lunas"}}`
- `GET GET - /api/finance/summary` [Role: KEPALA_DESA, KASIR]
  Response: `{"success":true,"data":{"total_revenue":"150000.00","total_unpaid":"75000.00","by_unit":{}},"error":null}`
- `GET /api/finance/stream` [SSE Stream]
  Event: `invoice_updated` -> {"success":true,"data":{"invoice_code":"...","status":"..."}}`
