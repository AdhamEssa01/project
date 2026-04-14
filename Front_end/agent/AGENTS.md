---
applyTo: '**'
---

# Plan & Act Mode Instructions

You have two modes of operation:

1. **Plan Mode** - Analyze and create strategy without making changes
2. **Act Mode** - Execute approved plans and make actual modifications

## Rules:
- Start in **Plan Mode** by default.
- Print `# Mode: PLAN` in plan responses; never modify files in PLAN.
- Switch to **Act Mode** only when the user types `ACT`; print `# Mode: ACT`.
- After any ACT response, return to PLAN.
- When the user types `PLAN`, switch to PLAN immediately.


# Role and Expertise

- Act as an Angular expert with deep understanding of Angular 20 best practices
- Provide guidance for writing high-quality, maintainable Angular code
- Help implement Angular features following official style guide and best practices
- Assist in:
  1. Component architecture and design
  2. State management solutions
  3. Performance optimization
  4. Code organization and structure
  5. TypeScript best practices
  6. Angular services and dependency injection
  7. Reactive programming with RxJS
  8. Angular forms (Reactive)
  9. Angular routing and lazy loading

# Angular Version

- This project uses Angular version 20

## ✅ DO generate code using Angular 20 best practices:

- Use **standalone components** (no NgModules).
- Use the **new control flow syntax**: `@if`, `@for`, `@switch`. Do NOT use `*ngIf`, `*ngFor`, etc.
- Do not use the **signals-based reactivity model** (like `signal()`, `computed()`, `effect()`). Use traditional `@Input()` and `@Output()` decorators instead of signal inputs.
- Use **zoneless change detection** with `provideZonelessChangeDetection()` and `ChangeDetectionStrategy.OnPush` if appropriate, but avoid signals.
- Use `createComponent()` with `inputBinding()`, `outputBinding()`, or `bindings` for dynamic components.
- Use **TypeScript 5.8+** and assume `strict` mode is enabled.
- Assume **Angular CLI generates standalone components by default**.
- Use **Angular Material 3** components where applicable (e.g., tonal buttons).

## ❌ DO NOT:

- Do NOT use `NgModule`, `BrowserModule`, or `imports` arrays.
- Do NOT use `*ngIf`, `*ngFor`, `*ngSwitch`. Use `@if`, `@for`, `@switch` instead.
- Do NOT use `ViewContainerRef` + `TemplateRef` with old structural directives.
- Do NOT use `Zone.js` or assume it's available.
- Do NOT use `@Injectable({ providedIn: 'root' })` unless creating a shared service.

## 🧪 Additional Notes:

- Tests use **TestBed with provideMockStore()** or **standalone component setup**.
- Project uses Vite (optional, but if used, avoid Webpack-specific syntax).

# PrimeNG for UI components

- Use PrimeNG for all UI components
- Follow PrimeNG documentation for implementation details 'https://primeng.org/'
- Use PrimeNG themes for consistent styling
- in components , don't write custom styles but use PrimeNG classes

# Library Management Guidelines

- Use the latest stable version compatible with Angular 20
- Verify compatibility with existing project dependencies
- Keep all libraries up to date while maintaining compatibility
- Read the official documentation for the libraries before use

# Component Architecture Patterns

1. **Simple Models (Dialog Approach):**

   - For simple entities with minimal fields, use dialogs for add/edit/view operations
   - Use PrimeNG Dialog component for modal interactions without routing
   - Keep operations within the same page context for better user experience with simple forms

2. **Complex Models (Routing Approach):**

   - For complex entities with multiple fields which may need sections/steps, use separate pages with routing
   - Use dedicated routes for add/edit/view operations when dealing with multi-step forms or extensive data
   - Implement proper navigation and state management for complex workflows

3. **Dropdown Controls Implementation:**
   - Always search for and use the appropriate backend API endpoints for dropdown data
   - For entity-specific dropdowns, use the respective service's dropdown methods (e.g., getSpecialitiesDropdown())
   - Implement proper caching and error handling for dropdown data loading

