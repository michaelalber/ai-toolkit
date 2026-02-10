---
name: blazor-telerik-component
description: Telerik UI for Blazor component patterns for grids, forms, and dialogs. Use when building Blazor UI with Telerik components, implementing data grids, or creating form/dialog workflows.
---

# Telerik Blazor Component Patterns

> "The best interface is no interface. The next best is one so intuitive that users never notice it."
> -- Golden Krishna

## Core Philosophy

This skill governs the composition and integration of Telerik UI for Blazor components. Every component decision must balance user experience, data integrity, accessibility, and performance.

**Non-Negotiable Constraints:**

1. **Component Composition Over Inheritance** -- Build complex UIs by composing small, focused Telerik components rather than extending or wrapping them in deep hierarchies
2. **Data Binding Integrity** -- All data flows must be explicit. Two-way binding (`@bind-Value`) requires a backing property with proper change notification. One-way binding requires explicit event handlers for updates
3. **Accessibility First** -- Every interactive component must be keyboard navigable and screen-reader compatible. WCAG 2.1 AA compliance is the minimum threshold
4. **Server vs WASM Awareness** -- Know your hosting model. Server-side Blazor has latency implications for frequent UI updates. WASM has payload size constraints. Component choices must respect the hosting model
5. **No Silent Failures** -- Every data operation must surface feedback to the user: loading indicators during fetch, validation messages on input, error states on failure, and confirmation on success

## Domain Principles Table

| # | Principle | Description | Priority |
|---|-----------|-------------|----------|
| 1 | **Component Encapsulation** | Each component owns its state, markup, and behavior. Parent components communicate via parameters and `EventCallback`. No direct child manipulation. | Critical |
| 2 | **Two-Way Binding Discipline** | Use `@bind-Value` only for form inputs. Use one-way binding with explicit `ValueChanged` handlers when transformation or validation is needed before state update. | Critical |
| 3 | **Virtualization by Default** | Any list or grid displaying more than 50 items must use virtualization (`ScrollMode="ScrollMode.Virtual"`). Never render unbounded collections without paging or virtual scroll. | High |
| 4 | **WCAG Accessibility** | All form fields require labels. All interactive elements require `aria-` attributes where Telerik does not provide them automatically. Color alone must never convey meaning. | Critical |
| 5 | **Responsive Layout** | Use `TelerikStackLayout` and `TelerikGridLayout` for responsive arrangements. Never use fixed pixel widths on containers. Test at 320px, 768px, and 1200px breakpoints. | High |
| 6 | **Centralized State Management** | For cross-component state, use a cascading parameter or injected state service. Never rely on chained `EventCallback` across more than two levels. | High |
| 7 | **Explicit Event Handling** | Every user interaction (click, select, edit) must have a named handler method. No inline lambdas for complex logic. Event handlers must be `async Task`, not `async void`. | High |
| 8 | **Loading State Coverage** | Every async data operation must display a loading indicator. Use `TelerikLoaderContainer` or grid built-in loading. The user must never stare at a blank component. | Critical |
| 9 | **Error Boundary Protection** | Wrap component sections in `<ErrorBoundary>` with `<ErrorContent>`. Provide user-friendly fallback UI. Log the exception for diagnostics. | High |
| 10 | **Theme Consistency** | Use only Telerik theme variables and classes for styling. Never override Telerik CSS with inline styles. Maintain a single theme across all components. | Medium |

## Workflow

### Component Development Lifecycle

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌───────────┐   ┌────────────┐   ┌────────┐   ┌─────────┐     │
│  │ Component  │──>│ Data Model │──>│ Layout │──>│ Binding │     │
│  │ Selection  │   │  Design    │   │        │   │         │     │
│  └───────────┘   └────────────┘   └────────┘   └─────────┘     │
│                                                      │          │
│  ┌───────────────┐   ┌──────────────┐   ┌───────────┐          │
│  │ Accessibility  │<──│  Validation  │<──│  Events   │<─────────│
│  │    Check       │   │              │   │           │          │
│  └───────────────┘   └──────────────┘   └───────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Step-by-Step

