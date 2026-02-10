# TelerikGrid Patterns

Comprehensive patterns for the Telerik Blazor Grid component covering data binding, configuration, editing, templates, export, and server-side operations.

## Basic Grid Setup with Data Binding

The simplest grid binds a collection to columns defined in Razor markup.

```razor
@page "/orders"

<TelerikGrid Data="@Orders"
             TItem="OrderDto"
             Pageable="true"
             PageSize="20"
             Height="600px">
    <GridColumns>
        <GridColumn Field="@nameof(OrderDto.Id)" Title="Order #" Width="100px" />
        <GridColumn Field="@nameof(OrderDto.CustomerName)" Title="Customer" />
        <GridColumn Field="@nameof(OrderDto.OrderDate)" Title="Date" DisplayFormat="{0:yyyy-MM-dd}" />
        <GridColumn Field="@nameof(OrderDto.Total)" Title="Total" DisplayFormat="{0:C2}" TextAlign="@ColumnTextAlign.Right" />
        <GridColumn Field="@nameof(OrderDto.Status)" Title="Status" />
    </GridColumns>
</TelerikGrid>

@code {
    private List<OrderDto> Orders { get; set; } = new();

    protected override async Task OnInitializedAsync()
    {
        Orders = await OrderService.GetOrdersAsync();
    }
}
```

### Model Definition

```csharp
public class OrderDto
{
    public int Id { get; set; }
    public string CustomerName { get; set; } = string.Empty;
    public DateTime OrderDate { get; set; }
    public decimal Total { get; set; }
    public string Status { get; set; } = string.Empty;
}
```

## Sorting, Filtering, Paging, and Grouping

Enable all standard data operations declaratively on the grid.

```razor
<TelerikGrid Data="@Products"
             TItem="ProductDto"
             Pageable="true"
             PageSize="25"
             Sortable="true"
             SortMode="@SortMode.Multiple"
             FilterMode="@GridFilterMode.FilterRow"
             Groupable="true"
             Resizable="true"
             Reorderable="true"
             Height="700px">
    <GridColumns>
        <GridColumn Field="@nameof(ProductDto.Name)"
                    Title="Product Name"
                    Filterable="true" />
        <GridColumn Field="@nameof(ProductDto.Category)"
                    Title="Category"
                    Filterable="true" />
        <GridColumn Field="@nameof(ProductDto.Price)"
                    Title="Price"
                    DisplayFormat="{0:C2}"
                    TextAlign="@ColumnTextAlign.Right"
                    Filterable="true" />
        <GridColumn Field="@nameof(ProductDto.InStock)"
                    Title="In Stock"
                    Width="120px" />
        <GridColumn Field="@nameof(ProductDto.CreatedDate)"
                    Title="Added"
                    DisplayFormat="{0:d}"
                    Filterable="true" />
    </GridColumns>
</TelerikGrid>
```

### Filter Menu Mode (Advanced Filtering)

For more complex filtering with operators (contains, starts with, greater than, etc.):

```razor
<TelerikGrid Data="@Products"
             TItem="ProductDto"
             FilterMode="@GridFilterMode.FilterMenu"
             Pageable="true"
             Sortable="true">
    <GridColumns>
        <GridColumn Field="@nameof(ProductDto.Name)" Title="Name" />
        <GridColumn Field="@nameof(ProductDto.Price)" Title="Price">
            <FilterMenuTemplate>
                <TelerikNumericTextBox @bind-Value="@((context.FilterDescriptor as FilterDescriptor).Value as decimal?)"
                                       Format="C2" />
            </FilterMenuTemplate>
        </GridColumn>
    </GridColumns>
</TelerikGrid>
```

## Virtual Scrolling for Large Datasets

When the dataset exceeds a few hundred rows, enable virtual scrolling instead of traditional paging.

