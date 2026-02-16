# 4D Forms to Blazor UI Migration

## Form Type Mapping

| 4D Form Type | Blazor Equivalent | Telerik Component |
|--------------|-------------------|-------------------|
| Input form | Edit page/component | TelerikForm, TelerikTextBox |
| List form | Grid page | TelerikGrid |
| Print form | Report | TelerikReportViewer |
| Dialog | Modal window | TelerikWindow, TelerikDialog |
| Subform | Child component | Nested component |
| Tab form | Tabbed layout | TelerikTabStrip |
| List box | Dropdown/ListView | TelerikDropDownList, TelerikListView |
| Pop-up menu | Context menu | TelerikContextMenu |
| Calendar | Date picker | TelerikDatePicker, TelerikScheduler |

## Input Form → Blazor Edit Form

### 4D Input Form
```
// 4D form with text fields, dropdowns, buttons
[FirstName] - Text input
[LastName] - Text input
[Department] - Pop-up menu (dropdown)
[HireDate] - Date field
[Salary] - Number field
[Save Button] - Calls method "SaveEmployee"
[Cancel Button] - Closes form
```

### Blazor Equivalent
```razor
@page "/employees/edit/{Id:int?}"
@inject IMediator Mediator
@inject NavigationManager Navigation

<TelerikForm Model="@employee" OnValidSubmit="@HandleSubmit">
    <FormValidation>
        <DataAnnotationsValidator />
    </FormValidation>

    <FormItems>
        <FormItem Field="@nameof(Employee.FirstName)" LabelText="First Name">
            <Template>
                <TelerikTextBox @bind-Value="@employee.FirstName" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(Employee.LastName)" LabelText="Last Name">
            <Template>
                <TelerikTextBox @bind-Value="@employee.LastName" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(Employee.DepartmentId)" LabelText="Department">
            <Template>
                <TelerikDropDownList Data="@departments"
                                     @bind-Value="@employee.DepartmentId"
                                     TextField="Name"
                                     ValueField="Id"
                                     DefaultText="Select Department..." />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(Employee.HireDate)" LabelText="Hire Date">
            <Template>
                <TelerikDatePicker @bind-Value="@employee.HireDate" Format="MM/dd/yyyy" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(Employee.Salary)" LabelText="Salary">
            <Template>
                <TelerikNumericTextBox @bind-Value="@employee.Salary"
                                       Format="C2"
                                       Min="0" />
            </Template>
        </FormItem>
    </FormItems>

    <FormButtons>
        <TelerikButton ButtonType="ButtonType.Submit" ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
            Save
        </TelerikButton>
        <TelerikButton ButtonType="ButtonType.Button" OnClick="@HandleCancel">
            Cancel
        </TelerikButton>
    </FormButtons>
</TelerikForm>

@code {
    [Parameter] public int? Id { get; set; }

    private EmployeeDto employee = new();
    private List<DepartmentDto> departments = new();

    protected override async Task OnInitializedAsync()
    {
        departments = await Mediator.Send(new GetDepartmentListQuery());

        if (Id.HasValue)
        {
            employee = await Mediator.Send(new GetEmployeeByIdQuery(Id.Value));
        }
    }

    private async Task HandleSubmit()
    {
        if (Id.HasValue)
        {
            await Mediator.Send(new UpdateEmployeeCommand(Id.Value, employee));
        }
        else
        {
            await Mediator.Send(new CreateEmployeeCommand(employee));
        }

        Navigation.NavigateTo("/employees");
    }

    private void HandleCancel()
    {
        Navigation.NavigateTo("/employees");
    }
}
```

## List Form → Telerik Grid

### 4D List Form
```
// 4D list form showing records
[ID] - Column
[FirstName] - Column
[LastName] - Column
[Department] - Column (relation display)
[HireDate] - Column
[Edit Button] - Opens input form
[Delete Button] - Deletes record
```