4. **Select List with Add New Record (Enriched Dropdown Pattern):**

   Use this pattern whenever a `p-select` dropdown needs to let the user add a new record or navigate to a management page without leaving the current form context.

   **HTML Template:**
   ```html
   <div class="field mb-4">
     <label for="entityId" class="font-semibold mb-2 block">
       <i class="pi pi-[icon] mr-2 text-primary"></i>
       {{ 'Feature.Form.Fields.Entity.Label' | localize }}
       <span class="text-red-500">*</span>
     </label>
     <div class="flex gap-2">
       <p-select
         id="entityId"
         formControlName="entityId"
         [options]="entities"
         optionLabel="name"
         optionValue="id"
         [placeholder]="'Feature.Form.Fields.Entity.Placeholder' | localize"
         [filter]="true"
         filterBy="name"
         [showClear]="true"
         appendTo="body"
         [class.ng-invalid]="isFieldInvalid('entityId')"
         [class.ng-dirty]="form.get('entityId')?.dirty"
         styleClass="flex-1"
       >
         <!-- Custom selected item display -->
         <ng-template pTemplate="selectedItem" let-selectedOption>
           @if (selectedOption) {
             <div class="flex align-items-center gap-2">
               <i class="pi pi-[icon] text-primary"></i>
               <span>{{ selectedOption.name }}</span>
             </div>
           }
         </ng-template>

         <!-- Custom item row in dropdown list -->
         <ng-template pTemplate="item" let-option>
           <div class="flex align-items-center gap-2">
             <i class="pi pi-[icon] text-primary"></i>
             <div>
               <div class="font-medium">{{ option.name }}</div>
               @if (option.description) {
                 <div class="text-sm text-500">{{ option.description }}</div>
               }
             </div>
           </div>
         </ng-template>

         <!-- Footer with Add New + Manage All actions -->
         <ng-template pTemplate="footer">
           <div class="border-top-1 surface-border">
             <div
               class="flex align-items-center gap-2 px-3 py-2 cursor-pointer bg-green-50 hover:bg-green-100 transition-colors"
               (click)="onAddNewEntity()"
             >
               <i class="pi pi-plus text-green-600"></i>
               <span class="text-lg text-green-600 font-semibold">{{ 'Feature.Entity.Actions.AddNew' | localize }}</span>
             </div>
             <div
               class="flex align-items-center gap-2 px-3 py-2 cursor-pointer bg-blue-50 hover:bg-blue-100 transition-colors border-top-1 surface-border"
               (click)="onManageEntities()"
             >
               <i class="pi pi-cog text-blue-600"></i>
               <span class="text-lg text-blue-600 font-semibold">{{ 'Feature.Entity.Actions.ManageAll' | localize }}</span>
             </div>
           </div>
         </ng-template>
       </p-select>

       <!-- Refresh button alongside the select -->
       <p-button
         icon="pi pi-refresh"
         [outlined]="true"
         severity="secondary"
         size="large"
         (onClick)="onRefreshEntities()"
         [loading]="loadingEntities"
         [pTooltip]="'Common.Actions.Refresh' | localize"
         tooltipPosition="top"
       ></p-button>
     </div>
     @if (isFieldInvalid('entityId')) {
       <small class="p-error block mt-1">{{ getFieldError('entityId') }}</small>
     }
   </div>
   ```

   **TypeScript — required state:**
   ```ts
   entities: EntitySelectDto[] = [];
   loadingEntities = false;
   private nestedDialogRef: DynamicDialogRef | null = null;
   managementPageOpened = false;
   ```

   **TypeScript — required methods:**
   ```ts
   onRefreshEntities(): void {
     this.loadEntities();
   }

   onAddNewEntity(): void {
     this.nestedDialogRef = this.dialogService.open(AddEntityDialogComponent, {
       header: this.L('Feature.Entity.Titles.Add'),
       width: '500px',
       modal: true,
       dismissableMask: false,
     });

     this.nestedDialogRef.onClose
       .pipe(takeUntil(this.destroy$))
       .subscribe((result) => {
         if (result?.success) {
           this.loadEntities();   // reload list after successful add
         }
       });
   }

   onManageEntities(): void {
     const url = this.router.serializeUrl(
       this.router.createUrlTree(['/entities'])
     );
     window.open(url, '_blank');
     this.managementPageOpened = true;
   }
   ```

   **Rules:**
   - Always use `takeUntil(this.destroy$)` when subscribing to `nestedDialogRef.onClose` to prevent memory leaks.
   - Reload the dropdown list (`loadEntities()`) only when `result?.success` is `true`.
   - Use `styleClass="flex-1"` on the `p-select` so it stretches to fill the flex row alongside the refresh button.
   - Always use `appendTo="body"` to prevent z-index clipping inside dialogs.
   - The **Add New** row uses green (`bg-green-50 / text-green-600`) and the **Manage All** row uses blue (`bg-blue-50 / text-blue-600`) — keep these colors consistent across all usages.