```razor
<TelerikGrid Data="@LargeDataSet"
             TItem="LogEntryDto"
             ScrollMode="@ScrollMode.Virtual"
             PageSize="40"
             RowHeight="40"
             Height="600px"
             Sortable="true"
             FilterMode="@GridFilterMode.FilterRow">
    <GridColumns>
        <GridColumn Field="@nameof(LogEntryDto.Timestamp)" Title="Time" Width="180px" DisplayFormat="{0:HH:mm:ss.fff}" />
        <GridColumn Field="@nameof(LogEntryDto.Level)" Title="Level" Width="100px" />
        <GridColumn Field="@nameof(LogEntryDto.Message)" Title="Message" />
        <GridColumn Field="@nameof(LogEntryDto.Source)" Title="Source" Width="200px" />
    </GridColumns>
</TelerikGrid>
```

**Key configuration for virtual scrolling:**
- `ScrollMode="@ScrollMode.Virtual"` -- enables the virtual viewport
- `PageSize` -- number of items rendered in the DOM at once (buffer size)
- `RowHeight` -- fixed row height in pixels (required for virtual scroll calculations)
- `Height` -- the grid must have a fixed height

### Virtual Scrolling with Server-Side OnRead

For truly large datasets, combine virtual scrolling with server-side data:

```razor
<TelerikGrid TItem="LogEntryDto"
             OnRead="@OnGridRead"
             ScrollMode="@ScrollMode.Virtual"
             PageSize="40"
             RowHeight="40"
             Height="600px"
             Sortable="true"
             FilterMode="@GridFilterMode.FilterRow">
    <GridColumns>
        <GridColumn Field="@nameof(LogEntryDto.Timestamp)" Title="Time" Width="180px" />
        <GridColumn Field="@nameof(LogEntryDto.Level)" Title="Level" Width="100px" />
        <GridColumn Field="@nameof(LogEntryDto.Message)" Title="Message" />
    </GridColumns>
</TelerikGrid>

@code {
    private async Task OnGridRead(GridReadEventArgs args)
    {
        var request = args.Request;

        var result = await LogService.GetLogsAsync(
            skip: request.Skip,
            take: request.PageSize,
            sort: request.Sorts,
            filters: request.Filters
        );

        args.Data = result.Items;
        args.Total = result.TotalCount;
    }
}
```

## Inline Editing

Allow users to edit cells directly in the grid row.

```razor
<TelerikGrid Data="@Employees"
             TItem="EmployeeDto"
             EditMode="@GridEditMode.Inline"
             Pageable="true"
             PageSize="20"
             OnUpdate="@OnUpdateHandler"
             OnCreate="@OnCreateHandler"
             OnDelete="@OnDeleteHandler"
             Height="600px">
    <GridToolBarTemplate>
        <GridCommandButton Command="Add" Icon="@SvgIcon.Plus">Add Employee</GridCommandButton>
    </GridToolBarTemplate>
    <GridColumns>
        <GridColumn Field="@nameof(EmployeeDto.FirstName)" Title="First Name" />
        <GridColumn Field="@nameof(EmployeeDto.LastName)" Title="Last Name" />
        <GridColumn Field="@nameof(EmployeeDto.Email)" Title="Email" />
        <GridColumn Field="@nameof(EmployeeDto.Department)" Title="Department">
            <EditorTemplate>
                @{
                    var employee = context as EmployeeDto;
                    <TelerikComboBox Data="@Departments"
                                     @bind-Value="@employee.Department"
                                     TextField="Name"
                                     ValueField="Name"
                                     Placeholder="Select department..." />
                }
            </EditorTemplate>
        </GridColumn>
        <GridColumn Field="@nameof(EmployeeDto.HireDate)" Title="Hire Date" DisplayFormat="{0:yyyy-MM-dd}" />
        <GridCommandColumn Width="200px">
            <GridCommandButton Command="Edit" Icon="@SvgIcon.Pencil">Edit</GridCommandButton>
            <GridCommandButton Command="Save" Icon="@SvgIcon.Save" ShowInEdit="true">Save</GridCommandButton>
            <GridCommandButton Command="Cancel" Icon="@SvgIcon.Cancel" ShowInEdit="true">Cancel</GridCommandButton>
            <GridCommandButton Command="Delete" Icon="@SvgIcon.Trash">Delete</GridCommandButton>
        </GridCommandColumn>
    </GridColumns>
</TelerikGrid>

@code {
    private List<EmployeeDto> Employees { get; set; } = new();
    private List<DepartmentDto> Departments { get; set; } = new();

    private async Task OnUpdateHandler(GridCommandEventArgs args)
    {
        var updatedEmployee = (EmployeeDto)args.Item;
        await EmployeeService.UpdateAsync(updatedEmployee);

        var index = Employees.FindIndex(e => e.Id == updatedEmployee.Id);
        if (index >= 0)
        {
            Employees[index] = updatedEmployee;
        }
    }

    private async Task OnCreateHandler(GridCommandEventArgs args)
    {
        var newEmployee = (EmployeeDto)args.Item;
        var created = await EmployeeService.CreateAsync(newEmployee);
        Employees.Insert(0, created);
    }

    private async Task OnDeleteHandler(GridCommandEventArgs args)
    {
        var employee = (EmployeeDto)args.Item;
        await EmployeeService.DeleteAsync(employee.Id);
        Employees.Remove(employee);
    }
}
```

