# Form and Dialog Patterns

Comprehensive patterns for Telerik Blazor forms, dialogs, and windows covering validation, layout, multi-step workflows, and CRUD dialog flows.

## TelerikForm with EditForm Integration

The `TelerikForm` component works with Blazor's `EditContext` and can be used standalone or alongside `EditForm`.

### Basic TelerikForm

```razor
<TelerikForm Model="@ContactModel"
             OnValidSubmit="@HandleValidSubmit"
             Columns="2"
             ColumnSpacing="20px">
    <FormValidation>
        <DataAnnotationsValidator />
    </FormValidation>
    <FormItems>
        <FormItem Field="@nameof(ContactFormModel.FirstName)" LabelText="First Name" />
        <FormItem Field="@nameof(ContactFormModel.LastName)" LabelText="Last Name" />
        <FormItem Field="@nameof(ContactFormModel.Email)" LabelText="Email" ColSpan="2" />
        <FormItem Field="@nameof(ContactFormModel.Phone)" LabelText="Phone" />
        <FormItem Field="@nameof(ContactFormModel.Company)" LabelText="Company" />
        <FormItem Field="@nameof(ContactFormModel.Notes)" LabelText="Notes" ColSpan="2">
            <Template>
                <label for="notes">Notes</label>
                <TelerikTextArea @bind-Value="@ContactModel.Notes" Id="notes" AutoSize="true" />
            </Template>
        </FormItem>
    </FormItems>
    <FormButtons>
        <TelerikButton ButtonType="@ButtonType.Submit"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
            Save Contact
        </TelerikButton>
        <TelerikButton ButtonType="@ButtonType.Button"
                        OnClick="@HandleCancel">
            Cancel
        </TelerikButton>
    </FormButtons>
</TelerikForm>

@code {
    private ContactFormModel ContactModel { get; set; } = new();

    private async Task HandleValidSubmit()
    {
        await ContactService.CreateAsync(ContactModel);
        NotificationService.Show("Contact saved successfully.", "Success");
        NavigationManager.NavigateTo("/contacts");
    }

    private void HandleCancel()
    {
        NavigationManager.NavigateTo("/contacts");
    }
}
```

### Model with DataAnnotations

```csharp
public class ContactFormModel
{
    [Required(ErrorMessage = "First name is required.")]
    [StringLength(100, ErrorMessage = "First name cannot exceed 100 characters.")]
    public string FirstName { get; set; } = string.Empty;

    [Required(ErrorMessage = "Last name is required.")]
    [StringLength(100, ErrorMessage = "Last name cannot exceed 100 characters.")]
    public string LastName { get; set; } = string.Empty;

    [Required(ErrorMessage = "Email is required.")]
    [EmailAddress(ErrorMessage = "Please enter a valid email address.")]
    public string Email { get; set; } = string.Empty;

    [Phone(ErrorMessage = "Please enter a valid phone number.")]
    public string? Phone { get; set; }

    [StringLength(200)]
    public string? Company { get; set; }

    [StringLength(2000, ErrorMessage = "Notes cannot exceed 2000 characters.")]
    public string? Notes { get; set; }
}
```

### TelerikForm Inside EditForm (Hybrid Approach)

When you need the flexibility of `EditForm` with Telerik component styling:

```razor
<EditForm Model="@OrderModel" OnValidSubmit="@SubmitOrder">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <div class="form-section">
        <h3>Order Details</h3>
        <div class="form-row">
            <label for="customer">Customer</label>
            <TelerikComboBox Data="@Customers"
                              @bind-Value="@OrderModel.CustomerId"
                              TextField="Name"
                              ValueField="Id"
                              Placeholder="Select customer..."
                              Filterable="true"
                              Id="customer" />
            <ValidationMessage For="@(() => OrderModel.CustomerId)" />
        </div>
        <div class="form-row">
            <label for="order-date">Order Date</label>
            <TelerikDatePicker @bind-Value="@OrderModel.OrderDate"
                                Format="yyyy-MM-dd"
                                Min="@DateTime.Today"
                                Id="order-date" />
            <ValidationMessage For="@(() => OrderModel.OrderDate)" />
        </div>
        <div class="form-row">
            <label for="priority">Priority</label>
            <TelerikDropDownList Data="@Priorities"
                                  @bind-Value="@OrderModel.Priority"
                                  DefaultText="Select priority..."
                                  Id="priority" />
            <ValidationMessage For="@(() => OrderModel.Priority)" />
        </div>
    </div>

    <TelerikButton ButtonType="@ButtonType.Submit"
                    ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
        Place Order
    </TelerikButton>
</EditForm>
```

## Validation with FluentValidation

### Setup

Register FluentValidation in `Program.cs`:

```csharp
builder.Services.AddScoped<IValidator<ProductFormModel>, ProductFormValidator>();
```

### Validator Class

