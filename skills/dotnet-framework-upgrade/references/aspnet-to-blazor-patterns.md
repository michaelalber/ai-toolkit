# ASP.NET Web Forms / MVC to Blazor Migration

## Migration Path Options

| Source | Target | Complexity |
|--------|--------|------------|
| ASP.NET Web Forms | Blazor Server | High |
| ASP.NET MVC (Razor) | Blazor Server/WASM | Medium |
| ASP.NET Web API | Minimal API or Controller | Low |

## ASP.NET MVC → Blazor

### Razor View → Blazor Component

```html
<!-- OLD: MVC Razor View (Views/Users/Index.cshtml) -->
@model IEnumerable<User>
@{
    ViewBag.Title = "Users";
}

<h2>Users</h2>
<table class="table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        @foreach (var user in Model)
        {
            <tr>
                <td>@user.Name</td>
                <td>@user.Email</td>
                <td>
                    @Html.ActionLink("Edit", "Edit", new { id = user.Id })
                    @Html.ActionLink("Delete", "Delete", new { id = user.Id })
                </td>
            </tr>
        }
    </tbody>
</table>
```

```razor
<!-- NEW: Blazor Component (Pages/Users/Index.razor) -->
@page "/users"
@inject IMediator Mediator

<PageTitle>Users</PageTitle>

<h2>Users</h2>

<TelerikGrid Data="@users" Pageable="true" Sortable="true">
    <GridColumns>
        <GridColumn Field="@nameof(UserDto.Name)" Title="Name" />
        <GridColumn Field="@nameof(UserDto.Email)" Title="Email" />
        <GridCommandColumn>
            <GridCommandButton Command="Edit" Icon="@SvgIcon.Pencil" OnClick="@(args => EditUser(args.Item as UserDto))" />
            <GridCommandButton Command="Delete" Icon="@SvgIcon.Trash" OnClick="@(args => DeleteUser(args.Item as UserDto))" />
        </GridCommandColumn>
    </GridColumns>
</TelerikGrid>

@code {
    private List<UserDto> users = new();

    protected override async Task OnInitializedAsync()
    {
        users = await Mediator.Send(new GetUserListQuery());
    }

    private void EditUser(UserDto? user)
    {
        if (user != null)
            Navigation.NavigateTo($"/users/edit/{user.Id}");
    }

    private async Task DeleteUser(UserDto? user)
    {
        if (user != null)
        {
            await Mediator.Send(new DeleteUserCommand(user.Id));
            users = await Mediator.Send(new GetUserListQuery());
        }
    }
}
```

### MVC Controller → Blazor + CQRS

```csharp
// OLD: MVC Controller
public class UsersController : Controller
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService)
    {
        _userService = userService;
    }

    public ActionResult Index()
    {
        var users = _userService.GetAll();
        return View(users);
    }

    public ActionResult Edit(int id)
    {
        var user = _userService.GetById(id);
        if (user == null)
            return HttpNotFound();
        return View(user);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public ActionResult Edit(UserViewModel model)
    {
        if (!ModelState.IsValid)
            return View(model);

        _userService.Update(model);
        return RedirectToAction("Index");
    }
}

// NEW: CQRS Handlers replace service methods
// Features/Users/Queries/GetUserList/
public record GetUserListQuery : IRequest<List<UserDto>>;

public class GetUserListHandler : IRequestHandler<GetUserListQuery, List<UserDto>>
{
    private readonly AppDbContext _db;

    public GetUserListHandler(AppDbContext db) => _db = db;

    public async Task<List<UserDto>> Handle(GetUserListQuery request, CancellationToken ct)
    {
        return await _db.Users
            .ProjectToType<UserDto>()
            .ToListAsync(ct);
    }
}

// Features/Users/Commands/UpdateUser/
public record UpdateUserCommand(int Id, UserDto Data) : IRequest<Result>;

public class UpdateUserHandler : IRequestHandler<UpdateUserCommand, Result>
{
    private readonly AppDbContext _db;

    public UpdateUserHandler(AppDbContext db) => _db = db;

    public async Task<Result> Handle(UpdateUserCommand request, CancellationToken ct)
    {
        var user = await _db.Users.FindAsync(request.Id);
        if (user == null)
            return Result.NotFound();

        request.Data.Adapt(user);
        await _db.SaveChangesAsync(ct);
        return Result.Success();
    }
}
```

### Form Handling

```html
<!-- OLD: MVC Form -->
@using (Html.BeginForm("Edit", "Users", FormMethod.Post))
{
    @Html.AntiForgeryToken()
    @Html.ValidationSummary(true)

    <div class="form-group">
        @Html.LabelFor(m => m.Name)
        @Html.TextBoxFor(m => m.Name, new { @class = "form-control" })
        @Html.ValidationMessageFor(m => m.Name)
    </div>

    <div class="form-group">
        @Html.LabelFor(m => m.Email)
        @Html.TextBoxFor(m => m.Email, new { @class = "form-control" })
        @Html.ValidationMessageFor(m => m.Email)
    </div>

    <button type="submit" class="btn btn-primary">Save</button>
}
```

