# Power Apps - Inventory Management System

## Overview

A Canvas App for managing product inventory with full CRUD operations, connected to SharePoint/Dataverse as the backend data source. Designed for warehouse staff and inventory managers.

## App Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Power Apps Canvas App                     │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │  Home    │  │ Products │  │  Add/Edit │  │ Dashboard │ │
│  │  Screen  │  │  Gallery │  │  Form    │  │  Screen   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬─────┘ │
│       │              │              │               │       │
└───────┼──────────────┼──────────────┼───────────────┼───────┘
        │              │              │               │
        └──────────────┴──────┬───────┴───────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Data Source       │
                    │   (SharePoint List  │
                    │    or Dataverse)    │
                    └────────────────────┘
```

## Screens

### 1. Home Screen
- Company logo and app title
- Navigation buttons to each section
- Quick stats: Total Products, Low Stock Alerts, Recent Updates
- User greeting with `User().FullName`

### 2. Product Gallery Screen
- Scrollable gallery of all products
- Search bar with real-time filtering
- Sort by: Name, Category, Stock Level, Last Updated
- Color-coded stock indicators (Green: OK, Yellow: Low, Red: Critical)
- Swipe to delete (with confirmation)

### 3. Add/Edit Product Form
- Product Name (text input, required)
- Category (dropdown: Electronics, Furniture, Office Supplies, Clothing, Food & Beverage)
- SKU (auto-generated: `"SKU-" & Text(CountRows(Products) + 1, "0000")`)
- Quantity in Stock (number input)
- Reorder Level (number input)
- Unit Price (currency input)
- Supplier (dropdown from Suppliers list)
- Location (dropdown: Warehouse A, Warehouse B, Warehouse C)
- Image (camera/upload)
- Notes (multiline text)

### 4. Dashboard Screen
- Total Inventory Value: `Sum(Products, Quantity * UnitPrice)`
- Products Below Reorder Level (count + gallery)
- Category Breakdown (pie chart)
- Stock Movement Trend (line chart - last 30 days)

## Key Formulas

### Search & Filter
```
// Gallery Items with search and filter
Sort(
    Filter(
        Products,
        SearchInput.Text in ProductName
        || SearchInput.Text in Category
        || SearchInput.Text in SKU,
        If(!IsBlank(CategoryFilter.Selected.Value),
            Category = CategoryFilter.Selected.Value,
            true
        )
    ),
    Switch(SortDropdown.Selected.Value,
        "Name", ProductName,
        "Stock", QuantityInStock,
        "Price", UnitPrice,
        "Updated", ModifiedDate
    ),
    If(SortOrder.Value = "Desc", SortOrder.Descending, SortOrder.Ascending)
)
```

### Submit New Product
```
// OnSelect for Save button
If(
    EditForm.Mode = FormMode.New,
    Patch(
        Products,
        Defaults(Products),
        {
            ProductName: txtProductName.Text,
            Category: ddCategory.Selected.Value,
            SKU: "SKU-" & Text(CountRows(Products) + 1, "0000"),
            QuantityInStock: Value(txtQuantity.Text),
            ReorderLevel: Value(txtReorderLevel.Text),
            UnitPrice: Value(txtUnitPrice.Text),
            Supplier: ddSupplier.Selected.Value,
            Location: ddLocation.Selected.Value,
            Notes: txtNotes.Text,
            CreatedBy: User().FullName,
            CreatedDate: Now()
        }
    ),
    Patch(
        Products,
        BrowseGallery.Selected,
        {
            ProductName: txtProductName.Text,
            Category: ddCategory.Selected.Value,
            QuantityInStock: Value(txtQuantity.Text),
            ReorderLevel: Value(txtReorderLevel.Text),
            UnitPrice: Value(txtUnitPrice.Text),
            Supplier: ddSupplier.Selected.Value,
            Location: ddLocation.Selected.Value,
            Notes: txtNotes.Text,
            ModifiedBy: User().FullName,
            ModifiedDate: Now()
        }
    )
);
Notify("Product saved successfully!", NotificationType.Success);
Navigate(ProductGalleryScreen, ScreenTransition.UnCoverRight)
```

### Delete with Confirmation
```
// OnSelect for Delete button
If(
    Confirm("Are you sure you want to delete " & ThisItem.ProductName & "?"),
    Remove(Products, ThisItem);
    Notify("Product deleted.", NotificationType.Warning)
)
```

### Low Stock Alert Indicator
```
// Fill color for stock indicator icon
If(
    ThisItem.QuantityInStock <= ThisItem.ReorderLevel * 0.5,
    Color.Red,
    If(
        ThisItem.QuantityInStock <= ThisItem.ReorderLevel,
        Color.Orange,
        Color.Green
    )
)
```

### Dashboard KPIs
```
// Total Inventory Value
Text(
    Sum(Products, QuantityInStock * UnitPrice),
    "$#,##0.00"
)

// Low Stock Count
CountIf(Products, QuantityInStock <= ReorderLevel)

// Category with Most Products
First(
    Sort(
        GroupBy(Products, "Category", "CategoryGroup"),
        CountRows(CategoryGroup),
        SortOrder.Descending
    )
).Category
```

## Data Source Schema

### SharePoint List: "Products"

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| ProductName | Single line text | Yes | Product display name |
| Category | Choice | Yes | Product category |
| SKU | Single line text | Yes | Auto-generated stock keeping unit |
| QuantityInStock | Number | Yes | Current stock level |
| ReorderLevel | Number | Yes | Threshold for reorder alert |
| UnitPrice | Currency | Yes | Price per unit |
| Supplier | Lookup (Suppliers list) | No | Supplier reference |
| Location | Choice | No | Warehouse location |
| ProductImage | Image | No | Product photo |
| Notes | Multiple lines | No | Additional notes |
| CreatedBy | Single line text | Auto | Record creator |
| CreatedDate | Date | Auto | Creation timestamp |
| ModifiedBy | Single line text | Auto | Last modifier |
| ModifiedDate | Date | Auto | Last modification |

### SharePoint List: "Suppliers"

| Column | Type | Description |
|--------|------|-------------|
| SupplierName | Single line text | Company name |
| ContactPerson | Single line text | Primary contact |
| Email | Single line text | Contact email |
| Phone | Single line text | Contact phone |
| LeadTimeDays | Number | Average delivery time |

### SharePoint List: "StockMovements" (Audit Trail)

| Column | Type | Description |
|--------|------|-------------|
| ProductID | Lookup | Reference to product |
| MovementType | Choice (In/Out/Adjustment) | Type of stock change |
| Quantity | Number | Units moved |
| PreviousStock | Number | Stock before change |
| NewStock | Number | Stock after change |
| Reason | Single line text | Movement reason |
| PerformedBy | Person | Who made the change |
| MovementDate | Date | When it happened |

## Integration with Power Automate

The app triggers a Power Automate flow when stock falls below reorder level:

```
Flow Trigger: When QuantityInStock <= ReorderLevel
Actions:
  1. Send email to procurement team
  2. Create item in "Purchase Requests" SharePoint list
  3. Post adaptive card in Teams for quick approval
  4. Update product status to "Reorder Pending"
```

## Responsive Design

- **Tablet Layout**: 1366x768 (primary)
- **Phone Layout**: 640x1136 (secondary)
- Uses containers for responsive positioning
- Horizontal/Vertical containers with `LayoutMode.Auto`

## Deployment

1. Create SharePoint lists with schemas above
2. Import the app package into Power Apps
3. Update data source connections
4. Share with security group
5. Add to Teams as a tab (optional)