```csharp
using FluentValidation;

public class ProductFormValidator : AbstractValidator<ProductFormModel>
{
    public ProductFormValidator()
    {
        RuleFor(p => p.Name)
            .NotEmpty().WithMessage("Product name is required.")
            .MaximumLength(200).WithMessage("Name cannot exceed 200 characters.");

        RuleFor(p => p.Sku)
            .NotEmpty().WithMessage("SKU is required.")
            .Matches(@"^[A-Z]{2,4}-\d{4,8}$").WithMessage("SKU must match format: XX-0000 (e.g., AB-1234).");

        RuleFor(p => p.Price)
            .GreaterThan(0).WithMessage("Price must be greater than zero.")
            .LessThanOrEqualTo(999999.99m).WithMessage("Price cannot exceed $999,999.99.");

        RuleFor(p => p.CategoryId)
            .GreaterThan(0).WithMessage("Please select a category.");

        RuleFor(p => p.StockQuantity)
            .GreaterThanOrEqualTo(0).WithMessage("Stock cannot be negative.");

        When(p => p.HasExpirationDate, () =>
        {
            RuleFor(p => p.ExpirationDate)
                .NotNull().WithMessage("Expiration date is required when product is perishable.")
                .GreaterThan(DateTime.Today).WithMessage("Expiration date must be in the future.");
        });
    }
}
```

### Form with FluentValidation

```razor
@using FluentValidation

<EditForm Model="@ProductModel" OnValidSubmit="@SaveProduct">
    <FluentValidationValidator />

    <TelerikForm Model="@ProductModel" Columns="2" ColumnSpacing="15px">
        <FormItems>
            <FormItem Field="@nameof(ProductFormModel.Name)" LabelText="Product Name" ColSpan="2" />
            <FormItem Field="@nameof(ProductFormModel.Sku)" LabelText="SKU" />
            <FormItem Field="@nameof(ProductFormModel.Price)" LabelText="Price">
                <Template>
                    <label for="price">Price</label>
                    <TelerikNumericTextBox @bind-Value="@ProductModel.Price"
                                            Format="C2"
                                            Min="0"
                                            Step="0.01m"
                                            Id="price" />
                </Template>
            </FormItem>
            <FormItem Field="@nameof(ProductFormModel.CategoryId)" LabelText="Category">
                <Template>
                    <label for="category">Category</label>
                    <TelerikDropDownList Data="@Categories"
                                          @bind-Value="@ProductModel.CategoryId"
                                          TextField="Name"
                                          ValueField="Id"
                                          DefaultText="Select category..."
                                          Id="category" />
                </Template>
            </FormItem>
            <FormItem Field="@nameof(ProductFormModel.StockQuantity)" LabelText="Stock Qty">
                <Template>
                    <label for="stock">Stock Quantity</label>
                    <TelerikNumericTextBox @bind-Value="@ProductModel.StockQuantity"
                                            Format="N0"
                                            Min="0"
                                            Step="1"
                                            Id="stock" />
                </Template>
            </FormItem>
        </FormItems>
    </TelerikForm>

    <ValidationSummary />

    <div class="form-actions">
        <TelerikButton ButtonType="@ButtonType.Submit"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
            Save Product
        </TelerikButton>
    </div>
</EditForm>
```

## TelerikDialog Patterns

### Simple Confirmation Dialog

```razor
<TelerikButton OnClick="@(() => IsDeleteDialogVisible = true)"
                ThemeColor="@ThemeConstants.Button.ThemeColor.Error">
    Delete Item
</TelerikButton>

<TelerikDialog @bind-Visible="@IsDeleteDialogVisible"
               Title="Confirm Deletion"
               Width="450px">
    <DialogContent>
        <p>Are you sure you want to delete <strong>@ItemToDelete?.Name</strong>?</p>
        <p>This action cannot be undone.</p>
    </DialogContent>
    <DialogButtons>
        <TelerikButton OnClick="@CancelDelete">Cancel</TelerikButton>
        <TelerikButton OnClick="@ConfirmDelete"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Error">
            Delete
        </TelerikButton>
    </DialogButtons>
</TelerikDialog>

@code {
    private bool IsDeleteDialogVisible { get; set; }
    private ItemDto? ItemToDelete { get; set; }

    private void CancelDelete()
    {
        IsDeleteDialogVisible = false;
        ItemToDelete = null;
    }

    private async Task ConfirmDelete()
    {
        if (ItemToDelete is null) return;

        try
        {
            await ItemService.DeleteAsync(ItemToDelete.Id);
            NotificationService.Show($"{ItemToDelete.Name} deleted.", "Success");
            Items.Remove(ItemToDelete);
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Delete failed for item {Id}", ItemToDelete.Id);
            NotificationService.Show("Could not delete item. Please try again.", "Error");
        }
        finally
        {
            IsDeleteDialogVisible = false;
            ItemToDelete = null;
        }
    }
}
```

### Information / Alert Dialog