# Enum Strategy — Backend Owns All Enums

> **CRITICAL RULE: Do NOT define TypeScript enums in the frontend. Enums belong exclusively in the backend.**

## Why No Frontend Enums

The backend already defines every enum with:
- **Numeric values** (e.g., `Open=1, Resolved=2`)
- **Localized display names** via `[LocalizationKey]` attributes
- **Color codes** via `[Color]` attributes (e.g., `ColorConstants.Success`)

Duplicating them in the frontend creates drift (wrong values, wrong labels) and breaks localization.

## How Enums Are Exposed by the Backend

The backend exposes each enum as a select-list API endpoint returning `SelectOptionDto[]`:

```
GET /api/app/[feature]-enum/[entity]-statuses-dropdown
```

Response shape (`SelectOptionDto`):
```ts
export interface SelectOptionDto {
  value: string;   // numeric enum value as string e.g. "1"
  text: string;    // localized display name e.g. "مفتوح" / "Open"
  color: string;   // color code e.g. "info", "success", "#34d399"
}
```

Some features return richer DTOs with additional fields like `icon` or `name`.

## Frontend Model Convention

### 1. DTO properties typed as `number` (not enum)

In response models, type enum fields as `number`. Companion display fields come from the backend:

```ts
// ✅ CORRECT — enum value is a plain number
export interface CommentListItemDto {
  id: string;
  status: number;       // numeric value from backend
  statusName: string;   // localized label — returned by backend list API
  statusColor: string;  // color code — returned by backend list API
}

// ❌ WRONG — importing and using a frontend enum
import { CommentStatus } from '../enums/comment-status.enum';
export interface CommentListItemDto {
  status: CommentStatus;  // Never do this
}
```

### 2. Select-list API call — always cached

In the feature service, expose a cached method that calls the backend select-list endpoint:

```ts
// comment.service.ts
private statusesDropdown$: Observable<SelectOptionDto[]> | null = null;

getStatusesDropdown(): Observable<SelectOptionDto[]> {
  if (!this.statusesDropdown$) {
    this.statusesDropdown$ = this.http
      .get<SelectOptionDto[]>(`${this.apiUrl}/statuses-dropdown`)
      .pipe(shareReplay(1));  // ← cache after first call, no re-fetching
  }
  return this.statusesDropdown$;
}
```

### 3. Using status in templates

Use the backend-returned `statusName` and `statusColor` directly from DTOs — never map a number to a label in the frontend:

```html
<!-- ✅ CORRECT — name and color come from the DTO -->
<p-tag [value]="item.statusName" [style.background]="item.statusColor + '20'" />

<!-- ❌ WRONG — mapping enum value to label in template -->
<p-tag [value]="getStatusLabel(item.status)" />
```

### 4. Filter/form dropdowns

Load options from the select-list API and bind directly to the dropdown:

```ts
// In component
statusOptions: SelectOptionDto[] = [];

ngOnInit() {
  this.service.getStatusesDropdown().subscribe(opts => {
    this.statusOptions = opts;
  });
}
```

```html
<p-select
  [(ngModel)]="filter.status"
  [options]="statusOptions"
  optionLabel="text"
  optionValue="value"
  placeholder="All Statuses" />
```

### 5. Filter DTO convention

Filter models use `string` or `number` for enum filter params (matching the `SelectOptionDto.value` type), not a frontend enum:

```ts
// ✅ CORRECT
export interface CommentFilterModel {
  status?: string;  // holds the SelectOptionDto.value e.g. "1"
}

// ❌ WRONG
export interface CommentFilterModel {
  status?: CommentStatus;  // No frontend enum reference
}
```

## Anti-Patterns (Never Do)

| ❌ Anti-pattern | ✅ Correct approach |
|---|---|
| `export enum TaskStatus { Todo = 1 }` in frontend | Delete it — type as `number` in DTOs |
| `export type CommentStatus = 'Open' \| 'Resolved'` | Delete it — use `number` or `string` from API |
| Mapping `status === 1 ? 'Open' : 'Closed'` in component | Use `item.statusName` from the DTO |
| Hardcoding colors per status in component SCSS | Use `item.statusColor` from the DTO |
| Calling select-list API on every component init | Cache with `shareReplay(1)` in the service |
| Redefining enum values that differ from backend | Frontend has no source of truth for enum values |

# Code Quality Standards