## Popup Editing

Use a popup dialog for editing when the row has many fields or requires a complex form.

```razor
<TelerikGrid Data="@Projects"
             TItem="ProjectDto"
             EditMode="@GridEditMode.Popup"
             Pageable="true"
             OnUpdate="@OnUpdateProject"
             OnCreate="@OnCreateProject"
             Height="600px">
    <GridToolBarTemplate>
        <GridCommandButton Command="Add" Icon="@SvgIcon.Plus">New Project</GridCommandButton>
    </GridToolBarTemplate>
    <GridColumns>
        <GridColumn Field="@nameof(ProjectDto.Name)" Title="Project" />
        <GridColumn Field="@nameof(ProjectDto.Client)" Title="Client" />
        <GridColumn Field="@nameof(ProjectDto.StartDate)" Title="Start" DisplayFormat="{0:d}" />
        <GridColumn Field="@nameof(ProjectDto.Budget)" Title="Budget" DisplayFormat="{0:C0}" />
        <GridCommandColumn Width="180px">
            <GridCommandButton Command="Edit" Icon="@SvgIcon.Pencil">Edit</GridCommandButton>
            <GridCommandButton Command="Save" Icon="@SvgIcon.Save" ShowInEdit="true">Save</GridCommandButton>
            <GridCommandButton Command="Cancel" Icon="@SvgIcon.Cancel" ShowInEdit="true">Cancel</GridCommandButton>
        </GridCommandColumn>
    </GridColumns>
</TelerikGrid>

@code {
    private List<ProjectDto> Projects { get; set; } = new();

    private async Task OnUpdateProject(GridCommandEventArgs args)
    {
        var updated = (ProjectDto)args.Item;
        await ProjectService.UpdateAsync(updated);

        var index = Projects.FindIndex(p => p.Id == updated.Id);
        if (index >= 0)
        {
            Projects[index] = updated;
        }
    }

    private async Task OnCreateProject(GridCommandEventArgs args)
    {
        var created = await ProjectService.CreateAsync((ProjectDto)args.Item);
        Projects.Insert(0, created);
    }
}
```

## Custom Cell Templates and Column Templates

Use templates to render custom content inside grid cells.

### Cell Template (Display Mode)

```razor
<GridColumn Field="@nameof(OrderDto.Status)" Title="Status">
    <Template>
        @{
            var order = (OrderDto)context;
            var badgeClass = order.Status switch
            {
                "Completed" => "k-badge-success",
                "Pending"   => "k-badge-warning",
                "Cancelled" => "k-badge-error",
                _           => "k-badge-info"
            };
        }
        <TelerikBadge Class="@badgeClass" Rounded="@ThemeConstants.Badge.Rounded.Full">
            @order.Status
        </TelerikBadge>
    </Template>
</GridColumn>
```

### Header Template

```razor
<GridColumn Field="@nameof(OrderDto.Total)" Title="Total">
    <HeaderTemplate>
        <span class="k-icon k-i-currency"></span>
        Total (USD)
    </HeaderTemplate>
</GridColumn>
```

### Footer Template with Aggregates

