# 5. Backend API

## 5.1 Authentication / User Context

All API endpoints require:

- Header: `x-user-id: <string>`

## 5.2 API Documentation

- Swagger UI: `/api/docs`
- OpenAPI JSON: `/api/docs?format=json`

## 5.3 Endpoints

### `GET /api/matches`

Returns match list.

**200 response**

```ts
id: string
competition: string
kickoffDate: string        // YYYY-MM-DD
homeTeam: string
awayTeam: string
odds: { home: number; draw: number; away: number }
```

### `GET /api/balance`

Returns user balance.

**200 response**

```ts
balance: number
currency: "EUR"
```

### `POST /api/place-bet`

Places one bet.

**Request body**

```ts
matchId: string
selection: "HOME" | "DRAW" | "AWAY"
stake: number
```

Extra fields may be ignored by the API.

**200 response**

```ts
message: string
matchId: string
selection: "HOME" | "DRAW" | "AWAY"
stake: number
odds: number
payout: number
balance: number
currency: "EUR"
```

**Expected error classes**

| Status | Meaning                                            |
|--------|----------------------------------------------------|
| 400    | malformed payload                                  |
| 401    | unauthorized user context                          |
| 405    | method not allowed                                 |
| 409    | bet already in progress (same user)                |
| 422    | semantic validation failures (selection/stake/match) |
| 500    | unexpected server failure                          |

### `POST /api/reset-balance`

Resets user balance to initial configured value.

**200 response**

```ts
message: string
balance: number
currency: "EUR"
```

Response body and persisted state must be consistent after reset.