### Blazor Equivalent
```razor
@page "/employees"
@inject IMediator Mediator

<TelerikGrid Data="@employees"
             TItem="EmployeeListDto"
             Pageable="true"
             PageSize="20"
             Sortable="true"
             FilterMode="GridFilterMode.FilterRow"
             OnRead="@OnGridRead"
             Height="600px">

    <GridToolBarTemplate>
        <GridCommandButton Command="Add" Icon="@SvgIcon.Plus">Add Employee</GridCommandButton>
    </GridToolBarTemplate>

    <GridColumns>
        <GridColumn Field="@nameof(EmployeeListDto.Id)" Title="ID" Width="80px" />
        <GridColumn Field="@nameof(EmployeeListDto.FirstName)" Title="First Name" />
        <GridColumn Field="@nameof(EmployeeListDto.LastName)" Title="Last Name" />
        <GridColumn Field="@nameof(EmployeeListDto.DepartmentName)" Title="Department" />
        <GridColumn Field="@nameof(EmployeeListDto.HireDate)" Title="Hire Date" DisplayFormat="{0:d}" />

        <GridCommandColumn Width="200px">
            <GridCommandButton Command="Edit" Icon="@SvgIcon.Pencil">Edit</GridCommandButton>
            <GridCommandButton Command="Delete" Icon="@SvgIcon.Trash">Delete</GridCommandButton>
        </GridCommandColumn>
    </GridColumns>

    <GridEvents>
        <OnCommand Handler="@OnGridCommand" />
    </GridEvents>
</TelerikGrid>

@code {
    private List<EmployeeListDto> employees = new();

    private async Task OnGridRead(GridReadEventArgs args)
    {
        var result = await Mediator.Send(new GetEmployeeListQuery
        {
            Page = args.Request.Page,
            PageSize = args.Request.PageSize,
            Sorts = args.Request.Sorts,
            Filters = args.Request.Filters
        });

        args.Data = result.Items;
        args.Total = result.TotalCount;
    }

    private async Task OnGridCommand(GridCommandEventArgs args)
    {
        var item = (EmployeeListDto)args.Item;

        switch (args.CommandName)
        {
            case "Add":
                Navigation.NavigateTo("/employees/edit");
                break;
            case "Edit":
                Navigation.NavigateTo($"/employees/edit/{item.Id}");
                break;
            case "Delete":
                await ShowDeleteConfirmation(item);
                break;
        }
    }
}
```

## Dialog Form → Telerik Window

### 4D Dialog
```
// 4D modal dialog for confirmation or quick input
[Message Text]
[Input Field] - Optional input
[OK Button]
[Cancel Button]
```

### Blazor Equivalent
```razor
<TelerikWindow @bind-Visible="@showDialog"
               Modal="true"
               Title="Confirm Delete"
               Width="400px">
    <WindowContent>
        <p>Are you sure you want to delete "@itemToDelete?.Name"?</p>
        <p class="text-danger">This action cannot be undone.</p>
    </WindowContent>
    <WindowActions>
        <WindowAction Name="Close" />
    </WindowActions>
    <WindowFooter>
        <TelerikButton OnClick="@ConfirmDelete" ThemeColor="@ThemeConstants.Button.ThemeColor.Error">
            Delete
        </TelerikButton>
        <TelerikButton OnClick="@CancelDelete">Cancel</TelerikButton>
    </WindowFooter>
</TelerikWindow>

@code {
    private bool showDialog = false;
    private EmployeeDto? itemToDelete;

    private void ShowDeleteDialog(EmployeeDto item)
    {
        itemToDelete = item;
        showDialog = true;
    }

    private async Task ConfirmDelete()
    {
        if (itemToDelete != null)
        {
            await Mediator.Send(new DeleteEmployeeCommand(itemToDelete.Id));
            showDialog = false;
            await RefreshGrid();
        }
    }

    private void CancelDelete()
    {
        showDialog = false;
        itemToDelete = null;
    }
}
```

## Subform → Child Component

### 4D Subform
```
// 4D subform showing related records (e.g., order lines on order form)
[Line Number]
[Product]
[Quantity]
[Unit Price]
[Line Total] - Calculated
```