1. Architecture Guidelines:

   - use standalone components as the primary development approach
   - Only use NgModules when absolutely necessary
   - Keep modules minimal and focused when they are required
   - Follow Angular's modular architecture
   - Implement lazy loading for feature modules
   - Use smart and presentational components pattern
   - Keep components small and focused
   - Follow the Single Responsibility Principle

2. Standalone Components Guidelines:

   - Use standalone: true in component decorators by default
   - Import dependencies directly in components using imports array
   - Leverage standalone directives and pipes
   - Use route loading with loadComponent instead of loadChildren where possible

3. Performance Best Practices:

   - Implement OnPush change detection where appropriate
   - Use async pipe for observables
   - Avoid memory leaks by properly unsubscribing
   - Implement proper caching strategies
   - Use trackBy with ngFor directives

4. Testing Requirements:
   - Don't write unit tests
# Code Organization Standards

1. File Separation Requirements:

   - Each component MUST be split into separate files:
     - `component-name.component.ts` - TypeScript logic
     - `component-name.component.html` - Template
     - `component-name.component.scss` - Styles
   - NEVER include templates or styles inline within the TypeScript file

2. Component Creation Guidelines:

   - Always include the `--style=scss` flag to ensure SCSS file creation
   - Always use kebab-case for file and folder names
   - Component class names should use PascalCase and end with 'Component'

3. File Organization:
   - Group component files together in a dedicated folder
   - Keep related files close to their parent components
   - Example structure:
     ```
     feature-name/
     ├── components/
     ├── dialogs/
     ├── models/
     └── services/
     ```

# Project Structure

```
src/
└── app/
    ├── core/           # Singleton services, guards, and interceptors
    │                   # Imported only in AppModule
    │
    ├── features/       # Feature modules (lazy-loaded)
    │                   # Each feature is a separate business domain
    │
    ├── layout/         # App shell components split into two scopes:
    │                   #   • main-layout   – global app shell (header + side nav) used by all standard feature routes
    │                   #   • project-layout – isolated shell (header + project side nav) used exclusively inside a project workspace
    │
    └── shared/         # Reusable components, pipes, and directives
                       # Can be imported in any feature module
```

## Features Folder Naming Convention

The `features/` folder has **two scopes**: global features and project workspace features. Each has its own folder location — but both use the **same naming rule**: plain, unprefixed, plural names.

### Global features — `features/<feature-name>/`
```
features/
├── campaigns/
├── tasks/
├── faqs/
├── prospects/
└── projects/
```

### Project workspace features — `features/projects/workspace/<feature-name>/`
```
features/projects/workspace/
├── overview/           ✅ NOT project-overview/
├── leads/              ✅ NOT project-leads/
├── tasks/              ✅ NOT project-tasks/
├── posts/              ✅ NOT project-posts/
├── faqs/               ✅ NOT faq/
├── campaigns/
├── comments/
├── conversations/
├── marketing-profile/
├── auto-reply/
├── chatbot/
├── question-bank/
└── team-members/
```

### Rules
- **No `project-` prefix** inside `workspace/` — the path already provides the scope context.
- **Always plural** — `faqs/`, `tasks/`, `leads/`, not `faq/`, `task/`, `lead/`.
- There is **no naming conflict** between `features/tasks/` and `features/projects/workspace/tasks/` — they live in separate paths.

This structure follows Angular best practices with:

- Core module for singleton services and guards
- Feature modules for specific functionality domains
- Shared module for reusable components
- Clear separation of concerns
- Lazy-loading ready architecture

## Localization Guidelines

1. **Base Component Usage**

   - All components requiring localization MUST extend the shared BaseComponent from path 'shared/components/base-component/base.component'.
   - The base component provides the `L` method, which must be used for translating strings in component TypeScript files.

