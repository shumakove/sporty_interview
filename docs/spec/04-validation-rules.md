# 4. Validation Rules

## 4.1 Stake Validation (UI and API)

| Field | Rule                                  | Layer    | Expected Result                          |
|-------|---------------------------------------|----------|------------------------------------------|
| Stake | Required to place bet                 | UI + API | Placement blocked/rejected if missing    |
| Stake | Must be numeric                       | UI + API | Reject non-numeric values                |
| Stake | Minimum €1.01 (positive values)       | UI + API | Show/reject with minimum message         |
| Stake | Maximum €100.00                       | UI + API | Show/reject with maximum message         |
| Stake | Max 2 decimal places                  | UI + API | Reject invalid precision                 |
| Stake | Must not exceed available balance     | UI + API | Show/reject as insufficient balance      |

## 4.2 Selection and Match Validation

| Field     | Rule                                   | Layer    | Expected Result                        |
|-----------|----------------------------------------|----------|----------------------------------------|
| Selection | Required                               | UI + API | Placement blocked/rejected if missing  |
| Selection | Must be one of `HOME`, `DRAW`, `AWAY`  | API      | Reject invalid values                  |
| Match ID  | Required and non-empty                 | API      | Reject missing/blank value             |
| Match ID  | Must exist in match catalog            | API      | Reject unknown match                   |

## 4.3 Request/Protocol Validation

| Rule                                        | Layer | Expected Result                        |
|---------------------------------------------|-------|----------------------------------------|
| Request body must be valid JSON object      | API   | Reject malformed/non-object payloads   |
| Unsupported HTTP method                     | API   | Return method-not-allowed response     |
| Missing/invalid user context (`x-user-id`)  | API   | Reject as unauthorized                 |

## 4.4 UI Error Messaging (minimum expected copy)

- `Minimum stake is €1.00`
- `Maximum stake is €100.00`
- `Insufficient balance`

UI input format behavior:

- Stake input accepts numeric values with a single decimal separator and up to 2 decimal
  places.