### Blazor Child Component
```razor
@* OrderLines.razor - Child component *@

<TelerikGrid Data="@Lines"
             TItem="OrderLineDto"
             EditMode="GridEditMode.Inline"
             OnCreate="@OnCreate"
             OnUpdate="@OnUpdate"
             OnDelete="@OnDelete">

    <GridToolBarTemplate>
        <GridCommandButton Command="Add" Icon="@SvgIcon.Plus">Add Line</GridCommandButton>
    </GridToolBarTemplate>

    <GridColumns>
        <GridColumn Field="@nameof(OrderLineDto.LineNumber)" Title="#" Width="60px" Editable="false" />

        <GridColumn Field="@nameof(OrderLineDto.ProductId)" Title="Product">
            <EditorTemplate>
                @{
                    var line = context as OrderLineDto;
                    <TelerikDropDownList Data="@products"
                                         @bind-Value="@line!.ProductId"
                                         TextField="Name"
                                         ValueField="Id" />
                }
            </EditorTemplate>
            <Template>
                @{
                    var line = context as OrderLineDto;
                    @(products.FirstOrDefault(p => p.Id == line?.ProductId)?.Name)
                }
            </Template>
        </GridColumn>

        <GridColumn Field="@nameof(OrderLineDto.Quantity)" Title="Qty" Width="100px" />
        <GridColumn Field="@nameof(OrderLineDto.UnitPrice)" Title="Unit Price" DisplayFormat="{0:C}" Width="120px" />

        <GridColumn Field="@nameof(OrderLineDto.LineTotal)" Title="Total" Width="120px" Editable="false">
            <Template>
                @{
                    var line = context as OrderLineDto;
                    @((line?.Quantity ?? 0) * (line?.UnitPrice ?? 0)).ToString("C")
                }
            </Template>
        </GridColumn>

        <GridCommandColumn Width="150px">
            <GridCommandButton Command="Edit" Icon="@SvgIcon.Pencil" />
            <GridCommandButton Command="Save" Icon="@SvgIcon.Save" ShowInEdit="true" />
            <GridCommandButton Command="Cancel" Icon="@SvgIcon.Cancel" ShowInEdit="true" />
            <GridCommandButton Command="Delete" Icon="@SvgIcon.Trash" />
        </GridCommandColumn>
    </GridColumns>
</TelerikGrid>

@code {
    [Parameter] public List<OrderLineDto> Lines { get; set; } = new();
    [Parameter] public EventCallback<List<OrderLineDto>> LinesChanged { get; set; }

    private List<ProductDto> products = new();

    private async Task OnCreate(GridCommandEventArgs args)
    {
        var newLine = (OrderLineDto)args.Item;
        newLine.LineNumber = Lines.Count + 1;
        Lines.Add(newLine);
        await LinesChanged.InvokeAsync(Lines);
    }

    private async Task OnUpdate(GridCommandEventArgs args)
    {
        var updatedLine = (OrderLineDto)args.Item;
        var index = Lines.FindIndex(l => l.LineNumber == updatedLine.LineNumber);
        if (index >= 0)
        {
            Lines[index] = updatedLine;
            await LinesChanged.InvokeAsync(Lines);
        }
    }

    private async Task OnDelete(GridCommandEventArgs args)
    {
        var deletedLine = (OrderLineDto)args.Item;
        Lines.Remove(deletedLine);
        // Renumber remaining lines
        for (int i = 0; i < Lines.Count; i++)
        {
            Lines[i].LineNumber = i + 1;
        }
        await LinesChanged.InvokeAsync(Lines);
    }
}
```

### Parent Usage
```razor
@* OrderEdit.razor - Parent form *@

<EditForm Model="@order">
    <!-- Order header fields -->
    <TelerikDatePicker @bind-Value="@order.OrderDate" />
    <TelerikDropDownList @bind-Value="@order.CustomerId" Data="@customers" />

    <!-- Order lines subform -->
    <OrderLines @bind-Lines="@order.Lines" />

    <!-- Totals -->
    <div class="order-totals">
        <span>Subtotal: @order.Lines.Sum(l => l.LineTotal).ToString("C")</span>
    </div>
</EditForm>
```

## Tab Form → Telerik TabStrip

### 4D Tab Form
```
// 4D form with tabs
[Tab 1: General Info]
  - FirstName, LastName, etc.
[Tab 2: Contact Info]
  - Phone, Email, Address
[Tab 3: Employment]
  - HireDate, Salary, Department
```