1. **Component Selection** -- Identify the correct Telerik component for the requirement
2. **Data Model Design** -- Define the C# model, DTO, or view model that backs the component
3. **Layout** -- Position the component within the page using Telerik layout containers
4. **Binding** -- Wire data to the component (one-way or two-way as appropriate)
5. **Events** -- Implement event handlers for user interactions
6. **Validation** -- Add DataAnnotations or FluentValidation rules; wire to the form
7. **Accessibility Check** -- Verify keyboard navigation, screen reader behavior, and WCAG compliance

### Component Selection Decision Tree

```
What does the user need to do?
│
├─ View/manage tabular data?
│  └─ TelerikGrid
│     ├─ < 100 rows, simple ──> Client-side operations
│     ├─ > 100 rows ──────────> Virtual scrolling + server-side OnRead
│     └─ Hierarchical data ───> Detail template or TreeList
│
├─ Fill out a form?
│  └─ TelerikForm + EditForm
│     ├─ Simple fields ───────> Auto-generated form items
│     ├─ Complex layout ──────> FormItem with Template
│     └─ Multi-step ──────────> TelerikWizard or custom stepper
│
├─ Confirm an action or show details?
│  └─ Dialog vs Window
│     ├─ Simple confirm ──────> TelerikDialog (modal)
│     ├─ Complex content ─────> TelerikWindow (draggable, resizable)
│     └─ Notification only ───> TelerikNotification
│
├─ Visualize data?
│  └─ TelerikChart
│     ├─ Trends ──────────────> Line/Area chart
│     ├─ Comparisons ─────────> Bar/Column chart
│     └─ Proportions ─────────> Pie/Donut chart
│
└─ Schedule / timeline?
   └─ TelerikScheduler
      ├─ Day/Week/Month ──────> Standard views
      └─ Timeline ────────────> Timeline view
```

## State Block Format

Maintain state across conversation turns using this block:

```
<blazor-component-state>
step: [Component Selection | Data Model | Layout | Binding | Events | Validation | Accessibility Check]
component_type: [grid | form | dialog | chart | scheduler]
data_source: [description of the data source or API endpoint]
accessibility_checked: [true | false]
last_action: [what was done]
next_action: [what's next]
blockers: [issues preventing progress]
</blazor-component-state>
```

### Example State Progression

```
<blazor-component-state>
step: Binding
component_type: grid
data_source: /api/orders - paginated endpoint returning OrderDto
accessibility_checked: false
last_action: Defined grid columns with sorting and filtering
next_action: Implement OnRead handler for server-side operations
blockers: none
</blazor-component-state>
```

## Output Templates

### Grid Setup Template

```markdown
## Grid Component: [Entity Name]

**Data Source**: [API endpoint or service method]
**Operations**: [Read / Create / Update / Delete]
**Rows Expected**: [estimate]

### Model

```csharp
public class [Entity]GridDto
{
    public int Id { get; set; }
    // ... properties matching grid columns
}
```

### Component

```razor
<TelerikGrid Data="@GridData"
             Pageable="true"
             Sortable="true"
             FilterMode="@GridFilterMode.FilterRow"
             OnRead="@OnGridRead"
             TItem="[Entity]GridDto"
             Height="600px">
    <GridColumns>
        <!-- columns here -->
    </GridColumns>
</TelerikGrid>
```

### Verification
- [ ] Loading state displays during data fetch
- [ ] Empty state displays when no data
- [ ] Error state displays on API failure
- [ ] Keyboard navigation works for all interactive elements
- [ ] Screen reader announces column headers and cell content
```

### Form Creation Template

```markdown
## Form Component: [Entity Name]

**Operation**: [Create | Edit]
**Validation**: [DataAnnotations | FluentValidation]

### Model

```csharp
public class [Entity]FormModel
{
    [Required(ErrorMessage = "[Field] is required")]
    public string Name { get; set; }
    // ... validated properties
}
```

### Component

```razor
<TelerikForm Model="@FormModel"
             OnValidSubmit="@HandleSubmit"
             ValidationMessageType="@FormValidationMessageType.Tooltip">
    <FormItems>
        <!-- form items here -->
    </FormItems>
    <FormButtons>
        <TelerikButton ButtonType="@ButtonType.Submit" ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">Save</TelerikButton>
    </FormButtons>
