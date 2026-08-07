# Invoice Agent (Agent Faktury)

An n8n workflow for automated analysis of invoices stored in a **PostgreSQL (Supabase)** database. An AI agent gathers the report requirements through a chat conversation, generates an HTML report (KPIs, top line items, highest-value invoices, detected anomalies), sends it to an operator for review, and — once approved — forwards it to the final recipient. A rejection triggers a revision loop.

## How it works

1. **Start the conversation** — the operator types a message in the n8n chat (e.g. *"generate a report"*). The first agent (`AI Agent1`) asks for:
   - the date range,
   - the counterparty (all companies / a specific one),
   - the type of analysis (totals, anomalies, top items, or everything).

   The operator's answers become the context for the rest of the flow.

2. **SQL analysis** — a second agent (`AI Agent`), with access to a Postgres tool, builds and runs its own SQL queries dynamically (rather than four fixed queries). It always checks:
   - the number of invoices and net/VAT/gross totals for the period,
   - the top 5 most frequent line items,
   - the top 5 highest-value invoices,
   - anomalies (invoices with no line items, zero-amount items, mismatches between `total_gross` and the sum of `gross_value`).

   Based on the results, it generates an HTML report.

3. **Operator review** — the generated report is emailed to the operator for approval, and the n8n chat prompts for approval/rejection (`sendAndWait`, double-approval mode).

4. **Approval** — the report is sent in a final email to the recipient.

5. **Rejection** — the rejection (along with the operator's comments) is logged in the database, and the agent generates a revised version of the report, taking the operator's feedback into account. The review cycle repeats until the report is approved.

## Architecture (n8n)

```
When chat message received
        │
        ▼
   AI Agent1  ──(asks for date range / counterparty / analysis type)
        │  ↔ OpenRouter Chat Model1
        │  ↔ Postgres Chat Memory
        ▼
      Chat1  (sendAndWait — passes the answers along)
        │
        ▼
    AI Agent  ──(builds and runs SQL queries, creates the HTML report)
        │  ↔ OpenRouter Chat Model
        │  ↔ Postgres Chat Memory1
        │  ↔ Execute a SQL query in Postgres (ai_tool, $fromAI query)
        ▼
  Code in JavaScript  (packages the result as html_report)
        │
        ▼
    Send an Email1  (email to operator: "FOR REVIEW")
        │
        ▼
       Chat  (sendAndWait — asks for approval in the n8n chat)
        │
        ▼
         If (approved == true?)
        ┌──────────────┴───────────────┐
     YES│                             NO│
        ▼                               ▼
  Send an Email             Execute a SQL query (logs rejection)
  (final report                    +
   to recipient)          Code in JavaScript1 (appends operator's notes)
                                   │
                                   ▼
                              AI Agent (loop — new report version)
```

## Tech stack

- **n8n** — workflow orchestration (`@n8n/n8n-nodes-langchain.agent`, `chatTrigger`, `sendAndWait`)
- **OpenRouter** — the LLM powering both AI agents
- **PostgreSQL / Supabase** — invoice database + chat memory (`memoryPostgresChat`) + rejection log (`report_logs`)
- **Email (MailerSend)** — sends the report for review and to the final recipient

## Database schema

### `invoices`
| Column | Type | Description |
|---|---|---|
| id | BIGINT | primary key |
| invoice_number | TEXT | invoice number |
| issue_date | DATE | issue date |
| sale_date | DATE | sale date |
| payment_due_date | DATE | payment due date |
| payment_method | TEXT | payment method |
| seller_name | TEXT | seller name |
| seller_nip | TEXT | seller tax ID (NIP) |
| buyer_name | TEXT | buyer name |
| buyer_nip | TEXT | buyer tax ID (NIP) |
| total_net | NUMERIC | net amount |
| total_vat | NUMERIC | VAT amount |
| total_gross | NUMERIC | gross amount |
| currency | TEXT | currency (default PLN) |
| created_at | TIMESTAMPTZ | record creation timestamp |

### `invoice_line_items`
| Column | Type | Description |
|---|---|---|
| id | BIGINT | primary key |
| invoice_id | BIGINT | FK to `invoices.id` |
| lp | INTEGER | line item sequence number |
| name | TEXT | item name |
| quantity | NUMERIC | quantity |
| unit | TEXT | unit of measure |
| net_price | NUMERIC | net unit price |
| net_value | NUMERIC | net value |
| vat_rate | TEXT | VAT rate |
| vat_value | NUMERIC | VAT value |
| gross_value | NUMERIC | gross value |
| created_at | TIMESTAMPTZ | record creation timestamp |

### `report_logs`
Logs report rejections (status, generation timestamp, report period, rejection reason) — used to keep a history of revisions.

## SQL generation rules

The SQL agent's system message enforces a consistent query style, including:
- filtering company names with `ILIKE`,
- filtering dates by the `issue_date` column,
- always using table aliases (`invoices AS i`, `invoice_line_items AS li`),
- prefixing every column with its table alias,
- no `SELECT *`,
- every column in `SELECT` must appear in `GROUP BY` or an aggregate function.

> Every query error encountered is appended to the agent's system message so the same mistake isn't repeated in future runs.

## Setup

1. Import `Agent_Faktury.json` into your n8n instance.
2. Configure credentials:
   - **Postgres/Supabase** — connection to the invoice database as well as the chat memory table (`n8n_chat_memory`) and the log table (`report_logs`),
   - **OpenRouter** — API key for both `OpenRouter Chat Model` nodes,
   - **Email (SMTP/MailerSend)** — sender/recipient addresses in the `Send an Email` and `Send an Email1` nodes.
3. Fill in the operator/recipient email addresses in the email node parameters.
4. Run the workflow and start a conversation in the n8n chat.

## Known limitations / future work

- Dynamic SQL generation by the agent can be unstable — execution errors occasionally occur and are patched ad hoc by extending the system message.
- The report revision process is iterative and may repeat several times before approval.
- Worth considering: validating/sanitizing the SQL queries generated via `$fromAI` before execution.