```razor
<TelerikGrid Data="@Orders"
             TItem="OrderDto"
             Pageable="true">
    <GridAggregates>
        <GridAggregate Field="@nameof(OrderDto.Total)" Aggregate="@GridAggregateType.Sum" />
        <GridAggregate Field="@nameof(OrderDto.Total)" Aggregate="@GridAggregateType.Average" />
        <GridAggregate Field="@nameof(OrderDto.Id)" Aggregate="@GridAggregateType.Count" />
    </GridAggregates>
    <GridColumns>
        <GridColumn Field="@nameof(OrderDto.Id)" Title="Order #">
            <FooterTemplate>
                Total Orders: @context.Count
            </FooterTemplate>
        </GridColumn>
        <GridColumn Field="@nameof(OrderDto.Total)" Title="Total" DisplayFormat="{0:C2}">
            <FooterTemplate>
                Sum: @context.Sum?.ToString("C2") | Avg: @context.Average?.ToString("C2")
            </FooterTemplate>
        </GridColumn>
    </GridColumns>
</TelerikGrid>
```

### Detail Row Template (Master-Detail)

```razor
<TelerikGrid Data="@Customers"
             TItem="CustomerDto"
             Pageable="true">
    <DetailTemplate>
        @{
            var customer = (CustomerDto)context;
        }
        <TelerikGrid Data="@customer.Orders"
                     TItem="OrderDto"
                     Pageable="true"
                     PageSize="5">
            <GridColumns>
                <GridColumn Field="@nameof(OrderDto.Id)" Title="Order #" />
                <GridColumn Field="@nameof(OrderDto.OrderDate)" Title="Date" DisplayFormat="{0:d}" />
                <GridColumn Field="@nameof(OrderDto.Total)" Title="Total" DisplayFormat="{0:C2}" />
            </GridColumns>
        </TelerikGrid>
    </DetailTemplate>
    <GridColumns>
        <GridColumn Field="@nameof(CustomerDto.Name)" Title="Customer" />
        <GridColumn Field="@nameof(CustomerDto.Email)" Title="Email" />
        <GridColumn Field="@nameof(CustomerDto.TotalOrders)" Title="Orders" />
    </GridColumns>
</TelerikGrid>
```

## Export to Excel and PDF

### Excel Export

```razor
<TelerikGrid @ref="@GridRef"
             Data="@Reports"
             TItem="ReportDto"
             Pageable="true">
    <GridToolBarTemplate>
        <GridCommandButton Command="ExcelExport" Icon="@SvgIcon.FileExcel">Export to Excel</GridCommandButton>
    </GridToolBarTemplate>
    <GridExcelExport FileName="report-export" AllPages="true" />
    <GridColumns>
        <GridColumn Field="@nameof(ReportDto.Category)" Title="Category" />
        <GridColumn Field="@nameof(ReportDto.Revenue)" Title="Revenue" DisplayFormat="{0:C2}" />
        <GridColumn Field="@nameof(ReportDto.Units)" Title="Units Sold" />
        <GridColumn Field="@nameof(ReportDto.Period)" Title="Period" />
    </GridColumns>
</TelerikGrid>

@code {
    private TelerikGrid<ReportDto> GridRef { get; set; } = default!;
}
```

### PDF Export

```razor
<TelerikGrid Data="@Invoices"
             TItem="InvoiceDto"
             Pageable="true">
    <GridToolBarTemplate>
        <GridCommandButton Command="ExcelExport" Icon="@SvgIcon.FileExcel">Excel</GridCommandButton>
        <GridCommandButton OnClick="@ExportToPdf" Icon="@SvgIcon.FilePdf">PDF</GridCommandButton>
    </GridToolBarTemplate>
    <GridExcelExport FileName="invoices" AllPages="true" />
    <GridColumns>
        <GridColumn Field="@nameof(InvoiceDto.InvoiceNumber)" Title="Invoice #" />
        <GridColumn Field="@nameof(InvoiceDto.Client)" Title="Client" />
        <GridColumn Field="@nameof(InvoiceDto.Amount)" Title="Amount" DisplayFormat="{0:C2}" />
        <GridColumn Field="@nameof(InvoiceDto.DueDate)" Title="Due Date" DisplayFormat="{0:d}" />
    </GridColumns>
</TelerikGrid>

@code {
    private async Task ExportToPdf()
    {
        // Use Telerik Document Processing or browser print for PDF
        await JsRuntime.InvokeVoidAsync("window.print");
    }
}
```

