# Incremental Sync Implementation

## Overview

The Jubelio connector now supports incremental sync for the **Orders** and **Contacts** streams, allowing for efficient data replication by only fetching new or updated records since the last sync.

## Supported Streams

### Orders Stream
- **Cursor Field**: `last_modified`
- **API Parameter**: `lastModifiedSince`
- **Endpoint**: `/sales/orders/`
- **Description**: Fetches only orders modified since the last sync timestamp

### Contacts Stream
- **Cursor Field**: `last_modified`
- **API Parameter**: `createdSince`
- **Endpoint**: `/contacts/`
- **Description**: Fetches only contacts created since the last sync timestamp

## Not Supported

### Products Stream
- **Reason**: While the schema includes a `last_modified` field, the `/inventory/items/` endpoint does not support temporal filtering parameters
- **Behavior**: Remains as a full refresh stream

### Categories Stream
- **Reason**: No temporal fields in the schema and no API filtering parameters
- **Behavior**: Remains as a full refresh stream

## Implementation Details

### Base Incremental Class

The `IncrementalJubelioStream` class extends the base `JubelioStream` and implements the `IncrementalMixin` to provide:

- **State Management**: Tracks the last cursor value between syncs
- **Request Parameter Injection**: Automatically adds temporal filter parameters to API requests
- **State Updates**: Updates the cursor value based on the latest record processed

### State Format

```json
{
  "last_modified": "2023-12-01T10:30:00Z"
}
```

### API Integration

- **Orders**: Uses `lastModifiedSince` parameter to filter orders
- **Contacts**: Uses `createdSince` parameter to filter contacts
- **Date Format**: ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`)

## Benefits

1. **Performance**: Significantly reduces API calls and data transfer
2. **Efficiency**: Only processes new/updated records
3. **Cost Optimization**: Reduces API usage for large datasets
4. **Fresh Data**: Ensures latest changes are captured in each sync

## Testing

Comprehensive test coverage includes:
- State management verification
- Request parameter injection
- Pagination with incremental sync
- Edge cases (missing cursor fields)
- Full backward compatibility

## Usage

No configuration changes are required. The incremental sync is automatically enabled for supported streams when running in incremental mode. The connector will:

1. Start with a full sync if no state exists
2. Use the cursor value from the state for subsequent syncs
3. Update the state with the latest cursor value after each sync

## Monitoring

Monitor incremental sync effectiveness by:
- Checking state updates between syncs
- Verifying API requests include temporal parameters
- Observing reduced record counts in incremental syncs vs full refresh