</TelerikForm>
```

### Verification
- [ ] All required fields show validation messages
- [ ] Tab order follows visual layout
- [ ] Submit button disabled during async save
- [ ] Success/error notification displays after operation
```

### Dialog Workflow Template

```markdown
## Dialog: [Purpose]

**Type**: [Confirmation | CRUD Form | Information]
**Modal**: [true | false]

### Component

```razor
<TelerikDialog @bind-Visible="@IsDialogVisible"
               Title="[Dialog Title]"
               Width="500px">
    <DialogContent>
        <!-- content here -->
    </DialogContent>
    <DialogButtons>
        <TelerikButton OnClick="@OnCancel">Cancel</TelerikButton>
        <TelerikButton OnClick="@OnConfirm" ThemeColor="@ThemeConstants.Button.ThemeColor.Primary">Confirm</TelerikButton>
    </DialogButtons>
</TelerikDialog>
```

### Verification
- [ ] Dialog traps focus when open
- [ ] Escape key closes dialog
- [ ] Action buttons are clearly labeled
- [ ] Dialog content is announced to screen readers
```

## AI Discipline Rules

### CRITICAL: Always Check Accessibility

Before marking any component implementation as complete:
1. Verify all form fields have associated `<label>` elements or `Label` parameters
2. Verify keyboard navigation works for every interactive element
3. Verify color is not the sole indicator of state (use icons or text alongside)
4. Verify focus management in dialogs (trap focus, restore on close)

If accessibility has not been checked, STOP and perform the check.

### CRITICAL: Never Skip Loading States

Every component that fetches data must:
1. Show a loading indicator immediately when the fetch begins
2. Hide the indicator only when data arrives or an error occurs
3. Never display an empty component while data is in transit
4. Use `TelerikLoaderContainer` or the grid's built-in `LoaderType` parameter

If a data-bound component has no loading state, STOP and add one.

### CRITICAL: Always Handle Empty and Error States

Every data-driven component must define three visual states:
1. **Loading** -- spinner or skeleton while fetching
2. **Empty** -- friendly message when data set is empty (use grid `NoDataTemplate`)
3. **Error** -- user-friendly message with retry option when the operation fails

If any of these states is missing, STOP and implement it.

### CRITICAL: Never Hardcode Grid Columns

Grid columns must always be derived from:
1. A strongly-typed model with explicit column definitions in Razor markup
2. Or a dynamic column generation loop when columns are runtime-configurable

Never use magic strings for field names. Always use `nameof()` or the `Field` parameter with a property expression. This ensures compile-time safety and refactoring support.

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It Is Wrong | Correct Approach |
|---|---|---|
| **Wrapping TelerikGrid in a custom component that re-exposes all parameters** | Creates a leaky abstraction that breaks on Telerik updates and hides configuration | Compose grids directly in page components. Extract only shared column definitions or OnRead logic into services |
| **Using `async void` for event handlers** | Exceptions are swallowed silently, UI state becomes inconsistent | Always use `async Task` return type. Telerik `EventCallback` already supports `Task` |
| **Fetching all data client-side then filtering in the grid** | Destroys performance for large datasets, wastes bandwidth and memory | Use `OnRead` with `DataSourceRequest` to push filtering, sorting, and paging to the server |
| **Inline CSS overrides on Telerik components** | Breaks theme consistency, may be overwritten by Telerik updates, untestable | Use Telerik theme variables, CSS custom properties, or a separate stylesheet with scoped classes |
| **Showing raw exception messages in dialogs** | Exposes internals to users, poor UX, potential security leak | Map exceptions to user-friendly messages. Log the full exception server-side. Show a generic error with a correlation ID |
| **Binding complex objects directly to form fields** | Causes unexpected re-renders, makes validation difficult, tight coupling to domain model | Create a dedicated form model (DTO/ViewModel) and map to/from the domain entity |
| **Nesting dialogs more than one level deep** | Confusing UX, broken focus management, accessibility nightmare | Redesign the flow: use a wizard, step-based form, or navigate to a new page instead |