## Grid State Persistence

Save and restore grid state (filters, sorts, page, column widths) across sessions.

```razor
<TelerikGrid @ref="@GridRef"
             Data="@Items"
             TItem="ItemDto"
             Pageable="true"
             Sortable="true"
             FilterMode="@GridFilterMode.FilterRow"
             Resizable="true"
             Reorderable="true"
             OnStateInit="@OnGridStateInit"
             OnStateChanged="@OnGridStateChanged"
             Height="600px">
    <GridColumns>
        <GridColumn Field="@nameof(ItemDto.Name)" Title="Name" />
        <GridColumn Field="@nameof(ItemDto.Category)" Title="Category" />
        <GridColumn Field="@nameof(ItemDto.Price)" Title="Price" DisplayFormat="{0:C2}" />
    </GridColumns>
</TelerikGrid>

@code {
    private TelerikGrid<ItemDto> GridRef { get; set; } = default!;
    private List<ItemDto> Items { get; set; } = new();

    private const string GridStateKey = "ItemsGridState";

    private async Task OnGridStateInit(GridStateEventArgs<ItemDto> args)
    {
        var savedState = await LocalStorage.GetItemAsync<GridState<ItemDto>>(GridStateKey);
        if (savedState is not null)
        {
            args.GridState = savedState;
        }
    }

    private async Task OnGridStateChanged(GridStateEventArgs<ItemDto> args)
    {
        await LocalStorage.SetItemAsync(GridStateKey, args.GridState);
    }
}
```

**Dependencies for state persistence:**
- Use `Blazored.LocalStorage` or `ProtectedLocalStorage` for storing the serialized grid state
- The `GridState<T>` object contains sort descriptors, filter descriptors, page info, column widths, and column order

## Server-Side Operations with OnRead

The `OnRead` event handler enables pushing all data operations to the server, which is essential for large datasets.

### Basic OnRead Pattern

```razor
<TelerikGrid TItem="CustomerDto"
             OnRead="@OnCustomerGridRead"
             Pageable="true"
             PageSize="25"
             Sortable="true"
             FilterMode="@GridFilterMode.FilterRow"
             Height="600px">
    <GridColumns>
        <GridColumn Field="@nameof(CustomerDto.Name)" Title="Name" />
        <GridColumn Field="@nameof(CustomerDto.Email)" Title="Email" />
        <GridColumn Field="@nameof(CustomerDto.City)" Title="City" />
        <GridColumn Field="@nameof(CustomerDto.LifetimeValue)" Title="LTV" DisplayFormat="{0:C2}" />
    </GridColumns>
    <NoDataTemplate>
        <p>No customers found matching your criteria.</p>
    </NoDataTemplate>
</TelerikGrid>

@code {
    private async Task OnCustomerGridRead(GridReadEventArgs args)
    {
        var request = args.Request;

        try
        {
            var result = await CustomerService.GetPagedAsync(new PagedRequest
            {
                Skip = request.Skip,
                Take = request.PageSize,
                SortDescriptors = request.Sorts,
                FilterDescriptors = request.Filters
            });

            args.Data = result.Items;
            args.Total = result.TotalCount;
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Failed to load customer grid data");
            args.Data = Enumerable.Empty<CustomerDto>();
            args.Total = 0;
            NotificationService.Show("Failed to load data. Please try again.", "Error");
        }
    }
}
```

### Server-Side Service Implementation

```csharp
public class CustomerService
{
    private readonly ApplicationDbContext _context;

    public CustomerService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<PagedResult<CustomerDto>> GetPagedAsync(PagedRequest request)
    {
        var query = _context.Customers.AsNoTracking();

        // Apply Telerik filters using the DataSourceRequest extensions
        // Or manually translate filters to LINQ:
        if (request.FilterDescriptors?.Any() == true)
        {
            query = ApplyFilters(query, request.FilterDescriptors);
        }

        // Apply sorting
        if (request.SortDescriptors?.Any() == true)
        {
            query = ApplySorts(query, request.SortDescriptors);
        }
        else
        {
            query = query.OrderBy(c => c.Name); // default sort
        }

        var totalCount = await query.CountAsync();

        var items = await query
            .Skip(request.Skip)
            .Take(request.Take)
            .Select(c => new CustomerDto
            {
                Id = c.Id,
                Name = c.Name,
                Email = c.Email,
                City = c.City,
                LifetimeValue = c.LifetimeValue
            })
            .ToListAsync();

        return new PagedResult<CustomerDto>
        {
            Items = items,
            TotalCount = totalCount
        };
    }
}
```