```razor
<TelerikDialog @bind-Visible="@IsAlertVisible"
               Title="@AlertTitle"
               Width="400px">
    <DialogContent>
        <div class="alert-content">
            <TelerikSvgIcon Icon="@AlertIcon" Size="@ThemeConstants.SvgIcon.Size.ExtraLarge" />
            <p>@AlertMessage</p>
        </div>
    </DialogContent>
    <DialogButtons>
        <TelerikButton OnClick="@(() => IsAlertVisible = false)"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
            OK
        </TelerikButton>
    </DialogButtons>
</TelerikDialog>

@code {
    private bool IsAlertVisible { get; set; }
    private string AlertTitle { get; set; } = string.Empty;
    private string AlertMessage { get; set; } = string.Empty;
    private ISvgIcon AlertIcon { get; set; } = SvgIcon.InfoCircle;

    private void ShowAlert(string title, string message, ISvgIcon? icon = null)
    {
        AlertTitle = title;
        AlertMessage = message;
        AlertIcon = icon ?? SvgIcon.InfoCircle;
        IsAlertVisible = true;
    }
}
```

## TelerikWindow Patterns

Use `TelerikWindow` when the user needs a draggable, resizable overlay with complex content.

### Draggable Detail Window

```razor
<TelerikWindow @bind-Visible="@IsDetailWindowVisible"
               Title="@($"Order Details - #{SelectedOrder?.Id}")"
               Width="700px"
               Height="500px"
               Draggable="true"
               Resizable="true"
               Modal="false">
    <WindowActions>
        <WindowAction Name="Minimize" />
        <WindowAction Name="Maximize" />
        <WindowAction Name="Close" />
    </WindowActions>
    <WindowContent>
        @if (SelectedOrder is not null)
        {
            <div class="order-detail">
                <div class="detail-row">
                    <strong>Customer:</strong> @SelectedOrder.CustomerName
                </div>
                <div class="detail-row">
                    <strong>Date:</strong> @SelectedOrder.OrderDate.ToString("D")
                </div>
                <div class="detail-row">
                    <strong>Status:</strong> @SelectedOrder.Status
                </div>

                <h4>Line Items</h4>
                <TelerikGrid Data="@SelectedOrder.LineItems"
                             TItem="LineItemDto"
                             Pageable="false"
                             Height="250px">
                    <GridColumns>
                        <GridColumn Field="@nameof(LineItemDto.Product)" Title="Product" />
                        <GridColumn Field="@nameof(LineItemDto.Quantity)" Title="Qty" Width="80px" />
                        <GridColumn Field="@nameof(LineItemDto.UnitPrice)" Title="Price" DisplayFormat="{0:C2}" Width="120px" />
                        <GridColumn Field="@nameof(LineItemDto.Total)" Title="Total" DisplayFormat="{0:C2}" Width="120px" />
                    </GridColumns>
                </TelerikGrid>

                <div class="order-total">
                    <strong>Order Total: @SelectedOrder.Total.ToString("C2")</strong>
                </div>
            </div>
        }
    </WindowContent>
</TelerikWindow>
```

### Modal Window for Complex Forms

```razor
<TelerikWindow @bind-Visible="@IsFormWindowVisible"
               Title="@FormWindowTitle"
               Width="800px"
               Height="600px"
               Modal="true"
               Centered="true">
    <WindowActions>
        <WindowAction Name="Close" />
    </WindowActions>
    <WindowContent>
        <EditForm Model="@EmployeeFormModel" OnValidSubmit="@SaveEmployee">
            <DataAnnotationsValidator />

            <TelerikForm Model="@EmployeeFormModel" Columns="2" ColumnSpacing="15px">
                <FormItems>
                    <FormItem Field="@nameof(EmployeeFormModel.FirstName)" LabelText="First Name" />
                    <FormItem Field="@nameof(EmployeeFormModel.LastName)" LabelText="Last Name" />
                    <FormItem Field="@nameof(EmployeeFormModel.Email)" LabelText="Email" ColSpan="2" />
                    <FormItem Field="@nameof(EmployeeFormModel.Department)" LabelText="Department">
                        <Template>
                            <label for="dept">Department</label>
                            <TelerikComboBox Data="@Departments"
                                              @bind-Value="@EmployeeFormModel.DepartmentId"
                                              TextField="Name"
                                              ValueField="Id"
                                              Filterable="true"
                                              Id="dept" />
                        </Template>
                    </FormItem>
                    <FormItem Field="@nameof(EmployeeFormModel.HireDate)" LabelText="Hire Date">
                        <Template>
                            <label for="hire-date">Hire Date</label>
                            <TelerikDatePicker @bind-Value="@EmployeeFormModel.HireDate"
                                                Format="yyyy-MM-dd"
                                                Id="hire-date" />
                        </Template>
                    </FormItem>
                </FormItems>
            </TelerikForm>

            <ValidationSummary />

            <div class="window-actions">
                <TelerikButton ButtonType="@ButtonType.Button"
                                OnClick="@(() => IsFormWindowVisible = false)">
                    Cancel
                </TelerikButton>
                <TelerikButton ButtonType="@ButtonType.Submit"
                                ThemeColor="@ThemeConstants.Button.ThemeColor.Primary"
                                Enabled="@(!IsSaving)">
                    @(IsSaving ? "Saving..." : "Save Employee")
                </TelerikButton>
            </div>
        </EditForm>
    </WindowContent>
</TelerikWindow>

@code {
    private bool IsFormWindowVisible { get; set; }
    private bool IsSaving { get; set; }
    private string FormWindowTitle => IsEditing ? "Edit Employee" : "New Employee";
    private bool IsEditing => EmployeeFormModel.Id > 0;
    private EmployeeFormModel EmployeeFormModel { get; set; } = new();

    private void OpenCreateForm()
    {
        EmployeeFormModel = new EmployeeFormModel();
        IsFormWindowVisible = true;
    }

    private void OpenEditForm(EmployeeDto employee)
    {
        EmployeeFormModel = Mapper.Map<EmployeeFormModel>(employee);
        IsFormWindowVisible = true;
    }

    private async Task SaveEmployee()
    {
        try
        {
            IsSaving = true;

            if (IsEditing)
            {
                await EmployeeService.UpdateAsync(EmployeeFormModel);
                NotificationService.Show("Employee updated.", "Success");
            }
            else
            {
                await EmployeeService.CreateAsync(EmployeeFormModel);
                NotificationService.Show("Employee created.", "Success");
            }

            IsFormWindowVisible = false;
            await RefreshGrid();
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Failed to save employee");
            NotificationService.Show("Save failed. Please try again.", "Error");
        }
        finally
        {
            IsSaving = false;
        }
    }
}
```