### Blazor Equivalent
```razor
<TelerikTabStrip>
    <TabStripTab Title="General Info">
        <FormItem Field="@nameof(employee.FirstName)" LabelText="First Name">
            <Template>
                <TelerikTextBox @bind-Value="@employee.FirstName" />
            </Template>
        </FormItem>
        <FormItem Field="@nameof(employee.LastName)" LabelText="Last Name">
            <Template>
                <TelerikTextBox @bind-Value="@employee.LastName" />
            </Template>
        </FormItem>
    </TabStripTab>

    <TabStripTab Title="Contact Info">
        <FormItem Field="@nameof(employee.Phone)" LabelText="Phone">
            <Template>
                <TelerikMaskedTextBox @bind-Value="@employee.Phone" Mask="(000) 000-0000" />
            </Template>
        </FormItem>
        <FormItem Field="@nameof(employee.Email)" LabelText="Email">
            <Template>
                <TelerikTextBox @bind-Value="@employee.Email" />
            </Template>
        </FormItem>
    </TabStripTab>

    <TabStripTab Title="Employment">
        <FormItem Field="@nameof(employee.HireDate)" LabelText="Hire Date">
            <Template>
                <TelerikDatePicker @bind-Value="@employee.HireDate" />
            </Template>
        </FormItem>
        <FormItem Field="@nameof(employee.Salary)" LabelText="Salary">
            <Template>
                <TelerikNumericTextBox @bind-Value="@employee.Salary" Format="C" />
            </Template>
        </FormItem>
    </TabStripTab>
</TelerikTabStrip>
```

## Common 4D Controls Mapping

| 4D Control | Telerik Blazor Component |
|------------|-------------------------|
| Text Variable | TelerikTextBox |
| Alpha Field | TelerikTextBox with MaxLength |
| Pop-up Menu | TelerikDropDownList |
| Combo Box | TelerikComboBox |
| Check Box | TelerikCheckBox |
| Radio Button | TelerikRadioGroup |
| List Box | TelerikListBox or TelerikMultiSelect |
| Hierarchical List | TelerikTreeView or TelerikTreeList |
| Button | TelerikButton |
| Picture | <img> or TelerikMediaQuery for responsive |
| Progress Bar | TelerikProgressBar |
| Slider | TelerikSlider |
| Calendar | TelerikCalendar |
| Date Input | TelerikDatePicker |
| Time Input | TelerikTimePicker |
| Spinner (Number) | TelerikNumericTextBox |
| Text Area | TelerikTextArea |
| Rich Text | TelerikEditor |
| Ruler | (No equivalent - use CSS) |
| Group Box | <fieldset> or Telerik Card |
| Tab Control | TelerikTabStrip |
| Splitter | TelerikSplitter |
| Web Area | <iframe> or custom component |

## Event Mapping

| 4D Event | Blazor Equivalent |
|----------|-------------------|
| On Load | OnInitializedAsync |
| On Click | @onclick |
| On Double Click | @ondblclick |
| On Validate | EditContext.OnValidationRequested |
| On Data Change | @bind or @oninput |
| On Getting Focus | @onfocus |
| On Losing Focus | @onblur |
| On Timer | Timer + InvokeAsync |
| On After Edit | OnUpdate event |
| On Resize | WindowResize event (JS interop) |
| On Close | IDisposable.Dispose or NavigatingTo |

## Validation Migration

### 4D Form Validation
```
// 4D validation in form method
If (Length([FirstName]) = 0)
    ALERT("First Name is required")
    $0 := False  // Prevent save
End if
```

### Blazor + FluentValidation
```csharp
// EmployeeValidator.cs
public class EmployeeValidator : AbstractValidator<EmployeeDto>
{
    public EmployeeValidator()
    {
        RuleFor(x => x.FirstName)
            .NotEmpty().WithMessage("First Name is required")
            .MaximumLength(50);

        RuleFor(x => x.LastName)
            .NotEmpty().WithMessage("Last Name is required")
            .MaximumLength(50);

        RuleFor(x => x.Email)
            .EmailAddress().When(x => !string.IsNullOrEmpty(x.Email));

        RuleFor(x => x.HireDate)
            .LessThanOrEqualTo(DateOnly.FromDateTime(DateTime.Today))
            .WithMessage("Hire date cannot be in the future");
    }
}
```

### Blazor Form with Validation
```razor
<TelerikForm Model="@employee" OnValidSubmit="@HandleSubmit">
    <FormValidation>
        <FluentValidationValidator />
    </FormValidation>

    <FormItems>
        <FormItem Field="@nameof(employee.FirstName)" />
        <FormItem Field="@nameof(employee.LastName)" />
    </FormItems>

    <TelerikValidationSummary />
</TelerikForm>
```