### Using Telerik DataSourceRequest Extensions

Telerik provides extension methods to apply `DataSourceRequest` directly to `IQueryable`:

```csharp
using Telerik.DataSource;
using Telerik.DataSource.Extensions;

public async Task<DataEnvelope<CustomerDto>> GetCustomersAsync(DataSourceRequest request)
{
    var query = _context.Customers
        .AsNoTracking()
        .Select(c => new CustomerDto
        {
            Id = c.Id,
            Name = c.Name,
            Email = c.Email,
            City = c.City,
            LifetimeValue = c.LifetimeValue
        });

    var result = await query.ToDataSourceResultAsync(request);

    return new DataEnvelope<CustomerDto>
    {
        Data = result.Data.Cast<CustomerDto>().ToList(),
        Total = result.Total
    };
}
```

## Selection Modes

### Single Row Selection

```razor
<TelerikGrid Data="@Items"
             TItem="ItemDto"
             SelectionMode="@GridSelectionMode.Single"
             SelectedItems="@SelectedItems"
             SelectedItemsChanged="@OnSelectionChanged"
             Pageable="true">
    <GridColumns>
        <GridColumn Field="@nameof(ItemDto.Name)" Title="Name" />
        <GridColumn Field="@nameof(ItemDto.Description)" Title="Description" />
    </GridColumns>
</TelerikGrid>

<div class="detail-panel">
    @if (SelectedItems.Any())
    {
        var selected = SelectedItems.First();
        <h4>@selected.Name</h4>
        <p>@selected.Description</p>
    }
    else
    {
        <p>Select an item to view details.</p>
    }
</div>

@code {
    private List<ItemDto> Items { get; set; } = new();
    private IEnumerable<ItemDto> SelectedItems { get; set; } = Enumerable.Empty<ItemDto>();

    private void OnSelectionChanged(IEnumerable<ItemDto> items)
    {
        SelectedItems = items;
    }
}
```

### Multiple Row Selection with Checkbox

```razor
<TelerikGrid Data="@Tasks"
             TItem="TaskDto"
             SelectionMode="@GridSelectionMode.Multiple"
             @bind-SelectedItems="@SelectedTasks"
             Pageable="true">
    <GridColumns>
        <GridCheckboxColumn SelectAll="true" Width="50px" />
        <GridColumn Field="@nameof(TaskDto.Title)" Title="Task" />
        <GridColumn Field="@nameof(TaskDto.Priority)" Title="Priority" />
        <GridColumn Field="@nameof(TaskDto.DueDate)" Title="Due" DisplayFormat="{0:d}" />
    </GridColumns>
    <GridToolBarTemplate>
        <TelerikButton OnClick="@BulkComplete"
                        Enabled="@SelectedTasks.Any()"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
            Complete Selected (@SelectedTasks.Count())
        </TelerikButton>
        <TelerikButton OnClick="@BulkDelete"
                        Enabled="@SelectedTasks.Any()"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Error">
            Delete Selected
        </TelerikButton>
    </GridToolBarTemplate>
</TelerikGrid>

@code {
    private List<TaskDto> Tasks { get; set; } = new();
    private IEnumerable<TaskDto> SelectedTasks { get; set; } = Enumerable.Empty<TaskDto>();

    private async Task BulkComplete()
    {
        var ids = SelectedTasks.Select(t => t.Id).ToList();
        await TaskService.BulkCompleteAsync(ids);
        SelectedTasks = Enumerable.Empty<TaskDto>();
        // Refresh grid
    }

    private async Task BulkDelete()
    {
        var ids = SelectedTasks.Select(t => t.Id).ToList();
        await TaskService.BulkDeleteAsync(ids);
        Tasks.RemoveAll(t => ids.Contains(t.Id));
        SelectedTasks = Enumerable.Empty<TaskDto>();
    }
}
```