## Multi-Step Wizard Forms

### Using TelerikWizard

```razor
<TelerikWizard OnFinish="@OnWizardFinish"
               Width="800px"
               Height="550px">
    <WizardSteps>
        <WizardStep Label="Basic Info" Icon="@SvgIcon.User">
            <Content>
                <div class="wizard-step-content">
                    <h4>Basic Information</h4>
                    <div class="form-field">
                        <label for="wiz-name">Full Name</label>
                        <TelerikTextBox @bind-Value="@WizardModel.FullName" Id="wiz-name" />
                    </div>
                    <div class="form-field">
                        <label for="wiz-email">Email</label>
                        <TelerikTextBox @bind-Value="@WizardModel.Email" Id="wiz-email" />
                    </div>
                    <div class="form-field">
                        <label for="wiz-phone">Phone</label>
                        <TelerikTextBox @bind-Value="@WizardModel.Phone" Id="wiz-phone" />
                    </div>
                </div>
            </Content>
        </WizardStep>

        <WizardStep Label="Address" Icon="@SvgIcon.MapMarker">
            <Content>
                <div class="wizard-step-content">
                    <h4>Address</h4>
                    <div class="form-field">
                        <label for="wiz-street">Street Address</label>
                        <TelerikTextBox @bind-Value="@WizardModel.Street" Id="wiz-street" />
                    </div>
                    <div class="form-field">
                        <label for="wiz-city">City</label>
                        <TelerikTextBox @bind-Value="@WizardModel.City" Id="wiz-city" />
                    </div>
                    <div class="form-row">
                        <div class="form-field">
                            <label for="wiz-state">State</label>
                            <TelerikComboBox Data="@States"
                                              @bind-Value="@WizardModel.State"
                                              TextField="Name"
                                              ValueField="Abbreviation"
                                              Filterable="true"
                                              Id="wiz-state" />
                        </div>
                        <div class="form-field">
                            <label for="wiz-zip">ZIP Code</label>
                            <TelerikTextBox @bind-Value="@WizardModel.ZipCode" Id="wiz-zip" />
                        </div>
                    </div>
                </div>
            </Content>
        </WizardStep>

        <WizardStep Label="Preferences" Icon="@SvgIcon.Gear">
            <Content>
                <div class="wizard-step-content">
                    <h4>Notification Preferences</h4>
                    <div class="form-field">
                        <TelerikCheckBox @bind-Value="@WizardModel.EmailNotifications" Id="wiz-email-notif" />
                        <label for="wiz-email-notif">Receive email notifications</label>
                    </div>
                    <div class="form-field">
                        <TelerikCheckBox @bind-Value="@WizardModel.SmsNotifications" Id="wiz-sms-notif" />
                        <label for="wiz-sms-notif">Receive SMS notifications</label>
                    </div>
                    <div class="form-field">
                        <label for="wiz-frequency">Notification Frequency</label>
                        <TelerikDropDownList Data="@Frequencies"
                                              @bind-Value="@WizardModel.NotificationFrequency"
                                              Id="wiz-frequency" />
                    </div>
                </div>
            </Content>
        </WizardStep>

        <WizardStep Label="Review" Icon="@SvgIcon.CheckCircle">
            <Content>
                <div class="wizard-step-content">
                    <h4>Review Your Information</h4>
                    <dl class="review-list">
                        <dt>Name</dt><dd>@WizardModel.FullName</dd>
                        <dt>Email</dt><dd>@WizardModel.Email</dd>
                        <dt>Phone</dt><dd>@WizardModel.Phone</dd>
                        <dt>Address</dt><dd>@WizardModel.Street, @WizardModel.City, @WizardModel.State @WizardModel.ZipCode</dd>
                        <dt>Email Notifications</dt><dd>@(WizardModel.EmailNotifications ? "Yes" : "No")</dd>
                        <dt>SMS Notifications</dt><dd>@(WizardModel.SmsNotifications ? "Yes" : "No")</dd>
                    </dl>
                </div>
            </Content>
        </WizardStep>
    </WizardSteps>
</TelerikWizard>

@code {
    private RegistrationWizardModel WizardModel { get; set; } = new();

    private async Task OnWizardFinish()
    {
        await RegistrationService.RegisterAsync(WizardModel);
        NotificationService.Show("Registration complete!", "Success");
        NavigationManager.NavigateTo("/dashboard");
    }
}
```

