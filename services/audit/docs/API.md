# Audit Service API

## Health Check

### GET /health

Checks whether the Audit Service is running.

Response:

```json
{
  "status": "ok",
  "service": "audit"
}
```

## Authentication Event Model

Authentication events use the following schema:

```json
{
  "event_id": "uuid",
  "event_type": "login_success",
  "user_id": "uuid",
  "organization_id": "uuid",
  "ip_address": "192.168.1.10",
  "user_agent": "Mozilla/5.0",
  "timestamp": "2026-08-24T20:00:00Z",
  "metadata": {}
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| event_id | string | Unique event identifier |
| event_type | string | Authentication event type |
| user_id | string | User associated with the event |
| organization_id | string | Organization associated with the event |
| ip_address | string | Source IP address |
| user_agent | string | Client user agent |
| timestamp | datetime | Event occurrence time |
| metadata | object | Additional event information |

## Kafka

Topic: `audit-events`

Broker: `kafka:9092`

Kafka event processing will be implemented in a later milestone.