```razor
<!-- NEW: Blazor Form with Telerik -->
<TelerikForm Model="@user" OnValidSubmit="@HandleSubmit">
    <FormValidation>
        <FluentValidationValidator />
    </FormValidation>

    <FormItems>
        <FormItem Field="@nameof(UserDto.Name)" LabelText="Name">
            <Template>
                <TelerikTextBox @bind-Value="@user.Name" />
            </Template>
        </FormItem>

        <FormItem Field="@nameof(UserDto.Email)" LabelText="Email">
            <Template>
                <TelerikTextBox @bind-Value="@user.Email" />
            </Template>
        </FormItem>
    </FormItems>

    <FormButtons>
        <TelerikButton ButtonType="ButtonType.Submit" ThemeColor="primary">Save</TelerikButton>
        <TelerikButton ButtonType="ButtonType.Button" OnClick="@Cancel">Cancel</TelerikButton>
    </FormButtons>
</TelerikForm>

@code {
    private UserDto user = new();

    private async Task HandleSubmit()
    {
        var result = await Mediator.Send(new UpdateUserCommand(user.Id, user));
        if (result.IsSuccess)
            Navigation.NavigateTo("/users");
    }
}
```

## ASP.NET Web Forms → Blazor

### Page Lifecycle → Component Lifecycle

| Web Forms Event | Blazor Equivalent |
|----------------|-------------------|
| Page_Init | Component constructor |
| Page_Load | OnInitialized / OnInitializedAsync |
| Page_PreRender | OnParametersSet / OnAfterRender |
| IsPostBack | (Not applicable - component state) |
| ViewState | @code { private fields } |
| Session | Inject session or use state container |

### Postback → Event Handlers

```aspx
<!-- OLD: Web Forms -->
<asp:Button ID="btnSave" runat="server" Text="Save" OnClick="btnSave_Click" />
<asp:GridView ID="gvUsers" runat="server" AutoGenerateColumns="false"
    OnRowCommand="gvUsers_RowCommand">
    <Columns>
        <asp:BoundField DataField="Name" HeaderText="Name" />
        <asp:ButtonField CommandName="Edit" Text="Edit" />
    </Columns>
</asp:GridView>
```

```csharp
// Web Forms code-behind
protected void btnSave_Click(object sender, EventArgs e)
{
    // Handle save
}

protected void gvUsers_RowCommand(object sender, GridViewCommandEventArgs e)
{
    if (e.CommandName == "Edit")
    {
        int id = Convert.ToInt32(e.CommandArgument);
        Response.Redirect($"Edit.aspx?id={id}");
    }
}
```

```razor
<!-- NEW: Blazor -->
<TelerikButton OnClick="@HandleSave">Save</TelerikButton>

<TelerikGrid Data="@users" TItem="UserDto">
    <GridColumns>
        <GridColumn Field="@nameof(UserDto.Name)" Title="Name" />
        <GridCommandColumn>
            <GridCommandButton Command="Edit" OnClick="@HandleEdit" />
        </GridCommandColumn>
    </GridColumns>
</TelerikGrid>

@code {
    private async Task HandleSave()
    {
        // Handle save
    }

    private void HandleEdit(GridCommandEventArgs args)
    {
        var user = (UserDto)args.Item;
        Navigation.NavigateTo($"/users/edit/{user.Id}");
    }
}
```

### ViewState → Component State

```csharp
// OLD: Web Forms - ViewState
protected void Page_Load(object sender, EventArgs e)
{
    if (!IsPostBack)
    {
        ViewState["EditMode"] = false;
        LoadData();
    }
}

protected void btnEdit_Click(object sender, EventArgs e)
{
    ViewState["EditMode"] = true;
    // Update UI
}

// NEW: Blazor - Component fields
@code {
    private bool isEditMode = false;
    private List<UserDto> users = new();

    protected override async Task OnInitializedAsync()
    {
        await LoadData();
    }

    private void EnableEditMode()
    {
        isEditMode = true;
        StateHasChanged();  // Re-render component
    }

    private async Task LoadData()
    {
        users = await Mediator.Send(new GetUserListQuery());
    }
}
```

### User Controls → Child Components

```aspx
<!-- OLD: Web Controls (UserCard.ascx) -->
<%@ Control Language="C#" AutoEventWireup="true" CodeBehind="UserCard.ascx.cs" %>
<div class="user-card">
    <h3><asp:Label ID="lblName" runat="server" /></h3>
    <p><asp:Label ID="lblEmail" runat="server" /></p>
</div>
```

```razor
<!-- NEW: Blazor Component (UserCard.razor) -->
<div class="user-card">
    <h3>@User.Name</h3>
    <p>@User.Email</p>
</div>

@code {
    [Parameter]
    public UserDto User { get; set; } = new();
}

<!-- Usage -->
<UserCard User="@currentUser" />
```