### Custom Stepper-Based Wizard (Without TelerikWizard)

For more control over step transitions and validation per step:

```razor
<TelerikStepper @bind-Value="@CurrentStep">
    <StepperSteps>
        <StepperStep Label="Account" Icon="@SvgIcon.User" />
        <StepperStep Label="Profile" Icon="@SvgIcon.Image" />
        <StepperStep Label="Confirm" Icon="@SvgIcon.Check" />
    </StepperSteps>
</TelerikStepper>

<div class="step-content">
    @switch (CurrentStep)
    {
        case 0:
            <EditForm Model="@AccountModel" OnValidSubmit="@GoToStep1">
                <DataAnnotationsValidator />
                <div class="form-field">
                    <label for="username">Username</label>
                    <TelerikTextBox @bind-Value="@AccountModel.Username" Id="username" />
                    <ValidationMessage For="@(() => AccountModel.Username)" />
                </div>
                <div class="form-field">
                    <label for="password">Password</label>
                    <TelerikTextBox @bind-Value="@AccountModel.Password" Password="true" Id="password" />
                    <ValidationMessage For="@(() => AccountModel.Password)" />
                </div>
                <TelerikButton ButtonType="@ButtonType.Submit"
                                ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
                    Next
                </TelerikButton>
            </EditForm>
            break;

        case 1:
            <EditForm Model="@ProfileModel" OnValidSubmit="@GoToStep2">
                <DataAnnotationsValidator />
                <div class="form-field">
                    <label for="display-name">Display Name</label>
                    <TelerikTextBox @bind-Value="@ProfileModel.DisplayName" Id="display-name" />
                    <ValidationMessage For="@(() => ProfileModel.DisplayName)" />
                </div>
                <div class="form-field">
                    <label for="bio">Bio</label>
                    <TelerikTextArea @bind-Value="@ProfileModel.Bio" Id="bio" />
                </div>
                <TelerikButton OnClick="@(() => CurrentStep = 0)">Back</TelerikButton>
                <TelerikButton ButtonType="@ButtonType.Submit"
                                ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">
                    Next
                </TelerikButton>
            </EditForm>
            break;

        case 2:
            <div class="confirmation-step">
                <p>Username: @AccountModel.Username</p>
                <p>Display Name: @ProfileModel.DisplayName</p>
                <TelerikButton OnClick="@(() => CurrentStep = 1)">Back</TelerikButton>
                <TelerikButton OnClick="@CompleteRegistration"
                                ThemeColor="@ThemeConstants.Button.ThemeColor.Primary"
                                Enabled="@(!IsSubmitting)">
                    @(IsSubmitting ? "Creating Account..." : "Create Account")
                </TelerikButton>
            </div>
            break;
    }
</div>

@code {
    private int CurrentStep { get; set; }
    private bool IsSubmitting { get; set; }
    private AccountStepModel AccountModel { get; set; } = new();
    private ProfileStepModel ProfileModel { get; set; } = new();

    private void GoToStep1() => CurrentStep = 1;
    private void GoToStep2() => CurrentStep = 2;

    private async Task CompleteRegistration()
    {
        IsSubmitting = true;
        try
        {
            await AuthService.CreateAccountAsync(AccountModel, ProfileModel);
            NavigationManager.NavigateTo("/welcome");
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Registration failed");
            NotificationService.Show("Registration failed. Please try again.", "Error");
        }
        finally
        {
            IsSubmitting = false;
        }
    }
}
```

## Form Field Components Reference

### TextBox and TextArea

```razor
<!-- Standard text input -->
<TelerikTextBox @bind-Value="@Model.Name"
                Placeholder="Enter name..."
                Label="Name"
                Width="100%" />

<!-- Password input -->
<TelerikTextBox @bind-Value="@Model.Password"
                Password="true"
                Label="Password" />

<!-- Multi-line text with auto-sizing -->
<TelerikTextArea @bind-Value="@Model.Description"
                  AutoSize="true"
                  Label="Description"
                  Rows="3" />
```

### NumericTextBox

```razor
<!-- Currency -->
<TelerikNumericTextBox @bind-Value="@Model.Price"
                        Format="C2"
                        Min="0"
                        Step="0.01m"
                        Label="Price" />

<!-- Integer -->
<TelerikNumericTextBox @bind-Value="@Model.Quantity"
                        Format="N0"
                        Min="0"
                        Max="9999"
                        Step="1"
                        Label="Quantity" />

<!-- Percentage -->
<TelerikNumericTextBox @bind-Value="@Model.Discount"
                        Format="P0"
                        Min="0"
                        Max="1"
                        Step="0.05m"
                        Label="Discount" />
```