## Loading and Empty State Patterns

Always provide visual feedback during data operations.

```razor
<TelerikLoaderContainer Visible="@IsLoading" Text="Loading data...">
    <TelerikGrid Data="@Data"
                 TItem="RecordDto"
                 Pageable="true"
                 Height="600px">
        <GridColumns>
            <GridColumn Field="@nameof(RecordDto.Name)" Title="Name" />
            <GridColumn Field="@nameof(RecordDto.Value)" Title="Value" />
        </GridColumns>
        <NoDataTemplate>
            <div style="padding: 2rem; text-align: center;">
                <TelerikSvgIcon Icon="@SvgIcon.InfoCircle" Size="@ThemeConstants.SvgIcon.Size.ExtraLarge" />
                <p>No records found. Adjust your filters or add a new record.</p>
            </div>
        </NoDataTemplate>
    </TelerikGrid>
</TelerikLoaderContainer>

@code {
    private List<RecordDto> Data { get; set; } = new();
    private bool IsLoading { get; set; } = true;

    protected override async Task OnInitializedAsync()
    {
        try
        {
            IsLoading = true;
            Data = await RecordService.GetAllAsync();
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Failed to load records");
            NotificationService.Show("Could not load records. Please refresh.", "Error");
        }
        finally
        {
            IsLoading = false;
        }
    }
}
```

## Column Chooser and Dynamic Columns

Let users toggle column visibility at runtime.

```razor
<TelerikGrid Data="@Inventory"
             TItem="InventoryDto"
             Pageable="true"
             ColumnMenu="true"
             Height="600px">
    <GridColumns>
        <GridColumn Field="@nameof(InventoryDto.Sku)" Title="SKU" VisibleInColumnChooser="false" />
        <GridColumn Field="@nameof(InventoryDto.ProductName)" Title="Product" />
        <GridColumn Field="@nameof(InventoryDto.Warehouse)" Title="Warehouse" />
        <GridColumn Field="@nameof(InventoryDto.Quantity)" Title="Qty" />
        <GridColumn Field="@nameof(InventoryDto.ReorderPoint)" Title="Reorder At" Visible="false" />
        <GridColumn Field="@nameof(InventoryDto.LastRestocked)" Title="Last Restocked" Visible="false" DisplayFormat="{0:d}" />
        <GridColumn Field="@nameof(InventoryDto.UnitCost)" Title="Unit Cost" Visible="false" DisplayFormat="{0:C2}" />
    </GridColumns>
</TelerikGrid>
```

**Notes:**
- `ColumnMenu="true"` adds a menu icon to each column header with sort, filter, and column chooser options
- `Visible="false"` hides the column by default but allows users to show it via the column chooser
- `VisibleInColumnChooser="false"` prevents a column from appearing in the chooser (useful for ID or key columns that must always be visible)

## Conditional Row Styling

Apply CSS classes to rows based on data conditions.

```razor
<TelerikGrid Data="@Orders"
             TItem="OrderDto"
             Pageable="true"
             OnRowRender="@OnRowRenderHandler"
             Height="600px">
    <GridColumns>
        <GridColumn Field="@nameof(OrderDto.Id)" Title="Order #" />
        <GridColumn Field="@nameof(OrderDto.Status)" Title="Status" />
        <GridColumn Field="@nameof(OrderDto.Total)" Title="Total" DisplayFormat="{0:C2}" />
    </GridColumns>
</TelerikGrid>

@code {
    private void OnRowRenderHandler(GridRowRenderEventArgs args)
    {
        var order = (OrderDto)args.Item;

        args.Class = order.Status switch
        {
            "Overdue" => "row-overdue",
            "Cancelled" => "row-cancelled",
            "Completed" => "row-completed",
            _ => string.Empty
        };
    }
}
```

```css
/* Component-scoped or global CSS */
.row-overdue {
    background-color: var(--kendo-color-error-subtle);
}

.row-cancelled {
    opacity: 0.6;
    text-decoration: line-through;
}

.row-completed {
    background-color: var(--kendo-color-success-subtle);
}
```