### Master Pages → Layouts

```aspx
<!-- OLD: Master Page (Site.Master) -->
<%@ Master Language="C#" AutoEventWireup="true" CodeBehind="Site.master.cs" %>
<!DOCTYPE html>
<html>
<head>
    <title><asp:ContentPlaceHolder ID="TitleContent" runat="server" /></title>
</head>
<body>
    <nav><!-- Navigation --></nav>
    <main>
        <asp:ContentPlaceHolder ID="MainContent" runat="server" />
    </main>
    <footer><!-- Footer --></footer>
</body>
</html>
```

```razor
<!-- NEW: Blazor Layout (MainLayout.razor) -->
@inherits LayoutComponentBase

<!DOCTYPE html>
<html>
<head>
    <title>@Title</title>
</head>
<body>
    <TelerikRootComponent>
        <nav>
            <NavMenu />
        </nav>
        <main>
            @Body
        </main>
        <footer><!-- Footer --></footer>
    </TelerikRootComponent>
</body>
</html>

@code {
    [CascadingParameter]
    public string? Title { get; set; }
}
```

## Common Control Mappings

| Web Forms / MVC | Telerik Blazor |
|----------------|----------------|
| asp:TextBox | TelerikTextBox |
| asp:DropDownList | TelerikDropDownList |
| asp:CheckBox | TelerikCheckBox |
| asp:RadioButton | TelerikRadioGroup |
| asp:Calendar | TelerikCalendar |
| asp:GridView | TelerikGrid |
| asp:ListView | TelerikListView |
| asp:TreeView | TelerikTreeView |
| asp:Menu | TelerikMenu |
| asp:FileUpload | TelerikUpload |
| asp:Wizard | TelerikWizard |

## Validation Migration

```csharp
// OLD: MVC Data Annotations + jQuery Validation
public class UserViewModel
{
    [Required(ErrorMessage = "Name is required")]
    [StringLength(100)]
    public string Name { get; set; }

    [Required]
    [EmailAddress]
    public string Email { get; set; }
}

// NEW: FluentValidation (Recommended)
public class UserValidator : AbstractValidator<UserDto>
{
    public UserValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Name is required")
            .MaximumLength(100);

        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress();
    }
}

// Registration in Program.cs
builder.Services.AddValidatorsFromAssemblyContaining<UserValidator>();
```

## JavaScript Integration

```javascript
// OLD: jQuery in MVC/Web Forms
$(document).ready(function() {
    $('#btnSave').click(function() {
        $.ajax({
            url: '/api/users',
            method: 'POST',
            data: JSON.stringify(userData),
            success: function(result) {
                alert('Saved!');
            }
        });
    });
});
```

```razor
<!-- NEW: Blazor - C# for most interactions -->
@inject IJSRuntime JS

<TelerikButton OnClick="@HandleSave">Save</TelerikButton>

@code {
    private async Task HandleSave()
    {
        var result = await Mediator.Send(new SaveUserCommand(userData));

        // Only use JS interop when necessary
        if (result.IsSuccess)
            await JS.InvokeVoidAsync("alert", "Saved!");
    }
}

<!-- Or for complex JS libraries, create interop -->
@inject IJSRuntime JS

@code {
    private async Task InitializeChart()
    {
        await JS.InvokeVoidAsync("initChart", chartElement, chartData);
    }
}
```

## Authentication Migration

```csharp
// OLD: Forms Authentication
FormsAuthentication.SetAuthCookie(username, createPersistentCookie);
FormsAuthentication.SignOut();

// NEW: ASP.NET Core Identity with Blazor
// Program.cs
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie();

builder.Services.AddCascadingAuthenticationState();

// In Blazor component
@inject AuthenticationStateProvider AuthStateProvider

<AuthorizeView>
    <Authorized>
        <p>Welcome, @context.User.Identity?.Name</p>
        <TelerikButton OnClick="@Logout">Logout</TelerikButton>
    </Authorized>
    <NotAuthorized>
        <LoginForm />
    </NotAuthorized>
</AuthorizeView>

@code {
    private async Task Logout()
    {
        // Sign out logic
    }
}
```

## Incremental Migration Strategy

1. **Create new Blazor project alongside existing MVC/Web Forms**
2. **Share database and business logic via class libraries**
3. **Migrate one feature at a time to Blazor**
4. **Use reverse proxy to route to appropriate app**
5. **Gradually reduce MVC/Web Forms until removed**

```
                    ┌─────────────────┐
    User Request → │  Reverse Proxy  │
                    └────────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │  Blazor   │   │    MVC    │   │ Web Forms │
    │   (new)   │   │ (legacy)  │   │ (legacy)  │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                    ┌───────────────┐
                    │ Shared Logic  │
                    │  (Library)    │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │   Database    │
                    └───────────────┘
```
