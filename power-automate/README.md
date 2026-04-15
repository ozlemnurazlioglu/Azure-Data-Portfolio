# Power Automate - Business Process Automation Flows

## Overview

Three production-ready Power Automate flows demonstrating enterprise automation patterns:
SharePoint integration, approval workflows, and scheduled data processing.

---

## Flow 1: Sales Report Auto-Generator

**Trigger**: Scheduled (Every Monday 8:00 AM)

### Flow Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Scheduled   │     │  Get Items   │     │   Apply to   │     │  Create      │
│  Trigger     ├────►│  from        ├────►│   Each Row   ├────►│  Excel       │
│  (Weekly)    │     │  SharePoint  │     │   + Filter   │     │  Table       │
└──────────────┘     │  List        │     └──────────────┘     └──────┬───────┘
                     └──────────────┘                                  │
                                                                       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Send Email  │◄────┤  Post to     │◄────┤  Upload to   │◄────┤  Format      │
│  with Link   │     │  Teams       │     │  SharePoint  │     │  Report      │
└──────────────┘     │  Channel     │     │  Document    │     │  Workbook    │
                     └──────────────┘     │  Library     │     └──────────────┘
                                          └──────────────┘
```

### Actions Detail

| Step | Action | Configuration |
|------|--------|---------------|
| 1 | Recurrence | Frequency: Week, Interval: 1, Day: Monday, Time: 08:00 |
| 2 | Get Items | Site: Sales Team Site, List: Weekly Sales Data |
| 3 | Filter Array | `@greaterOrEquals(items('Apply_to_each')?['OrderDate'], addDays(utcNow(), -7))` |
| 4 | Select | Map columns: OrderID, Customer, Product, Amount, Region |
| 5 | Create Table | Excel Online → Create table in pre-formatted template |
| 6 | Add Rows | Loop through filtered items, add to Excel table |
| 7 | Create File | Upload completed Excel to SharePoint Document Library |
| 8 | Post Message | Teams → Sales Channel → "Weekly report ready: [link]" |
| 9 | Send Email | To: sales-managers@company.com with Excel attachment |

### Expression Examples Used

```
// Filter orders from last 7 days
@greaterOrEquals(
    items('Apply_to_each')?['OrderDate'],
    addDays(utcNow(), -7)
)

// Calculate total revenue
@mul(
    items('Apply_to_each')?['Quantity'],
    items('Apply_to_each')?['UnitPrice']
)

// Dynamic file name
@concat('WeeklySalesReport_', formatDateTime(utcNow(), 'yyyy-MM-dd'), '.xlsx')
```

---

## Flow 2: Purchase Order Approval Workflow

**Trigger**: When an item is created in SharePoint List "Purchase Orders"

### Flow Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐
│  SharePoint  │     │  Initialize  │     │  Condition:          │
│  Trigger:    ├────►│  Variables   ├────►│  Amount > $5,000?    │
│  New Item    │     │              │     └──────────┬───────────┘
└──────────────┘     └──────────────┘           Yes  │  No
                                                 │    │
                                    ┌────────────┘    └────────────┐
                                    ▼                              ▼
                            ┌──────────────┐             ┌──────────────┐
                            │ Multi-Level  │             │ Single       │
                            │ Approval     │             │ Approval     │
                            │ (Manager +   │             │ (Manager     │
                            │  Director)   │             │  Only)       │
                            └──────┬───────┘             └──────┬───────┘
                                   │                            │
                                   └──────────┬─────────────────┘
                                              ▼
                            ┌──────────────────────────────┐
                            │  Condition: Approved?         │
                            └──────────┬───────────────────┘
                                  Yes  │  No
                              ┌────────┘  └────────┐
                              ▼                    ▼
                     ┌──────────────┐     ┌──────────────┐
                     │ Update SP    │     │ Update SP    │
                     │ Status:      │     │ Status:      │
                     │ "Approved"   │     │ "Rejected"   │
                     │ + Send Email │     │ + Send Email │
                     │ + Post Teams │     │ + Post Teams │
                     └──────────────┘     └──────────────┘
```

### Key Configuration

| Parameter | Value |
|-----------|-------|
| SharePoint List | Purchase Orders |
| Threshold for Multi-Level | $5,000 |
| First Approver | Direct Manager (from Azure AD) |
| Second Approver | Department Director (from SharePoint lookup) |
| Timeout | 7 days per approval level |
| Escalation | Auto-escalate to VP after timeout |

### Approval Email Template

```html
<h2>Purchase Order Approval Request</h2>
<table>
  <tr><td><b>PO Number:</b></td><td>@{triggerOutputs()?['body/PONumber']}</td></tr>
  <tr><td><b>Requester:</b></td><td>@{triggerOutputs()?['body/Requester/DisplayName']}</td></tr>
  <tr><td><b>Amount:</b></td><td>$@{triggerOutputs()?['body/TotalAmount']}</td></tr>
  <tr><td><b>Vendor:</b></td><td>@{triggerOutputs()?['body/VendorName']}</td></tr>
  <tr><td><b>Description:</b></td><td>@{triggerOutputs()?['body/Description']}</td></tr>
</table>
<p>Please review and approve/reject this purchase order.</p>
```

---

## Flow 3: Data Pipeline Monitor & Alert

**Trigger**: Scheduled (Every 30 minutes)

### Flow Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Scheduled   │     │  HTTP:       │     │  Parse JSON  │     │ Condition:   │
│  Trigger     ├────►│  Call Azure  ├────►│  Response    ├────►│ Pipeline     │
│  (30 min)    │     │  Synapse API │     │              │     │ Failed?      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                  Yes │  No
                                                              ┌───────┘  └──┐
                                                              ▼             ▼
                                                     ┌──────────────┐  ┌─────────┐
                                                     │ Create       │  │ Log     │
                                                     │ Incident in  │  │ Success │
                                                     │ SharePoint + │  │ to SP   │
                                                     │ Alert Teams  │  │ List    │
                                                     │ + Email      │  └─────────┘
                                                     └──────────────┘
```

### HTTP Action Configuration

```json
{
    "method": "GET",
    "uri": "https://<synapse-workspace>.dev.azuresynapse.net/pipelineruns?api-version=2020-12-01",
    "authentication": {
        "type": "ManagedServiceIdentity",
        "audience": "https://dev.azuresynapse.net"
    },
    "queries": {
        "lastUpdatedAfter": "@{addMinutes(utcNow(), -30)}",
        "lastUpdatedBefore": "@{utcNow()}"
    }
}
```

---

## Implementation Guide

### Prerequisites
- Microsoft 365 license with Power Automate
- SharePoint site with required lists
- Azure AD for user lookups
- Teams channels for notifications

### SharePoint Lists Required

**Weekly Sales Data List**:
| Column | Type |
|--------|------|
| OrderID | Single line text |
| CustomerName | Single line text |
| Product | Choice |
| Quantity | Number |
| UnitPrice | Currency |
| OrderDate | Date |
| Region | Choice |

**Purchase Orders List**:
| Column | Type |
|--------|------|
| PONumber | Auto-generated |
| Requester | Person |
| VendorName | Single line text |
| TotalAmount | Currency |
| Description | Multiple lines |
| Status | Choice (Pending/Approved/Rejected) |
| ApproverComments | Multiple lines |

### Deployment Steps

1. Create SharePoint lists with the schemas above
2. In Power Automate portal, create flows from blank
3. Add connectors: SharePoint, Office 365 Outlook, Microsoft Teams, Excel Online
4. Configure each action following the diagrams above
5. Test with sample data
6. Enable and monitor via Power Automate analytics