### DatePicker, TimePicker, DateTimePicker

```razor
<!-- Date only -->
<TelerikDatePicker @bind-Value="@Model.BirthDate"
                    Format="yyyy-MM-dd"
                    Min="@(new DateTime(1900, 1, 1))"
                    Max="@DateTime.Today"
                    Label="Date of Birth" />

<!-- Time only -->
<TelerikTimePicker @bind-Value="@Model.StartTime"
                    Format="HH:mm"
                    Label="Start Time" />

<!-- Date and time -->
<TelerikDateTimePicker @bind-Value="@Model.AppointmentDateTime"
                        Format="yyyy-MM-dd HH:mm"
                        Min="@DateTime.Now"
                        Label="Appointment" />

<!-- Date range -->
<TelerikDateRangePicker StartValue="@Model.StartDate"
                         StartValueChanged="@((DateTime? v) => Model.StartDate = v)"
                         EndValue="@Model.EndDate"
                         EndValueChanged="@((DateTime? v) => Model.EndDate = v)"
                         Label="Date Range" />
```

### ComboBox and DropDownList

```razor
<!-- DropDownList (select from fixed list, no typing) -->
<TelerikDropDownList Data="@Statuses"
                      @bind-Value="@Model.Status"
                      DefaultText="Select status..."
                      Label="Status" />

<!-- ComboBox (select from list with filtering/typing) -->
<TelerikComboBox Data="@Countries"
                  @bind-Value="@Model.CountryId"
                  TextField="Name"
                  ValueField="Id"
                  Filterable="true"
                  FilterOperator="@StringFilterOperator.Contains"
                  Placeholder="Search countries..."
                  Label="Country" />

<!-- MultiSelect (multiple values) -->
<TelerikMultiSelect Data="@Tags"
                     @bind-Value="@Model.SelectedTagIds"
                     TextField="Name"
                     ValueField="Id"
                     Placeholder="Select tags..."
                     AutoClose="false"
                     Label="Tags" />

<!-- AutoComplete (text suggestions, free-form input) -->
<TelerikAutoComplete Data="@Suggestions"
                      @bind-Value="@Model.SearchTerm"
                      Placeholder="Type to search..."
                      MinLength="2"
                      Label="Search" />
```

### Checkbox, Switch, RadioGroup

```razor
<!-- Checkbox -->
<TelerikCheckBox @bind-Value="@Model.AcceptTerms" Id="accept-terms" />
<label for="accept-terms">I accept the terms and conditions</label>

<!-- Switch (toggle) -->
<TelerikSwitch @bind-Value="@Model.IsActive"
                OnLabel="Active"
                OffLabel="Inactive" />

<!-- RadioGroup -->
<TelerikRadioGroup Data="@PaymentMethods"
                    @bind-Value="@Model.PaymentMethod"
                    TextField="Label"
                    ValueField="Value"
                    Layout="@RadioGroupLayout.Vertical"
                    Label="Payment Method" />
```

### Slider and RangeSlider

```razor
<!-- Slider -->
<TelerikSlider @bind-Value="@Model.Rating"
                Min="1"
                Max="10"
                SmallStep="1"
                LargeStep="5"
                Label="Rating" />

<!-- RangeSlider -->
<TelerikRangeSlider @bind-StartValue="@Model.MinPrice"
                     @bind-EndValue="@Model.MaxPrice"
                     Min="0"
                     Max="1000"
                     SmallStep="10"
                     LargeStep="100"
                     Label="Price Range" />
```

## Responsive Form Layouts

### Two-Column Layout with Stack

```razor
<TelerikStackLayout Orientation="@StackLayoutOrientation.Horizontal"
                     Spacing="20px"
                     HorizontalAlign="@StackLayoutHorizontalAlign.Stretch">
    <div class="form-column">
        <h4>Personal Information</h4>
        <TelerikTextBox @bind-Value="@Model.FirstName" Label="First Name" Width="100%" />
        <TelerikTextBox @bind-Value="@Model.LastName" Label="Last Name" Width="100%" />
        <TelerikDatePicker @bind-Value="@Model.DateOfBirth" Label="Date of Birth" Width="100%" />
    </div>
    <div class="form-column">
        <h4>Contact Information</h4>
        <TelerikTextBox @bind-Value="@Model.Email" Label="Email" Width="100%" />
        <TelerikTextBox @bind-Value="@Model.Phone" Label="Phone" Width="100%" />
        <TelerikTextBox @bind-Value="@Model.Address" Label="Address" Width="100%" />
    </div>
</TelerikStackLayout>
```

### Responsive with CSS Grid