## Error Recovery

### Problem: Component Does Not Render or Renders Blank

```
Symptom: Telerik component appears as empty space or is missing entirely
```

**Action:**
1. Verify the `TelerikRootComponent` is present in `App.razor` or the layout
2. Check that `builder.Services.AddTelerikBlazor()` is called in `Program.cs`
3. Confirm the Telerik CSS theme is referenced in `_Host.cshtml` or `index.html`
4. Check browser console for JavaScript interop errors
5. Verify the component has a `Data` source or `TItem` type parameter set

### Problem: Data Binding Does Not Update the UI

```
Symptom: Data changes in code but the grid/form does not reflect the update
```

**Action:**
1. Verify the data collection is an `ObservableCollection<T>` or that you call `StateHasChanged()` after mutation
2. For grids using `OnRead`, verify you are setting `args.Data` and `args.Total` in the handler
3. For forms, verify `@bind-Value` is used (not just `Value`) or that `ValueChanged` calls `StateHasChanged()`
4. Check that the property implements `INotifyPropertyChanged` if using one-way binding with manual updates
5. Ensure you are not replacing the collection reference without re-triggering the grid's data source

### Problem: Grid Performance Degrades with Large Datasets

```
Symptom: Grid becomes slow to render, scroll, or filter beyond a few hundred rows
```

**Action:**
1. Switch from client-side data to `OnRead` with server-side operations
2. Enable virtual scrolling: `ScrollMode="ScrollMode.Virtual"` with `PageSize` and `RowHeight`
3. Reduce the number of visible columns; hide non-essential columns behind a column chooser
4. Avoid complex templates in cells that are always visible; use detail templates for expandable content
5. Profile the `OnRead` handler to ensure the server query is efficient (indexed, paginated)

### Problem: Validation Messages Do Not Appear

```
Symptom: Form submits without showing validation errors, or errors appear in wrong location
```

**Action:**
1. Verify the form model has `DataAnnotations` attributes or a registered `FluentValidation` validator
2. Confirm the `TelerikForm` is inside an `EditForm` or uses its own `Model` parameter
3. Check that `ValidationMessageType` is set (e.g., `FormValidationMessageType.Tooltip` or `Inline`)
4. For custom form layouts, verify each field has a `<ValidationMessage For="@(() => Model.Property)" />`
5. Ensure `OnValidSubmit` (not `OnSubmit`) is used so validation runs before the handler

### Problem: Dialog Focus and Keyboard Navigation Broken

```
Symptom: Tab key escapes the dialog, screen reader does not announce dialog content
```

**Action:**
1. Verify the dialog uses `Modal="true"` to enable focus trapping
2. Check that `CloseOnOverlayClick` and `ShowCloseButton` are configured appropriately
3. Ensure dialog buttons have explicit `aria-label` attributes if the text is ambiguous
4. Test with Escape key -- it should close the dialog and return focus to the trigger element
5. Add `role="dialog"` and `aria-modal="true"` only if Telerik does not set them automatically (check rendered HTML)

## Integration with Other Skills

- **`dotnet-vertical-slice`** -- Grid and form components are the UI layer of a vertical slice. The slice defines the API endpoint, command/query handler, and data access. This skill provides the Blazor component that consumes that endpoint. When building a new feature, start with `dotnet-vertical-slice` for the backend, then use this skill for the UI
- **`ef-migration-manager`** -- When a grid or form requires a new database column or table, coordinate with `ef-migration-manager` to create the migration before building the UI. The form model and grid DTO should match the entity shape defined in the migration
- **`nuget-package-scaffold`** -- If you are building a reusable Telerik component library as a NuGet package, use `nuget-package-scaffold` for the package structure, then apply the patterns from this skill for the component implementations

## Reference Files

See detailed patterns and code examples:
- [Grid Patterns](references/grid-patterns.md) -- Comprehensive TelerikGrid configuration, data binding, editing, and performance patterns
- [Form and Dialog Patterns](references/form-dialog-patterns.md) -- TelerikForm, TelerikDialog, TelerikWindow, validation, and multi-step workflows