2. **Resource File Structure & Naming**

   - Resource files are organized as **split JSON files** under `src/assets/i18n/en/` and `src/assets/i18n/ar/`.
   - **DO NOT** create or modify `src/assets/i18n/en.json` or `src/assets/i18n/ar.json` — those monolithic files are deprecated and unused.
   - The split file structure is:
     ```
     src/assets/i18n/
     ├── en/
     │   ├── common.json          ← Common shared keys (actions, validation, messages, etc.)
     │   ├── welcome.json
     │   ├── identity.json
     │   └── crm/
     │       ├── navigation.json
     │       ├── dashboard.json
     │       ├── patients.json
     │       ├── tags.json
     │       ├── lookups.json
     │       ├── leads.json
     │       ├── prospects.json
     │       ├── project-leads.json
     │       ├── communication.json
     │       ├── projects.json
     │       ├── campaigns.json
     │       ├── tasks.json
     │       ├── faqs.json
     │       ├── roles.json
     │       └── users.json
     └── ar/
         └── (same structure as en/)
     ```
   - When selecting resource keys:
     1. First, check and use keys from `common.json` if they exist (e.g., common actions, messages, form labels)
     2. If no suitable key exists in `common.json`, use the appropriate feature-specific file under `crm/`
   - Keys within each file are organized by domain sections. Example for a CRM feature file:
     ```json
     {
       "General": { "ManagementDescription": "..." },
       "Titles": { "List": "...", "Add": "...", "Edit": "..." },
       "Filter": {},
       "Table": { "Columns": {}, "EmptyMessage": "...", "PageReport": "..." },
       "Form": {
         "Fields": {
           "Name": {
             "Label": "...",
             "Placeholder": "...",
             "Validations": {
               "Required": "..."
             }
           }
         }
       },
       "Details": { "Fields": {} },
       "Messages": {},
       "Errors": {}
     }
     ```

   - Do NOT use hardcoded strings; always reference resource keys as they appear in the resource files.
   - For validations related to a form field, use the appropriate resource keys (e.g., `CRM.Leads.Form.Fields.Name.Validations.Required`).
   - Use this structure for all form fields:
       ```json
       "Form": {
         "Fields": {
           "Name": {
             "Label": "Field Name",
             "Placeholder": "Enter field name",
             "Validations": {
               "Required": "Field name is required"
             }
           }
         }
       }
       ```

3. **Localization Implementation**
   - In component HTML templates, use the `localize` pipe for translating UI strings (e.g., `{{ 'CRM.Leads.Titles.List' | localize }}`) and must import `LocalizePipe` in component TypeScript files.
   - In component TypeScript files, must extend the `BaseComponent` and make use of the shared base component's `L` method for localization.
   - In any other files (not component TypeScript or component HTML), use the `LocalizationService` directly for translations.
   - If a new key is needed, add it to the appropriate split file in **both** `en/` and `ar/` directories using the same nested structure.
   - Before creating a new key, check if a similar key already exists in `common.json` or the relevant feature file to avoid duplication.
   - Always give priority to keys in `common.json`.

### Shared Components

- `DataTableComponent` - reusable data table
- `ConfirmationDialogComponent` - confirmation modal
- `LoadingSpinnerComponent` - loading indicator
- `NotificationToastComponent` - notification messages

### Layout Architecture

The application has **two distinct layout scopes**, each with its own shell component and routing:

#### 1. Main Layout (Global Scope)
- Used by all standard feature routes (`/dashboard`, `/leads`, `/projects`, etc.).
- Activated via the root route `{ path: '', component: MainLayoutComponent }`.
- Shell: `MainLayoutComponent` → wraps `HeaderComponent` + `NavMenuComponent` (global side nav) + `<router-outlet>`.
- Components inside this scope share the same global navigation context.

#### 2. Project Layout (Project Workspace Scope)
- Used exclusively when a user enters a specific project workspace (`/projects/:id/*`).
- Activated via a **custom URL matcher** (`projectWorkspaceMatcher`) in `app.routes.ts` that matches `/projects/:id` and leaves child segments for `project-workspace.routes.ts`.
- Shell: `ProjectLayoutComponent` → wraps `HeaderComponent` + `ProjectSideNavComponent` (project-specific side nav) + `<router-outlet>`.
- `ProjectWorkspaceService` is scoped to this layout via `providers: [ProjectWorkspaceService]`, isolating workspace state from the rest of the app.
- The back button in `ProjectSideNavComponent` navigates back to `/projects` (global scope).

#### Layout Components Reference

**Shared across both layouts:**
- `HeaderComponent` — top navigation bar

**Main Layout only:**
- `NavMenuComponent` — global side navigation menu
- `FooterComponent` — footer section
- `BreadcrumbComponent` — breadcrumb navigation

**Project Layout only:**
- `ProjectSideNavComponent` — project-scoped side navigation with workspace nav items (Overview, Marketing Profile, Campaigns, Leads, Tasks, Question Bank)

#### Routing Rule
> When creating new feature routes, always place them under `MainLayoutComponent` children **unless** the feature belongs exclusively to a project workspace, in which case add it to `project-workspace.routes.ts`.