```razor
<div class="responsive-form">
    <div class="form-field">
        <TelerikTextBox @bind-Value="@Model.Name" Label="Name" Width="100%" />
    </div>
    <div class="form-field">
        <TelerikTextBox @bind-Value="@Model.Email" Label="Email" Width="100%" />
    </div>
    <div class="form-field full-width">
        <TelerikTextArea @bind-Value="@Model.Description" Label="Description" Width="100%" AutoSize="true" />
    </div>
    <div class="form-field">
        <TelerikDropDownList Data="@Categories" @bind-Value="@Model.Category" Label="Category" Width="100%" />
    </div>
    <div class="form-field">
        <TelerikDatePicker @bind-Value="@Model.DueDate" Label="Due Date" Width="100%" />
    </div>
</div>
```

```css
.responsive-form {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
}

.responsive-form .full-width {
    grid-column: 1 / -1;
}
```

## Dialog-Based CRUD Workflows

A complete pattern for managing entities through a grid with dialog-based create, edit, and delete.

### Parent Component (Grid + Dialogs)

```razor
@page "/products"

<h2>Product Management</h2>

<TelerikGrid Data="@Products"
             TItem="ProductDto"
             Pageable="true"
             PageSize="20"
             Sortable="true"
             FilterMode="@GridFilterMode.FilterRow"
             Height="600px">
    <GridToolBarTemplate>
        <TelerikButton OnClick="@OpenCreateDialog"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Primary"
                        Icon="@SvgIcon.Plus">
            New Product
        </TelerikButton>
    </GridToolBarTemplate>
    <GridColumns>
        <GridColumn Field="@nameof(ProductDto.Name)" Title="Product" />
        <GridColumn Field="@nameof(ProductDto.Category)" Title="Category" />
        <GridColumn Field="@nameof(ProductDto.Price)" Title="Price" DisplayFormat="{0:C2}" />
        <GridColumn Field="@nameof(ProductDto.InStock)" Title="In Stock" Width="100px" />
        <GridColumn Title="Actions" Width="200px">
            <Template>
                @{
                    var product = (ProductDto)context;
                }
                <TelerikButton OnClick="@(() => OpenEditDialog(product))"
                                Icon="@SvgIcon.Pencil"
                                FillMode="@ThemeConstants.Button.FillMode.Flat">
                    Edit
                </TelerikButton>
                <TelerikButton OnClick="@(() => OpenDeleteDialog(product))"
                                Icon="@SvgIcon.Trash"
                                FillMode="@ThemeConstants.Button.FillMode.Flat"
                                ThemeColor="@ThemeConstants.Button.ThemeColor.Error">
                    Delete
                </TelerikButton>
            </Template>
        </GridColumn>
    </GridColumns>
    <NoDataTemplate>
        <p>No products found. Click "New Product" to add one.</p>
    </NoDataTemplate>
</TelerikGrid>

<!-- CREATE / EDIT Dialog -->
<TelerikWindow @bind-Visible="@IsFormDialogVisible"
               Title="@FormDialogTitle"
               Width="600px"
               Modal="true"
               Centered="true">
    <WindowActions>
        <WindowAction Name="Close" />
    </WindowActions>
    <WindowContent>
        <EditForm Model="@FormModel" OnValidSubmit="@SaveProduct">
            <DataAnnotationsValidator />

            <div class="dialog-form">
                <div class="form-field">
                    <label for="prod-name">Product Name</label>
                    <TelerikTextBox @bind-Value="@FormModel.Name" Id="prod-name" Width="100%" />
                    <ValidationMessage For="@(() => FormModel.Name)" />
                </div>
                <div class="form-field">
                    <label for="prod-category">Category</label>
                    <TelerikComboBox Data="@Categories"
                                      @bind-Value="@FormModel.CategoryId"
                                      TextField="Name"
                                      ValueField="Id"
                                      Filterable="true"
                                      Id="prod-category"
                                      Width="100%" />
                    <ValidationMessage For="@(() => FormModel.CategoryId)" />
                </div>
                <div class="form-field">
                    <label for="prod-price">Price</label>
                    <TelerikNumericTextBox @bind-Value="@FormModel.Price"
                                            Format="C2"
                                            Min="0"
                                            Id="prod-price"
                                            Width="100%" />
                    <ValidationMessage For="@(() => FormModel.Price)" />
                </div>
                <div class="form-field">
                    <label for="prod-stock">Initial Stock</label>
                    <TelerikNumericTextBox @bind-Value="@FormModel.StockQuantity"
                                            Format="N0"
                                            Min="0"
                                            Id="prod-stock"
                                            Width="100%" />
                </div>
            </div>

            <ValidationSummary />

            <div class="dialog-actions">
                <TelerikButton ButtonType="@ButtonType.Button"
                                OnClick="@(() => IsFormDialogVisible = false)">
                    Cancel
                </TelerikButton>
                <TelerikButton ButtonType="@ButtonType.Submit"
                                ThemeColor="@ThemeConstants.Button.ThemeColor.Primary"
                                Enabled="@(!IsSaving)">
                    @(IsSaving ? "Saving..." : "Save")
                </TelerikButton>
            </div>
        </EditForm>
    </WindowContent>
</TelerikWindow>

<!-- DELETE Confirmation Dialog -->
<TelerikDialog @bind-Visible="@IsDeleteDialogVisible"
               Title="Confirm Deletion"
               Width="450px">
    <DialogContent>
        <p>Are you sure you want to delete <strong>@ProductToDelete?.Name</strong>?</p>
        <p>This action cannot be undone.</p>
    </DialogContent>
    <DialogButtons>
        <TelerikButton OnClick="@(() => IsDeleteDialogVisible = false)">Cancel</TelerikButton>
        <TelerikButton OnClick="@ConfirmDelete"
                        ThemeColor="@ThemeConstants.Button.ThemeColor.Error"
                        Enabled="@(!IsDeleting)">
            @(IsDeleting ? "Deleting..." : "Delete")
        </TelerikButton>
    </DialogButtons>
</TelerikDialog>

@code {
    private List<ProductDto> Products { get; set; } = new();
    private List<CategoryDto> Categories { get; set; } = new();

    // Form dialog state
    private bool IsFormDialogVisible { get; set; }
    private bool IsSaving { get; set; }
    private ProductFormModel FormModel { get; set; } = new();
    private string FormDialogTitle => FormModel.Id > 0 ? "Edit Product" : "New Product";

    // Delete dialog state
    private bool IsDeleteDialogVisible { get; set; }
    private bool IsDeleting { get; set; }
    private ProductDto? ProductToDelete { get; set; }

    protected override async Task OnInitializedAsync()
    {
        Products = await ProductService.GetAllAsync();
        Categories = await CategoryService.GetAllAsync();
    }

    private void OpenCreateDialog()
    {
        FormModel = new ProductFormModel();
        IsFormDialogVisible = true;
    }

    private void OpenEditDialog(ProductDto product)
    {
        FormModel = new ProductFormModel
        {
            Id = product.Id,
            Name = product.Name,
            CategoryId = product.CategoryId,
            Price = product.Price,
            StockQuantity = product.StockQuantity
        };
        IsFormDialogVisible = true;
    }

    private void OpenDeleteDialog(ProductDto product)
    {
        ProductToDelete = product;
        IsDeleteDialogVisible = true;
    }

    private async Task SaveProduct()
    {
        IsSaving = true;
        try
        {
            if (FormModel.Id > 0)
            {
                var updated = await ProductService.UpdateAsync(FormModel);
                var index = Products.FindIndex(p => p.Id == updated.Id);
                if (index >= 0) Products[index] = updated;
                NotificationService.Show("Product updated.", "Success");
            }
            else
            {
                var created = await ProductService.CreateAsync(FormModel);
                Products.Insert(0, created);
                NotificationService.Show("Product created.", "Success");
            }
            IsFormDialogVisible = false;
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Failed to save product");
            NotificationService.Show("Save failed. Please try again.", "Error");
        }
        finally
        {
            IsSaving = false;
        }
    }

    private async Task ConfirmDelete()
    {
        if (ProductToDelete is null) return;

        IsDeleting = true;
        try
        {
            await ProductService.DeleteAsync(ProductToDelete.Id);
            Products.Remove(ProductToDelete);
            NotificationService.Show($"{ProductToDelete.Name} deleted.", "Success");
            IsDeleteDialogVisible = false;
        }
        catch (Exception ex)
        {
            Logger.LogError(ex, "Failed to delete product {Id}", ProductToDelete.Id);
            NotificationService.Show("Delete failed. Please try again.", "Error");
        }
        finally
        {
            IsDeleting = false;
            ProductToDelete = null;
        }
    }
}
```

