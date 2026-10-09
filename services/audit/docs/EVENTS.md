# Audit Event Contracts

## Overview

The Audit Service receives audit events from services that generate security, identity, and organization-related activity.

Events use a common schema so that authentication, organization, membership, workspace, and project activity can be recorded consistently.

## Kafka Strategy

The Audit Service uses a single Kafka topic for audit events.

- Broker: `kafka:9092`
- Topic: `audit-events`

Identity Service and Organization Service publish audit events to the `audit-events` topic.

The Audit Service consumes events from this topic.

The `event_type` field identifies the type of event being recorded.

## Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "user.login",
  "event_version": "1.0",
  "service_name": "identity",
  "user_id": "uuid",
  "tenant_id": "uuid",
  "organization_id": "uuid",
  "workspace_id": "uuid",
  "project_id": "uuid",
  "resource_type": "user",
  "resource_id": "uuid",
  "action": "login",
  "status": "success",
  "ip_address": "192.168.1.10",
  "user_agent": "Mozilla/5.0",
  "request_id": "uuid",
  "timestamp": "2026-09-07T10:00:00Z",
  "metadata":  {}
}
## Core Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `event_id` | string | Yes | Unique identifier for the event |
| `event_type` | string | Yes | Identifies the event category and operation |
| `event_version` | string | Yes | Version of the event contract |
| `service_name` | string | Yes | Service that generated the event |
| `user_id` | string | Conditional | User associated with the event |
| `tenant_id` | string | Required* | Tenant context used by Identity Service |
| `organization_id` | string | Required* | Organization associated with the event |
| `workspace_id` | string | Conditional | Workspace associated with the event |
| `project_id` | string | Conditional | Project associated with the event |
| `resource_type` | string | No | Type of resource affected |
| `resource_id` | string | No | Identifier of the affected resource |
| `action` | string | Yes | Operation performed |
| `status` | string | Yes | Result of the operation |
| `ip_address` | string | No | Source IP address |
| `user_agent` | string | No | Client user-agent |
| `request_id` | string | No | Identifier used to trace a request |
| `timestamp` | datetime | Yes | Time the event occurred |
| `metadata` | object | No | Additional event-specific information |

## Tenant Context

Identity Service currently defines `tenant_id` for users and sessions.

Organization-related database structures use `organization_id`.

The Audit Service keeps `tenant_id` and `organization_id` as separate fields because the repository does not currently define a mapping between the two identifiers.

An event must contain at least one of `tenant_id` or `organization_id`.

## Authentication Events

| Event Type | Service | Action |
|---|---|---|
| `user.registered` | identity | register |
| `user.login` | identity | login |
| `user.logout` | identity | logout |
| `token.refreshed` | identity | refresh |
| `mfa.verified` | identity | verify |

Authentication events should include `user_id` where available.

Identity events should include `tenant_id` when tenant context is available.

Authentication events involving client requests may also include `ip_address`, `user_agent`, and `request_id`.

## Organization Events

| Event Type | Service | Action |
|---|---|---|
| `organization.created` | organization | create |
| `organization.updated` | organization | update |
| `organization.deleted` | organization | delete |

Organization events should include `organization_id`.

## Membership Events

| Event Type | Service | Action |
|---|---|---|
| `membership.created` | organization | create |
| `membership.updated` | organization | update |
| `membership.deleted` | organization | delete |

Membership events should include:

- `user_id`
- `organization_id`
- `workspace_id`

## Workspace Events

| Event Type | Service | Action |
|---|---|---|
| `workspace.created` | organization | create |
| `workspace.updated` | organization | update |
| `workspace.deleted` | organization | delete |

Workspace events should include:

- `organization_id`
- `workspace_id`

## Project Events

| Event Type | Service | Action |
|---|---|---|
| `project.created` | organization | create |
| `project.updated` | organization | update |
| `project.deleted` | organization | delete |

Project events should include:

- `organization_id`
- `workspace_id`
- `project_id`

The project database model directly references `workspace_id`, while the workspace references `organization_id`. Both identifiers should therefore be included in project audit events to preserve tenant context.

## Producer Expectations

Identity and Organization services are expected to publish events to the `audit-events` Kafka topic.

Producers should:

1. Generate a unique `event_id`.
2. Set the appropriate `event_type`.
3. Set `event_version`.
4. Identify the originating service with `service_name`.
5. Include applicable user and tenant/organization context.
6. Include the affected resource identifiers when applicable.
7. Set the action and operation status.
8. Include request metadata when available.
9. Set the event timestamp.

## Consumer Expectations

The Audit Service consumer is responsible for receiving events from the `audit-events` topic.

Before an event is recorded, the consumer should validate the required event fields and tenant/organization context.

Invalid events should be rejected rather than recorded as valid audit events.

Detailed event processing, persistence, and hash-chain handling will be implemented in later integration work.

## Event Versioning

The `event_version` field allows the event contract to evolve without ambiguity.

Producers and consumers should use the event version when interpreting event payloads.

The initial contract version is `1.0`.