## TelerikNotification for Operation Feedback

Always pair form/dialog operations with user notifications.

### Setup in Layout

```razor
<!-- In MainLayout.razor -->
<TelerikRootComponent>
    @Body
    <TelerikNotification @ref="@NotificationRef"
                          AnimationType="@AnimationType.Fade"
                          HorizontalPosition="@NotificationHorizontalPosition.Right"
                          VerticalPosition="@NotificationVerticalPosition.Top" />
</TelerikRootComponent>

@code {
    private TelerikNotification NotificationRef { get; set; } = default!;
}
```

### Notification Service

```csharp
public class AppNotificationService
{
    private TelerikNotification? _notification;

    public void SetNotificationComponent(TelerikNotification notification)
    {
        _notification = notification;
    }

    public void ShowSuccess(string message)
    {
        _notification?.Show(new NotificationModel
        {
            Text = message,
            ThemeColor = ThemeConstants.Notification.ThemeColor.Success,
            CloseAfter = 3000
        });
    }

    public void ShowError(string message)
    {
        _notification?.Show(new NotificationModel
        {
            Text = message,
            ThemeColor = ThemeConstants.Notification.ThemeColor.Error,
            CloseAfter = 5000
        });
    }

    public void ShowWarning(string message)
    {
        _notification?.Show(new NotificationModel
        {
            Text = message,
            ThemeColor = ThemeConstants.Notification.ThemeColor.Warning,
            CloseAfter = 4000
        });
    }

    public void ShowInfo(string message)
    {
        _notification?.Show(new NotificationModel
        {
            Text = message,
            ThemeColor = ThemeConstants.Notification.ThemeColor.Info,
            CloseAfter = 3000
        });
    }
}
```
