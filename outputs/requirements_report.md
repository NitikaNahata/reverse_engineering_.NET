# Legacy application requirements report

> Generated deterministically from validated extraction artifacts. Inferred findings still require human review.

## Extraction dashboard

| Artifact | Extracted |
|---|---:|
| Business rules | 15 |
| User journeys | 2 |
| Entity mappings | 3 |
| Field mappings | 18 |
| SQL conversions | 3 |
| API contracts | 24 |
| Events | 0 |
| Non-functional requirements | 12 |
| Acceptance criteria | 20 |
| Unresolved questions | 17 |

### Confidence

| Report | Confidence |
|---|---:|
| Architecture | 0.68 |
| Dependencies | 0.7 |
| Business rules | 0.62 |
| Data mapping | 0.72 |
| API and events | 0.72 |
| Non-functional | 0.72 |
| Acceptance criteria | 0.68 |

## 1. System overview

The repository contains two parallel implementations of an 'eShop' Catalog web application: a legacy ASP.NET MVC 5 / Web API 2 application (src/eShopLegacyMVC) targeting classic .NET Framework, and a strangler-fig / ported ASP.NET Core 2.2 application (eShopPorted) targeting net461 via Microsoft.NET.Sdk.Web. Both share a nearly identical layered design: MVC controllers, Web API controllers, an ICatalogService abstraction with a real EF-backed CatalogService and a CatalogServiceMock, and Catalog domain models (CatalogItem, CatalogBrand, CatalogType) persisted through a CatalogDBContext (EF6 in the legacy app, EF Core 2.2.6 in the ported app). A shared eShopLegacy.Utilities library provides binary serialization used by both apps' Files/Brands API controllers. Autofac provides dependency injection in both versions via near-duplicate ApplicationModule classes, and log4net provides logging. The legacy app additionally wires Application Insights telemetry, bundling/optimization, and classic Global.asax/App_Start startup, while the ported app uses Startup.cs/Program.cs (Kestrel/IWebHostBuilder) and EF Core Migrations with a code-first model snapshot. A PowerShell script (Convert-ToPackageReference.ps1) suggests active migration tooling from packages.config to PackageReference format, reinforcing that this is a migration-in-progress repository rather than a single coherent architecture.

### Architectural styles

- Layered monolithic web application (Controller-Service-DataAccess)
- Strangler-fig / parallel migration pattern (legacy ASP.NET MVC & WebAPI alongside ported ASP.NET Core equivalent)
- Repository/Service abstraction via ICatalogService with interchangeable real and mock implementations
- Dependency Injection via Autofac modules
- Code-first ORM data access (Entity Framework 6 / EF Core)

### Major components

| Component | Type | Responsibility |
|---|---|---|
| eShopLegacyMVC Web Application | ASP.NET MVC5/WebAPI2 application | Legacy web front-end and REST API surface for catalog browsing/management, hosted under classic .NET Framework via Global.asax and App_Start configuration. |
| eShopPorted Web Application | ASP.NET Core 2.2 application | Ported/modernized web front-end and REST API surface for catalog browsing/management, hosted via Kestrel/IWebHostBuilder with Startup.cs configuration. |
| eShopLegacy.Utilities | shared class library | Provides cross-cutting binary serialization/deserialization helpers reused by both the legacy and ported Web API file/brand endpoints. |
| Catalog MVC Controllers | presentation/controller component | Handles browser-facing CRUD requests (Index/Create/Edit/Delete/Details) for catalog items, present in duplicate legacy and ported forms. |
| Catalog Web API Controllers | REST API controller component | Exposes brand, file, and catalog data over HTTP APIs (WebApi/BrandsController, WebApi/FilesController, Api/CatalogController, PicController) in both legacy WebAPI2 and ported ASP.NET Core Mvc styles. |
| Catalog Service Layer (legacy) | service/business-logic component | Implements ICatalogService for the legacy app, with a real EF6-backed CatalogService and an in-memory CatalogServiceMock alternative selected presumably by configuration. |
| Catalog Service Layer (ported) | service/business-logic component | Implements ICatalogService for the ported app, with a real EF Core-backed CatalogService and an in-memory CatalogServiceMock; appsettings.json exposes a UseMockData flag suggesting runtime toggling. |
| Catalog Domain Models (legacy) | domain model / entity component | Defines CatalogItem, CatalogBrand, CatalogType entities and the PaginatedItemsViewModel used across legacy controllers, services, and views. |
| Catalog Domain Models (ported) | domain model / entity component | Defines CatalogItem, CatalogBrand, CatalogType entities and Fluent API configuration classes (CatalogBrandConfig/CatalogTypeConfig/CatalogItemConfig) for the ported EF Core context. |
| CatalogDBContext (legacy/EF6) | data access component | Entity Framework 6 DbContext configuring catalog entities via DbModelBuilder, seeded via CatalogDBInitializer, and relying on a custom HiLo ID generator with raw SQL sequence queries. |
| CatalogDBContext (ported/EF Core) | data access component | EF Core 2.2 DbContext applying IEntityTypeConfiguration classes from the assembly and seeding via HasData/PreconfiguredData; supports EF Core Migrations. |
| Autofac DI Modules | dependency injection configuration component | Registers services (ICatalogService implementations) and controllers with Autofac's ContainerBuilder in both legacy (Global.asax RegisterContainer) and ported (Startup.ConfigureServices) hosting models. |
| Preconfigured/Seed Data | seed data component | Supplies hardcoded catalog brand/type/item seed data used by both DB initializers/migrations to populate a fresh database. |
| Migration Tooling Script | build/migration automation script | PowerShell script (Convert-ToPackageReference.ps1) that converts legacy packages.config-based NuGet references to PackageReference format, indicating in-progress project modernization tooling. |

**Confidence:** 0.68

## 2. Dependencies

The repository contains two parallel .NET web applications (legacy ASP.NET MVC5/WebAPI2 on classic .NET Framework 4.7.2 and a 'ported' ASP.NET Core 2.2-style app that still targets net461 via Microsoft.NET.Sdk.Web) plus a shared eShopLegacy.Utilities library. Dependency evidence shows heavy duplication of NuGet packages across both csproj files (Autofac, log4net, Newtonsoft.Json, WebGrease, Antlr) with mismatched or inconsistent versions, a legacy app still using packages.config alongside migrated PackageReference entries, EF6 in the legacy app vs EF Core 2.2.6 in the ported app, and Application Insights/telemetry packages present only in the legacy project. The ported project's continued net461 targeting despite ASP.NET Core package references represents a significant compatibility risk since several ASP.NET Core packages (Microsoft.AspNetCore, Microsoft.AspNetCore.Mvc, EFCore.SqlServer) are designed for netcoreapp/netstandard runtimes and have limited or altered behavior on net461.

| Dependency | Ecosystem | Version | Status | Recommendation |
|---|---|---|---|---|
| EntityFramework | NuGet | 6.2.0 | outdated | Plan migration to EF Core to align with the ported app; EF6 is in maintenance mode with no new feature development. |
| Microsoft.EntityFrameworkCore / .SqlServer / .Design / .Relational | NuGet | 2.2.6 | deprecated | EF Core 2.2 is out of support (support ended Dec 2019); upgrade to a supported EF Core LTS version (e.g., 6.0/8.0) alongside a real .NET (not net461) target framework. |
| Microsoft.AspNetCore / Microsoft.AspNetCore.Mvc / Microsoft.AspNetCore.StaticFiles | NuGet | 2.2.0 | deprecated | ASP.NET Core 2.2 reached end of support in Dec 2019; upgrade to a current LTS release and retarget the project to netcoreapp/net so the packages are used on their intended runtime rather than net461. |
| Autofac / Autofac.Mvc5 / Autofac.Extensions.DependencyInjection | NuGet | 4.9.1 / 4.0.2 / 4.4.0 (ported); 6.1.0/4.0.2 (legacy, version-conflicted) | outdated | Consolidate on a single, current Autofac major version across both projects and resolve the version mismatch between the csproj PackageReference (Autofac 4.9.1) and Web.config bindingRedirect (Autofac 6.1.0) in the legacy app. |
| log4net | NuGet | 2.0.10 | supported | Version is consistent across both apps and reasonably current; keep monitoring for newer 2.x releases addressing security patches. |
| Newtonsoft.Json | NuGet | 12.0.1 (legacy) / 13.0.2 (ported) | supported | Align on a single Newtonsoft.Json version across both projects; verify the ported app actually wires Newtonsoft formatters into MVC since AspNetCore.Mvc 2.2 does not add Newtonsoft support automatically. |
| Microsoft.AspNet.WebApi / .Client / .Core / .WebHost | NuGet | 5.2.7 | deprecated | Web API 2 (System.Web.Http based) has no further feature development; migrate controller logic to ASP.NET Core MVC/Web API equivalents already partially present in eShopPorted. |
| Microsoft.ApplicationInsights.* (Web, DependencyCollector, PerfCounterCollector, WindowsServer, Agent.Intercept, WindowsServer.TelemetryChannel) | NuGet | 2.9.1 (2.4.0 for Agent.Intercept) | outdated | No equivalent telemetry package exists in eShopPorted; either port using Microsoft.ApplicationInsights.AspNetCore or adopt OpenTelemetry to close the observability gap before decommissioning the legacy app. |
| Antlr | NuGet | 3.5.0.2 | outdated | Verify whether Antlr is truly required in the ported net461 ASP.NET Core project; if it's only needed for legacy Web.Optimization bundling, remove it from eShopPorted once bundling is replaced by a modern asset pipeline. |
| WebGrease | NuGet | 1.6.0 | deprecated | Remove WebGrease from eShopPorted since ASP.NET Core does not use System.Web.Optimization; replace bundling in both apps with a modern build tool (webpack, esbuild, or BundlerMinifier). |
| .NET Framework runtime (net461/net472/net47.2) | .NET | net461 (eShopPorted) / v4.7.2 (eShopLegacyMVC, compiled with httpRuntime targetFramework 4.6.1) | deprecated | Retarget eShopPorted to a supported netcoreapp/net (e.g., net8.0) TFM to realize genuine modernization benefits (cross-platform hosting, current EF Core, current ASP.NET Core support); plan a full .NET Framework exit for eShopLegacyMVC as well. |
| packages.config (legacy NuGet management) | NuGet tooling | Not specified | deprecated | Complete migration to PackageReference-only format using the repository's own Convert-ToPackageReference.ps1 script, then remove packages.config and redundant HintPath references. |

### Compatibility issues

#### ASP.NET Core 2.2 / EF Core packages targeting net461 instead of a modern .NET TFM (high)

eShopPorted.csproj uses Microsoft.NET.Sdk.Web and references ASP.NET Core 2.2 and EF Core 2.2.6 packages, but the project's TargetFramework is net461 (classic .NET Framework), not netcoreapp2.2 or a modern net TFM. Several ASP.NET Core/EF Core features and hosting behaviors (e.g., full Kestrel cross-platform support, some middleware) assume a .NET Core runtime; running on net461 can cause missing APIs, different default behaviors, and blocks any future upgrade path to non-Windows hosting.

**Remediation:** Change eShopPorted.csproj TargetFramework to a supported .NET (Core) TFM such as net6.0 or net8.0, and upgrade all ASP.NET Core/EF Core packages to versions compatible with that TFM.

#### Autofac version mismatch between legacy csproj PackageReference and Web.config bindingRedirect (medium)

src/eShopLegacyMVC/packages.config lists Autofac version 4.9.1, but eShopLegacyMVC.csproj declares PackageReference Autofac Version 6.1.0, and Web.config's assemblyBinding bindingRedirect for Autofac targets newVersion 6.1.0.0. This inconsistency across the three sources of truth (packages.config, csproj, Web.config) can cause assembly load failures or silently load an unintended Autofac version at runtime.

**Remediation:** Reconcile the Autofac version declared in packages.config, eShopLegacyMVC.csproj PackageReference, and the Web.config bindingRedirect so all three reference the same resolved version; consider removing packages.config entirely once fully migrated to PackageReference.

#### Newtonsoft.Json version divergence between legacy and ported apps (low)

The legacy app pins Newtonsoft.Json to 12.0.1 (matching its Web.config bindingRedirect to 12.0.0.0), while the ported app references Newtonsoft.Json 13.0.2. Because both projects reference the shared eShopLegacy.Utilities library and exchange serialized DTOs conceptually, divergent JSON library versions across the solution increase risk of subtle serialization behavior differences if JSON-based endpoints are later unified or compared.

**Remediation:** Standardize on a single Newtonsoft.Json version (preferably the latest stable, 13.x) across both eShopLegacyMVC.csproj and eShopPorted.csproj, updating the legacy Web.config bindingRedirect accordingly.

#### Duplicate/legacy-style Reference+HintPath entries coexisting with PackageReference in the same csproj (medium)

eShopLegacyMVC.csproj contains, for multiple packages (EntityFramework, Newtonsoft.Json, Pipelines.Sockets.Unofficial, System.Buffers, System.Diagnostics.DiagnosticSource, System.Diagnostics.PerformanceCounter, System.IO.Compression, System.IO.Compression.ZipFile, System.IO.Pipelines, System.Memory, System.Numerics.Vectors, System.Runtime.CompilerServices.Unsafe, System.Threading.Channels, System.Threading.Tasks.Extensions), both a PackageReference entry and a classic <Reference> with an explicit packages-folder HintPath. This dual declaration pattern is characteristic of an incomplete/partial conversion via the repository's Convert-ToPackageReference.ps1 tool and can cause MSBuild ambiguity or duplicate assembly resolution warnings.

**Remediation:** Re-run/complete the Convert-ToPackageReference.ps1 migration and remove all redundant <Reference>/HintPath entries once packages.config is deleted, leaving only PackageReference entries.

#### WebGrease/Antlr bundling dependencies present in ASP.NET Core project despite incompatible bundling model (low)

eShopPorted.csproj references WebGrease 1.6.0 and Antlr 3.5.0.2, both of which exist to support the classic System.Web.Optimization bundling pipeline used only by the legacy app's App_Start/BundleConfig.cs. ASP.NET Core does not use System.Web.Optimization, so these dependencies are likely dead weight in the ported project, inflating the dependency surface without functional benefit.

**Remediation:** Remove WebGrease and Antlr from eShopPorted.csproj unless a specific ported bundling mechanism depends on them; adopt a modern client-asset bundler if bundling is still required.

#### Application Insights telemetry present only in legacy app, missing modern equivalent in ported app (medium)

The legacy project includes a full Application Insights package set (Microsoft.ApplicationInsights.Web/DependencyCollector/PerfCounterCollector/WindowsServer/Agent.Intercept) and an ApplicationInsights.config file, but eShopPorted.csproj has no telemetry/monitoring package reference at all, creating an observability gap once traffic shifts to the ported app.

**Remediation:** Add Microsoft.ApplicationInsights.AspNetCore (or an OpenTelemetry-based alternative compatible with the eventual target framework) to eShopPorted.csproj and configure equivalent telemetry initializers/modules before decommissioning the legacy app.

## 3. Business rules and user journeys

The eShop Modernizing repository contains a parallel ASP.NET MVC5/WebAPI2 legacy application (src/eShopLegacyMVC) and an ASP.NET Core 2.2 ported application (eShopPorted), both implementing a product catalog CRUD system with shared utility classes. Key business rules extracted include mandatory name/price fields, price range restrictions (0–1,000,000), stock management thresholds, pagination logic, identifier generation via HiLo sequences (legacy only), picture URI construction, and mock/real service selection via configuration flags. Two primary user journeys are identified: catalog browsing with pagination and catalog item CRUD operations. The extraction is constrained by incomplete evidence on some business conditions (e.g., reorder logic triggers, validation error handling specifics) and duplicate/divergent implementations across the two codebases.

### Business rules

#### BR-001: Catalog Item Price Validation

CatalogItem.Price must be a positive decimal with maximum two decimal places and must fall within the range [0, 1,000,000]. A RegularExpression validation attribute enforces the format constraint.

- **Basis:** explicit
- **Category:** validation
- **Conditions:** CatalogItem.Price property is being set or updated, Price value is submitted through Create or Edit form
- **Outcomes:** Price is validated against the regex pattern ^\d+(\.\d{0,2})*$, If validation fails, error message returned: 'The field Price must be a positive number with maximum two decimals.', If validation passes, price is persisted to the database
- **Evidence:**
  - `eShopPorted/Models/CatalogItem.cs`: CatalogItem.Price decorated with [RegularExpression(@"^\d+(\.\d{0,2})*$", ErrorMessage = "The field Price must be a positive number with maximum two decimals.")] and [Range(0, 1000000)]
  - `src/eShopLegacyMVC/Models/CatalogItem.cs`: Identical Price validation constraints present in legacy model

#### BR-002: Stock Availability Range Constraint

CatalogItem.AvailableStock must be a non-negative integer in the range [0, 10,000,000]. A Range attribute enforces this constraint.

- **Basis:** explicit
- **Category:** validation
- **Conditions:** AvailableStock property is set during Create or Edit
- **Outcomes:** If AvailableStock < 0 or > 10,000,000, validation error returned: 'The field Stock must be between 0 and 10 million.', If valid, AvailableStock is persisted
- **Evidence:**
  - `eShopPorted/Models/CatalogItem.cs`: [Range(0, 10000000, ErrorMessage = "The field Stock must be between 0 and 10 million.")] applied to AvailableStock property
  - `src/eShopLegacyMVC/Models/CatalogItem.cs`: Identical constraint in legacy codebase

#### BR-003: Restock Threshold Range Validation

CatalogItem.RestockThreshold must be a non-negative integer between 0 and 10,000,000, enforced by a Range attribute.

- **Basis:** explicit
- **Category:** validation
- **Conditions:** RestockThreshold is being modified
- **Outcomes:** If RestockThreshold outside [0, 10000000], error 'The field Restock must be between 0 and 10 million.' is raised, If valid, RestockThreshold is saved
- **Evidence:**
  - `eShopPorted/Models/CatalogItem.cs`: [Range(0, 10000000, ErrorMessage = "The field Restock must be between 0 and 10 million.")] on RestockThreshold

#### BR-004: Max Stock Threshold Limit

CatalogItem.MaxStockThreshold must be a non-negative integer between 0 and 10,000,000 due to physical/logistical warehouse constraints.

- **Basis:** explicit
- **Category:** constraint
- **Conditions:** MaxStockThreshold property is modified
- **Outcomes:** If outside [0, 10000000], error raised: 'The field Max stock must be between 0 and 10 million.', If valid, constraint is satisfied and value persisted
- **Evidence:**
  - `eShopPorted/Models/CatalogItem.cs`: [Range(0, 10000000, ErrorMessage = "The field Max stock must be between 0 and 10 million.")] on MaxStockThreshold property
  - `src/eShopLegacyMVC/Models/CatalogItem.cs`: Identical constraint in legacy implementation

#### BR-005: Catalog Item Name Required Field

CatalogItem.Name is mandatory and must not be null or empty. Maximum length is 50 characters.

- **Basis:** explicit
- **Category:** validation
- **Conditions:** CatalogItem.Name is null, empty, or exceeds 50 characters
- **Outcomes:** Validation fails and name is required to proceed with Create/Edit, Error message indicates name is required
- **Evidence:**
  - `eShopPorted/Models/CatalogItem.cs`: [Required] and [MaxLength(50)] attributes on Name property
  - `src/eShopLegacyMVC/Models/CatalogItem.cs`: Same constraints in legacy codebase

#### BR-006: Picture File Name Required

CatalogItem.PictureFileName is required and must have a value. Default value is 'dummy.png' if not explicitly set during construction.

- **Basis:** explicit
- **Category:** validation
- **Conditions:** CatalogItem is created or updated without PictureFileName
- **Outcomes:** If no PictureFileName provided, default 'dummy.png' is assigned in constructor, PictureFileName is required for database persistence
- **Evidence:**
  - `eShopPorted/Models/CatalogItem.cs`: Constructor sets PictureFileName = DefaultPictureName ('dummy.png') if not provided; [Required] attribute enforces persistence
  - `src/eShopLegacyMVC/Models/CatalogItem.cs`: Identical behavior in legacy model

#### BR-007: Pagination of Catalog Items

Catalog items are retrieved in paginated batches. Each page is defined by pageSize and pageIndex parameters. Total item count is calculated for pagination UI.

- **Basis:** explicit
- **Category:** business logic
- **Conditions:** User requests Catalog/Index endpoint with pageSize and pageIndex query parameters (defaults: pageSize=10, pageIndex=0)
- **Outcomes:** Service retrieves total count of all CatalogItems, Service skips (pageSize × pageIndex) items and takes pageSize items from database, PaginatedItemsViewModel is populated with ActualPage, ItemsPerPage, TotalItems, TotalPages, and Data (item collection), View renders pagination controls based on TotalPages and ActualPage
- **Evidence:**
  - `eShopPorted/Controllers/CatalogController.cs`: Index(int pageSize = 10, int pageIndex = 0) calls service.GetCatalogItemsPaginated(pageSize, pageIndex)
  - `eShopPorted/Services/CatalogService.cs`: GetCatalogItemsPaginated calculates totalItems, skips and takes based on pageSize/pageIndex, returns PaginatedItemsViewModel with TotalPages = (int)Math.Ceiling(((decimal)count / pageSize))
  - `eShopPorted/ViewModel/PaginatedItemsViewModel.cs`: TotalPages computed as (int)Math.Ceiling(((decimal)count / pageSize)) in constructor

#### BR-008: Picture URI Construction

Picture URI for a catalog item is dynamically constructed as '/Pics/{itemId}.png' in the ported app. In the legacy app, it uses a route helper to construct an absolute URL via the PicController route.

- **Basis:** explicit
- **Category:** business logic
- **Conditions:** CatalogItem is retrieved and displayed in a view
- **Outcomes:** Ported app: PictureUri is set to '/Pics/{item.Id}.png', Legacy app: PictureUri is set via Url.RouteUrl(PicController.GetPicRouteName, ...) producing an absolute URL to the PicController.Index route with catalogItemId parameter
- **Evidence:**
  - `eShopPorted/Controllers/CatalogController.cs`: AddUriPlaceHolder method sets item.PictureUri = $"/Pics/{item.Id}.png"
  - `src/eShopLegacyMVC/Controllers/CatalogController.cs`: AddUriPlaceHolder method sets item.PictureUri = this.Url.RouteUrl(PicController.GetPicRouteName, new { catalogItemId = item.Id }, this.Request.Url.Scheme)

#### BR-009: Service Implementation Selection (Mock vs Real)

The application can switch between a real database-backed CatalogService and a mock in-memory CatalogServiceMock based on configuration. The eShopPorted appsettings.json exposes a 'UseMockData' flag; logic for conditional registration is inferred but not fully evidenced.

- **Basis:** inferred
- **Category:** configuration
- **Conditions:** Application starts, DI container is configured (Autofac)
- **Outcomes:** If UseMockData = true, CatalogServiceMock is registered as ICatalogService implementation, If UseMockData = false, real CatalogService is registered, All controller dependencies receive the selected implementation
- **Evidence:**
  - `eShopPorted/appsettings.json`: Contains "UseMockData": "true" flag
  - `eShopPorted/Services/CatalogServiceMock.cs`: Provides hardcoded in-memory implementation of ICatalogService using PreconfiguredData
  - `eShopPorted/Services/CatalogService.cs`: Real implementation backed by CatalogDBContext

#### BR-010: Legacy HiLo Sequence-Based ID Generation

In the legacy application, CatalogItem IDs are generated using a custom HiLo (High-Low) sequence pattern. When creating a new CatalogItem, CatalogItemHiLoGenerator.GetNextSequenceValue is called to fetch the next ID from the 'catalog_hilo' SQL sequence.

- **Basis:** explicit
- **Category:** business logic
- **Conditions:** CreateCatalogItem is called in legacy CatalogService, ID has not been manually set
- **Outcomes:** HiLoGenerator.GetNextSequenceValue executes: 'SELECT NEXT VALUE FOR catalog_hilo;', Database SQL sequence returns the next ID, ID is assigned to the new CatalogItem before insertion, Item is persisted with the generated ID
- **Evidence:**
  - `src/eShopLegacyMVC/Services/CatalogService.cs`: CreateCatalogItem calls catalogItem.Id = indexGenerator.GetNextSequenceValue(db)
  - `src/eShopLegacyMVC/Models/CatalogItemHiLoGenerator.cs`: GetNextSequenceValue executes db.Database.SqlQuery<Int64>("SELECT NEXT VALUE FOR catalog_hilo;")

#### BR-011: Catalog Item CRUD Operations

The catalog system supports Create, Read, Update, Delete (CRUD) operations on CatalogItem entities. Each operation is exposed through both MVC controller actions and (in legacy) Web API endpoints.

- **Basis:** explicit
- **Category:** business logic
- **Conditions:** User navigates to or submits catalog forms (Create, Edit, Delete), User calls REST API endpoints
- **Outcomes:** Create: New CatalogItem is instantiated, validated, persisted via service.CreateCatalogItem(), Read: CatalogItem is retrieved via service.FindCatalogItem(id) or service.GetCatalogItemsPaginated(), Update: Modified CatalogItem is saved via service.UpdateCatalogItem() with EntityState.Modified, Delete: CatalogItem is removed via service.RemoveCatalogItem()
- **Evidence:**
  - `eShopPorted/Controllers/CatalogController.cs`: Index, Details, Create (GET/POST), Edit (GET/POST), Delete (GET/POST), DeleteConfirmed all map to corresponding service methods
  - `eShopPorted/Services/ICatalogService.cs`: Interface defines FindCatalogItem, GetCatalogItemsPaginated, CreateCatalogItem, UpdateCatalogItem, RemoveCatalogItem

#### BR-012: Image MIME Type Resolution

When serving catalog item picture files, the system determines the MIME type based on the file extension (.png, .gif, .jpg, .jpeg, .bmp, .tiff, .wmf, .jp2, .svg). If extension is unrecognized, default 'application/octet-stream' is used.

- **Basis:** explicit
- **Category:** business logic
- **Conditions:** PicController.Index is called with a catalogItemId, Item has a PictureFileName with an extension
- **Outcomes:** File extension is extracted from PictureFileName, GetImageMimeTypeFromImageFileExtension maps extension to MIME type, File is read from disk and returned with correct Content-Type header
- **Evidence:**
  - `eShopPorted/Controllers/PicController.cs`: GetImageMimeTypeFromImageFileExtension switches on imageFileExtension to map .png→image/png, .jpg→image/jpeg, etc.; defaults to application/octet-stream
  - `src/eShopLegacyMVC/Controllers/PicController.cs`: Identical MIME type resolution logic in legacy implementation

#### BR-013: Catalog Brand and Type Reference Data

The system maintains a fixed set of catalog brands (Azure, .NET, Visual Studio, SQL Server, Other) and catalog types (Mug, T-Shirt, Sheet, USB Memory Stick) as reference data. These are seeded into the database at initialization.

- **Basis:** explicit
- **Category:** data
- **Conditions:** Database is initialized or migrated
- **Outcomes:** 5 CatalogBrand records are inserted with IDs 1–5, 4 CatalogType records are inserted with IDs 1–4, Reference data is available for dropdown/selection in Create/Edit forms
- **Evidence:**
  - `eShopPorted/Models/Infrastructure/PreconfiguredData.cs`: GetPreconfiguredCatalogBrands returns 5 hardcoded brands; GetPreconfiguredCatalogTypes returns 4 hardcoded types
  - `eShopPorted/Models/Config/CatalogBrandConfig.cs`: HasData() seeding in Fluent API applies PreconfiguredData.GetPreconfiguredCatalogBrands()
  - `src/eShopLegacyMVC/Models/Infrastructure/PreconfiguredData.cs`: Identical seed data in legacy codebase

#### BR-014: Anti-Forgery Token Validation on Mutation Endpoints

All HTTP POST endpoints that mutate state (Create, Edit, DeleteConfirmed) require an anti-forgery token validated by the [ValidateAntiForgeryToken] attribute to prevent CSRF attacks.

- **Basis:** explicit
- **Category:** security
- **Conditions:** User submits a form via POST to Create, Edit, or DeleteConfirmed endpoint, Request lacks or has invalid anti-forgery token
- **Outcomes:** If token is missing or invalid, request is rejected with HTTP 400 Bad Request, If token is valid, form processing continues
- **Evidence:**
  - `eShopPorted/Controllers/CatalogController.cs`: [ValidateAntiForgeryToken] decorates Create(POST), Edit(POST), and DeleteConfirmed(POST) methods
  - `src/eShopLegacyMVC/Controllers/CatalogController.cs`: Same CSRF protection in legacy controller

#### BR-015: REST API Brand Data Serialization

Web API endpoints serving brand data serialize CatalogBrand objects using binary serialization (via eShopLegacy.Utilities.Serializing) for file download responses.

- **Basis:** explicit
- **Category:** integration
- **Conditions:** FilesController.Index or WebApi/FilesController.Get is called
- **Outcomes:** Service retrieves CatalogBrand list, Brands are mapped to BrandDTO objects (Id, Brand properties), DTOs are serialized to binary stream via Serializing.SerializeBinary(), Response is returned as a StreamContent with the serialized bytes
- **Evidence:**
  - `eShopPorted/Controllers/Api/FilesController.cs`: Index() maps brands to BrandDTO list, calls Serializing().SerializeBinary(brands), returns Ok(data)
  - `src/eShopLegacyMVC/Controllers/WebApi/FilesController.cs`: Get() similarly serializes brands using Serializing.SerializeBinary() and wraps in HttpResponseMessage with StreamContent

### User journeys

#### UJ-001: Browse Catalog with Pagination

- **Actor:** Customer/End User
- **Trigger:** User navigates to /Catalog/Index or clicks 'Next'/'Previous' pagination link
- **Preconditions:** Application is running and database is initialized with seed data, User is viewing a web browser

1. **User:** User opens /Catalog/Index in browser (or clicks pagination link with pageSize=10, pageIndex=0)
   **System:** CatalogController.Index(10, 0) is invoked
2. **User:** System processes the request
   **System:** Service.GetCatalogItemsPaginated(10, 0) is called, fetches total item count and first 10 items from database
3. **User:** System constructs the response
   **System:** PaginatedItemsViewModel is populated: ActualPage=0, ItemsPerPage=10, TotalItems=N, TotalPages=ceil(N/10), Data=[items 1-10]
4. **User:** System enriches item URIs
   **System:** For each item, PictureUri is set to /Pics/{item.Id}.png
5. **User:** System returns view with pagination controls
   **System:** View renders CatalogTable partial with 10 items and pagination UI showing Previous (disabled), page info, Next (enabled if more pages)

**Alternate paths:** If user navigates to /Catalog/Index?pageSize=5&pageIndex=2, the same flow repeats with pageSize=5, pageIndex=2

**Outcome:** User sees a paginated list of 10 (or custom pageSize) catalog items with clickable pagination controls to browse through pages

#### UJ-002: Create New Catalog Item

- **Actor:** Admin/Catalog Manager
- **Trigger:** Admin clicks 'Create New' button on /Catalog/Index
- **Preconditions:** Admin has access to the application, Database is initialized with brand and type seed data

1. **User:** Admin clicks 'Create New' button
   **System:** CatalogController.Create() (GET) is invoked, populates ViewBag.CatalogBrandId and ViewBag.CatalogTypeId dropdowns from service.GetCatalogBrands/Types()
2. **User:** Browser renders /Catalog/Create form with empty fields and anti-forgery token
   **System:** User sees form with Name, Description, Brand dropdown, Type dropdown, Price, Picture, Stock, Restock, Max Stock fields
3. **User:** Admin fills form: Name='Test Product', Price=19.99, Stock=50, Brand=2 (.NET), Type=2 (T-Shirt), submits POST
   **System:** CatalogController.Create(CatalogItem model) validates ModelState
4. **User:** System validates all fields (Name required, Price format/range, Stock range, etc.)
   **System:** If any validation fails, form is re-rendered with error messages. If all valid, service.CreateCatalogItem(catalogItem) is called.
5. **User:** Service persists new item (legacy: generates ID via HiLo, ported: EF Core auto-identity)
   **System:** Item inserted into database with generated ID

**Alternate paths:** If validation fails, form is re-rendered with errors and user must correct and resubmit

**Outcome:** New catalog item is created and persisted; user is redirected to /Catalog/Index to see the updated list

## 4. Legacy data mapping and SQL conversions

The eShopModernizing repository contains a legacy ASP.NET MVC5/WebAPI2 application (src/eShopLegacyMVC) and a ported ASP.NET Core 2.2 application (eShopPorted), both managing a product catalog persisted via Entity Framework. Three primary entities (CatalogItem, CatalogBrand, CatalogType) map directly between the two codebases with identical schemas, though ID generation differs: legacy uses HiLo sequences, ported uses EF Core identity. Both preserve pagination logic, validation constraints (price range 0–1,000,000, stock limits 0–10,000,000), nullable fields, and foreign key relationships. Key structural differences include EF6/DbModelBuilder (legacy) vs. EF Core/Fluent Config (ported), and raw SQL sequence queries (legacy) vs. native EF Core generated IDs (ported). Seed data is duplicated across CatalogDBInitializer/PreconfiguredData (legacy) and Fluent HasData configurations (ported). No explicit SQL stored procedures, triggers, or views are evidenced; all data access flows through ORM layers.

### CatalogItem (legacy, EF6) → CatalogItem (ported, EF Core 2.2)

**Mapping:** direct

| Source field | Target field | Source type | Target type | Transformation |
|---|---|---|---|---|
| Id | Id | int | int | Direct; legacy uses HiLo-generated IDs via CatalogItemHiLoGenerator.GetNextSequenceValue(), ported uses EF Core auto-generated identity via SqlServer:ValueGenerationStrategy=IdentityColumn |
| Name | Name | string | string | Direct; Required, MaxLength(50) |
| Description | Description | string\|null | string\|null | Direct; nullable string |
| Price | Price | decimal | decimal | Direct; validates RegularExpression(^\d+(\.\d{0,2})*$) and Range(0, 1000000) |
| PictureFileName | PictureFileName | string | string | Direct; Required, defaults to 'dummy.png' in constructor |
| PictureUri | PictureUri | string\|null | string\|null | Ignored in DB; computed in controller via AddUriPlaceHolder() method. Legacy uses Url.RouteUrl() for absolute URL, ported uses simple string interpolation /Pics/{item.Id}.png |
| CatalogTypeId | CatalogTypeId | int | int | Direct FK; references CatalogType.Id |
| CatalogType | CatalogType | CatalogType | CatalogType | Direct navigation property |
| CatalogBrandId | CatalogBrandId | int | int | Direct FK; references CatalogBrand.Id |
| CatalogBrand | CatalogBrand | CatalogBrand | CatalogBrand | Direct navigation property |
| AvailableStock | AvailableStock | int | int | Direct; Range(0, 10000000) validates stock quantity |
| RestockThreshold | RestockThreshold | int | int | Direct; Range(0, 10000000) for reorder trigger level |
| MaxStockThreshold | MaxStockThreshold | int | int | Direct; Range(0, 10000000) for warehouse capacity |
| OnReorder | OnReorder | bool | bool | Direct boolean flag; defaults to false |

### CatalogBrand (legacy, EF6) → CatalogBrand (ported, EF Core 2.2)

**Mapping:** direct

| Source field | Target field | Source type | Target type | Transformation |
|---|---|---|---|---|
| Id | Id | int | int | Direct; legacy uses HiLo sequence catalog_brand_hilo, ported uses EF Core auto-identity |
| Brand | Brand | string | string | Direct; Required, MaxLength(100) |

### CatalogType (legacy, EF6) → CatalogType (ported, EF Core 2.2)

**Mapping:** direct

| Source field | Target field | Source type | Target type | Transformation |
|---|---|---|---|---|
| Id | Id | int | int | Direct; legacy uses HiLo sequence catalog_type_hilo, ported uses EF Core auto-identity |
| Type | Type | string | string | Direct; Required, MaxLength(100) |

### SQL-001: Migrate Legacy HiLo ID Generation to EF Core IDENTITY

Legacy application uses custom HiLo (High-Low) sequences for CatalogItem, CatalogBrand, and CatalogType ID generation via raw SQL queries (SELECT NEXT VALUE FOR catalog_hilo). EF Core 2.2 uses IDENTITY columns. This conversion removes the HiLo pattern and relies on EF Core's native identity generation.

> Review only—this SQL has not been executed.

```sql
-- No user-facing SQL required; EF Core Migrations handle IDENTITY column creation.
-- However, if migrating existing data, verify existing IDs do not conflict with IDENTITY seed:
DBCC CHECKIDENT ('Catalog', RESEED, 12);
DBCC CHECKIDENT ('CatalogBrand', RESEED, 5);
DBCC CHECKIDENT ('CatalogType', RESEED, 4);
```

**Validation SQL**

```sql
-- Verify IDENTITY columns are configured and auto-increment
SELECT COLUMNPROPERTY(OBJECT_ID('Catalog'), 'Id', 'IsIdentity') AS IsIdentity_Catalog,
       IDENT_CURRENT('Catalog') AS CurrentSeed_Catalog,
       COLUMNPROPERTY(OBJECT_ID('CatalogBrand'), 'Id', 'IsIdentity') AS IsIdentity_Brand,
       IDENT_CURRENT('CatalogBrand') AS CurrentSeed_Brand,
       COLUMNPROPERTY(OBJECT_ID('CatalogType'), 'Id', 'IsIdentity') AS IsIdentity_Type,
       IDENT_CURRENT('CatalogType') AS CurrentSeed_Type;
```

**Rollback SQL**

```sql
-- Restore HiLo sequences if reverting to legacy app:
DROP SEQUENCE IF EXISTS [dbo].[catalog_hilo];
DROP SEQUENCE IF EXISTS [dbo].[catalog_brand_hilo];
DROP SEQUENCE IF EXISTS [dbo].[catalog_type_hilo];
CREATE SEQUENCE [dbo].[catalog_hilo] AS [bigint] START WITH 1 INCREMENT BY 10;
CREATE SEQUENCE [dbo].[catalog_brand_hilo] AS [bigint] START WITH 1 INCREMENT BY 10;
CREATE SEQUENCE [dbo].[catalog_type_hilo] AS [bigint] START WITH 1 INCREMENT BY 10;
```

### SQL-002: Seed Reference Data (Brands and Types) via EF Core HasData

Legacy application seeds CatalogBrand and CatalogType via CatalogDBInitializer.Seed() which either loads from CSV files (if UseCustomizationData=true) or calls PreconfiguredData.GetPreconfiguredCatalogBrands/Types(). Ported app uses EF Core Fluent API HasData() in entity configurations. This conversion consolidates seeding into Fluent configuration and removes the need for imperative initializers.

> Review only—this SQL has not been executed.

```sql
-- No direct SQL; EF Core Migrations generate INSERT statements from HasData() configuration.
-- Equivalent INSERT statements (generated by EF Core migration):
INSERT INTO [CatalogBrand] ([Id], [Brand]) VALUES (1, N'Azure'), (2, N'.NET'), (3, N'Visual Studio'), (4, N'SQL Server'), (5, N'Other');
INSERT INTO [CatalogType] ([Id], [Type]) VALUES (1, N'Mug'), (2, N'T-Shirt'), (3, N'Sheet'), (4, N'USB Memory Stick');
```

**Validation SQL**

```sql
SELECT COUNT(*) AS BrandCount FROM CatalogBrand;
SELECT COUNT(*) AS TypeCount FROM CatalogType;
SELECT * FROM CatalogBrand ORDER BY Id;
SELECT * FROM CatalogType ORDER BY Id;
```

**Rollback SQL**

```sql
DELETE FROM CatalogBrand WHERE Id IN (1, 2, 3, 4, 5);
DELETE FROM CatalogType WHERE Id IN (1, 2, 3, 4);
```

### SQL-003: Seed CatalogItems via EF Core HasData with Updated ForeignKey References

Legacy application seeds CatalogItem instances in CatalogDBInitializer.AddCatalogItems(), assigning IDs via HiLo generator and linking to CatalogBrand/CatalogType via FK. Ported app uses CatalogItemConfig.HasData(PreconfiguredData.GetPreconfiguredCatalogItems()) with pre-assigned integer IDs (1–12) and matching FK references. This conversion ensures seeded items reference correct brand/type IDs and use IDENTITY for ID generation.

> Review only—this SQL has not been executed.

```sql
-- EF Core Migration generates INSERT statements for 12 CatalogItems; example for first few:
INSERT INTO [Catalog] ([Id], [AvailableStock], [CatalogBrandId], [CatalogTypeId], [Description], [MaxStockThreshold], [Name], [OnReorder], [PictureFileName], [Price], [RestockThreshold])
VALUES (1, 100, 2, 2, N'.NET Bot Black Hoodie', 0, N'.NET Bot Black Hoodie', 0, N'1.png', 19.5, 0),
       (2, 100, 2, 1, N'.NET Black & White Mug', 0, N'.NET Black & White Mug', 0, N'2.png', 8.50, 0),
       -- ... 10 more rows (IDs 3–12)
       (12, 100, 5, 2, N'Prism White TShirt', 0, N'Prism White TShirt', 0, N'12.png', 12, 0);
```

**Validation SQL**

```sql
SELECT COUNT(*) AS ItemCount FROM Catalog;
SELECT Id, Name, CatalogBrandId, CatalogTypeId, Price FROM Catalog ORDER BY Id;
-- Verify FK references are valid:
SELECT c.Id, c.Name, cb.Brand, ct.Type FROM Catalog c
JOIN CatalogBrand cb ON c.CatalogBrandId = cb.Id
JOIN CatalogType ct ON c.CatalogTypeId = ct.Id
ORDER BY c.Id;
```

**Rollback SQL**

```sql
DELETE FROM Catalog WHERE Id BETWEEN 1 AND 12;
```

## 5. API contracts and events

The repository contains two parallel implementations of an eShop Catalog web application: a legacy ASP.NET MVC5/WebAPI2 application on .NET Framework (src/eShopLegacyMVC) and a partially ported ASP.NET Core 2.2 application targeting net461 (eShopPorted). The legacy app exposes multiple HTTP API endpoints for catalog management (Brands, Files, Catalog items) via Web API 2, while the ported app provides equivalent routes via ASP.NET Core MVC/API controllers. Both share identical domain models (CatalogItem, CatalogBrand, CatalogType) and services (ICatalogService interface with real and mock implementations), but diverge in data access layers (EF6 vs EF Core 2.2). No asynchronous event contracts (pub/sub, messaging) are detected in the codebase; the application is synchronous request-response only.

| ID | Application | Method | Route | Compatibility |
|---|---|---|---|---|
| API-001 | eShopLegacyMVC | GET | `api/brands` | equivalent |
| API-002 | eShopPorted | GET | `api/brands` | equivalent |
| API-003 | eShopLegacyMVC | DELETE | `api/brands/{id}` | equivalent |
| API-004 | eShopPorted | DELETE | `api/brands/{id}` | equivalent |
| API-005 | eShopLegacyMVC | GET | `api/files` | equivalent |
| API-006 | eShopPorted | GET | `api/files` | equivalent |
| API-007 | eShopLegacyMVC | GET | `Catalog` | equivalent |
| API-008 | eShopPorted | GET | `Catalog` | equivalent |
| API-009 | eShopLegacyMVC | GET | `Catalog/Details/{id}` | equivalent |
| API-010 | eShopPorted | GET | `Catalog/Details/{id}` | equivalent |
| API-011 | eShopLegacyMVC | GET | `Catalog/Create` | equivalent |
| API-012 | eShopPorted | GET | `Catalog/Create` | equivalent |
| API-013 | eShopLegacyMVC | POST | `Catalog/Create` | equivalent |
| API-014 | eShopPorted | POST | `Catalog/Create` | equivalent |
| API-015 | eShopLegacyMVC | GET | `Catalog/Edit/{id}` | equivalent |
| API-016 | eShopPorted | GET | `Catalog/Edit/{id}` | equivalent |
| API-017 | eShopLegacyMVC | POST | `Catalog/Edit/{id}` | equivalent |
| API-018 | eShopPorted | POST | `Catalog/Edit/{id}` | equivalent |
| API-019 | eShopLegacyMVC | GET | `Catalog/Delete/{id}` | equivalent |
| API-020 | eShopPorted | GET | `Catalog/Delete/{id}` | equivalent |
| API-021 | eShopLegacyMVC | POST | `Catalog/Delete/{id}` | equivalent |
| API-022 | eShopPorted | POST | `Catalog/Delete/{id}` | equivalent |
| API-023 | eShopLegacyMVC | GET | `items/{catalogItemId}/pic` | equivalent |
| API-024 | eShopPorted | GET | `items/{catalogItemId}/pic` | equivalent |

### Events

No repository evidence of published or consumed events was found.

## 6. Non-functional requirements

This repository contains a strangler-fig migration from legacy ASP.NET MVC5/WebAPI2 (.NET Framework 4.7.2) to ASP.NET Core 2.2 (targeting net461), both implementing a catalog e-commerce application. The architecture uses layered design with controllers, services, and EF-based data access. The codebase exhibits significant technical debt: the ported application still targets net461 despite using ASP.NET Core packages, BinaryFormatter-based serialization is used for API payloads (a security risk), EF Core 2.2 is outdated, dependency versions diverge between projects, and critical telemetry/monitoring was not ported from legacy to new application. The migration is incomplete, indicated by mixed package management (packages.config + PackageReference) and duplicated logic across both implementations.

| ID | Category | Requirement | Basis | Priority | Verification |
|---|---|---|---|---|---|
| NFR-001 | security | Eliminate use of BinaryFormatter for serialization of API payloads in eShopLegacy.Utilities and Web API endpoints, replacing with secure serialization (e.g., System.Text.Json or Newtonsoft.Json over HTTP). | observed | high | Code review confirming removal of BinaryFormatter from Serializing.cs and all Web API controllers; automated security scanning for deprecated serialization patterns. |
| NFR-002 | security | Resolve Autofac version mismatch between packages.config (4.9.1), eShopLegacyMVC.csproj PackageReference (6.1.0), and Web.config bindingRedirect (6.1.0.0) to ensure consistent assembly resolution. | observed | high | Verify all Autofac references across packages.config, csproj, and Web.config declare the same version; test DI container initialization in both legacy and ported applications. |
| NFR-003 | maintainability | Complete migration from packages.config to PackageReference format in eShopLegacyMVC, removing all duplicate Reference/HintPath entries that coexist with PackageReference declarations. | observed | high | Verify eShopLegacyMVC.csproj contains only PackageReference entries (no duplicate Reference/HintPath); packages.config is deleted; build completes without ambiguous assembly resolution warnings. |
| NFR-004 | deployment | Retarget eShopPorted.csproj from net461 to a supported .NET (Core) target framework (e.g., net6.0 or net8.0) to enable genuine ASP.NET Core modernization and cross-platform deployment. | observed | high | TargetFramework element in eShopPorted.csproj updated to net6.0 or later; ASP.NET Core and EF Core packages upgraded to versions compatible with new TFM; application builds and runs on non-Windows platforms. |
| NFR-005 | performance | Upgrade Microsoft.EntityFrameworkCore from 2.2.6 to a current LTS version (6.0 or 8.0) in eShopPorted to benefit from performance improvements and query optimization enhancements. | observed | high | EF Core package version updated; run database query performance benchmarks; verify no query behavior regression; validate ORM-specific features work correctly. |
| NFR-006 | observability | Port Microsoft Application Insights telemetry configuration from eShopLegacyMVC to eShopPorted (or replace with equivalent observability framework) to maintain operational visibility across both applications during strangler-fig cutover. | observed | high | eShopPorted.csproj includes Microsoft.ApplicationInsights.AspNetCore (or OpenTelemetry equivalent); ApplicationInsights configuration present in Startup.cs; telemetry events logged for key application flows; data flows to Application Insights workspace. |
| NFR-007 | data_integrity | Standardize Newtonsoft.Json dependency version across eShopLegacyMVC (12.0.1) and eShopPorted (13.0.2) to 13.0.2 to ensure consistent JSON serialization behavior for shared data contracts and API payloads. | observed | medium | Both eShopLegacyMVC.csproj and eShopPorted.csproj reference Newtonsoft.Json 13.0.2; Web.config bindingRedirect updated to 13.0.0.0; integration tests verify JSON payloads serialize/deserialize identically across both projects. |
| NFR-008 | maintainability | Remove WebGrease (1.6.0) and Antlr (3.5.0.2) dependencies from eShopPorted.csproj, as System.Web.Optimization bundling is not used in ASP.NET Core projects. | observed | medium | eShopPorted.csproj has no WebGrease or Antlr PackageReference entries; verify application still builds and runs; client asset bundling is handled by alternative pipeline if needed. |
| NFR-009 | maintainability | Consolidate duplicated catalog service implementations, models, and DI modules from src/eShopLegacyMVC and eShopPorted into a single codebase or establish a clear feature-branch cutover date to minimize maintenance burden and reduce divergence risk. | inferred | high | Strangler-fig migration plan documented with cutover date; feature flags in place to route traffic; automated tests verify behavioral equivalence across both implementations; legacy app deprecated after cutover date. |
| NFR-010 | security | Update all NuGet packages in eShopLegacyMVC and eShopPorted to versions that have active security patching; replace end-of-support frameworks (ASP.NET MVC 5.2.7, Web API 5.2.7, EF 6.2.0, ASP.NET Core 2.2.0) with modern equivalents. | observed | high | Dependency audit tool reports zero high/critical vulnerabilities; all packages have release dates within past 18 months; security scanning passes; application successfully upgrades to LTS versions of .NET, ASP.NET Core, EF Core, and supporting libraries. |
| NFR-011 | observability | Establish logging consistency across legacy (log4net) and ported (log4net) applications by verifying both use identical log4net version (2.0.10) and configuration patterns; ensure cutover does not introduce observability blind spots. | observed | medium | Both projects reference log4net 2.0.10; log4net configuration files present in both; structured logging is captured consistently; log files/streams unified during cutover. |
| NFR-012 | data_integrity | Migrate from raw SQL HiLo sequence queries (CatalogItemHiLoGenerator) in legacy EF6 to EF Core native value generation strategy (ValueGeneratedOnAdd with SqlServer IDENTITY) in ported application to ensure portability and simplify ID generation logic. | observed | medium | Raw SQL queries removed from CatalogItemHiLoGenerator; EF Core migration files reflect HasValueGenerator for CatalogItem.Id using IDENTITY or HiLo without raw SQL; functional tests verify ID sequences are monotonically increasing and consistent. |

## 7. Acceptance criteria

This eShop Modernizing repository demonstrates a strangler-fig migration from legacy ASP.NET MVC5/WebAPI2 (.NET Framework 4.7.2) to ASP.NET Core 2.2 (targeting net461). Both implementations provide identical catalog CRUD functionality with models, services, controllers, and data access layers. Extracted acceptance criteria cover primary journeys (catalog browsing with pagination, item CRUD), validation constraints (price range 0–1,000,000, stock limits 0–10,000,000), pagination logic, anti-forgery protection, MIME type resolution, and reference data seeding. The extraction is constrained by incomplete evidence on conditional service selection (UseMockData flag wiring) and some validation error handling flows. All criteria are grounded in repository evidence; inferences are minimal and recorded as unresolved questions.

### AC-001: Catalog Item Pagination with Default Page Size

- **Given** A user opens the catalog index page without specifying page parameters
- **When** CatalogController.Index() is invoked with default query parameters (pageSize=10, pageIndex=0)
- **Then** The service retrieves total item count, skips 0 items, takes 10 items from database, calculates TotalPages = ceil(count/10), populates PaginatedItemsViewModel with ActualPage=0, ItemsPerPage=10, Data containing first 10 items, and renders View with pagination controls showing Next enabled if TotalPages > 1
- **Priority:** high
- **Verification:** Integration test: navigate to /Catalog/Index, verify HTTP 200 response, assert ViewModel.ActualPage == 0, ViewModel.ItemsPerPage == 10, ViewModel.Data.Count <= 10, pagination UI rendered correctly
- **Related rules:** BR-007
- **Related journeys:** UJ-001
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-002: Catalog Item Pagination with Custom Page Size

- **Given** A user requests a catalog page with custom pageSize and pageIndex parameters
- **When** CatalogController.Index(pageSize=5, pageIndex=2) is invoked
- **Then** Service calculates skip = 5 * 2 = 10, takes 5 items starting at offset 10, TotalPages = ceil(count/5), ViewModel.ActualPage = 2, ViewModel.ItemsPerPage = 5, View renders page 2 with 5 items and pagination controls showing Previous and Next as appropriate
- **Priority:** high
- **Verification:** Integration test: navigate to /Catalog/Index?pageSize=5&pageIndex=2, assert ViewModel.ActualPage == 2, ViewModel.ItemsPerPage == 5, ViewModel.Data.Count <= 5, verify second page items differ from first page
- **Related rules:** BR-007
- **Related journeys:** UJ-001
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-003: Price Validation: Regex Pattern and Range Constraint

- **Given** An admin creates a new catalog item with a price value
- **When** CatalogItem.Create form is submitted with Price = '19.99'
- **Then** Model validation applies [RegularExpression(@"^\d+(\.\d{0,2})*$")] and [Range(0, 1000000)] attributes, regex pattern validates format (positive decimal with max 2 decimals), Range validates 0 <= Price <= 1000000, ModelState.IsValid returns true, item is persisted
- **Priority:** high
- **Verification:** Unit test: instantiate CatalogItem with Price=19.99, call validator, assert no errors. Test with Price=19.999 (too many decimals), assert regex validation error. Test with Price=-5, assert Range validation error. Test with Price=1000001, assert Range validation error.
- **Related rules:** BR-001
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-004: Stock Availability Range Validation

- **Given** An admin edits a catalog item and modifies the AvailableStock field
- **When** CatalogItem.Edit form is submitted with AvailableStock = '5000000'
- **Then** Model validation applies [Range(0, 10000000, ErrorMessage = "The field Stock must be between 0 and 10 million.")] attribute, Range validator confirms 0 <= AvailableStock <= 10000000, ModelState.IsValid returns true, item persists with updated stock
- **Priority:** high
- **Verification:** Unit test: instantiate CatalogItem with AvailableStock=5000000, assert validator passes. Test AvailableStock=-1, assert Range error. Test AvailableStock=10000001, assert Range error.
- **Related rules:** BR-002
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-005: Restock Threshold Validation

- **Given** An admin sets the RestockThreshold for a catalog item
- **When** CatalogItem form is submitted with RestockThreshold = '7500000'
- **Then** Model validation applies [Range(0, 10000000)] attribute, validator confirms threshold within bounds, ModelState.IsValid returns true, RestockThreshold is persisted
- **Priority:** medium
- **Verification:** Unit test: test RestockThreshold at boundary (0, 10000000, outside range); verify only valid values persist
- **Related rules:** BR-003
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-006: Max Stock Threshold Validation

- **Given** An admin configures the MaxStockThreshold for warehouse capacity
- **When** CatalogItem form is submitted with MaxStockThreshold = '9000000'
- **Then** Model validation applies [Range(0, 10000000, ErrorMessage = "The field Max stock must be between 0 and 10 million.")] attribute, validator confirms within warehouse constraint, ModelState.IsValid returns true, MaxStockThreshold is persisted
- **Priority:** medium
- **Verification:** Unit test: test boundary values (0, 10000000, out-of-range); verify persistence only for valid thresholds
- **Related rules:** BR-004
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-007: Catalog Item Name Required and Length Validation

- **Given** An admin creates a new catalog item without a name or with excessive length
- **When** CatalogItem.Create form is submitted with Name=null or Name.Length > 50
- **Then** Model validation applies [Required] and [MaxLength(50)] attributes, validator reports Name is required if null/empty, or exceeds max length error if > 50 chars, ModelState.IsValid returns false, form is re-rendered with validation error message, item is not persisted
- **Priority:** high
- **Verification:** Unit test: submit form with Name=null, assert Required error. Submit with Name='a'*51, assert MaxLength error. Submit with valid Name, assert no error and persistence.
- **Related rules:** BR-005
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-008: Picture File Name Default Assignment

- **Given** An admin creates a catalog item without explicitly specifying PictureFileName
- **When** CatalogItem() constructor is called with no PictureFileName parameter
- **Then** Constructor assigns PictureFileName = 'dummy.png' (DefaultPictureName constant), item retains this default on database insert unless overridden
- **Priority:** medium
- **Verification:** Unit test: instantiate CatalogItem() with default constructor, assert PictureFileName == 'dummy.png'. Test with explicit PictureFileName override, assert override value is retained.
- **Related rules:** BR-006
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-009: Picture URI Construction for Ported Application

- **Given** A catalog item is displayed in the ported eShopPorted application
- **When** CatalogController.Index or Details action executes AddUriPlaceHolder() method
- **Then** PictureUri is constructed as '/Pics/{item.Id}.png' (relative URL path), image element src is set to this URI, when client requests /items/{itemId}/pic, PicController resolves and serves the image file
- **Priority:** high
- **Verification:** Integration test: navigate to /Catalog/Index, inspect HTML img src attributes, verify format matches '/Pics/\d+\.png'. Request /items/1/pic, assert HTTP 200 and image binary content returned.
- **Related rules:** BR-008
- **Related journeys:** UJ-001
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-010: Anti-Forgery Token Validation on Mutation Endpoints

- **Given** An admin submits a catalog item form via POST (Create, Edit, DeleteConfirmed)
- **When** POST request to /Catalog/Create, /Catalog/Edit, or /Catalog/DeleteConfirmed is submitted without or with invalid __RequestVerificationToken
- **Then** [ValidateAntiForgeryToken] attribute intercepts request, validates token against session/cookie, if invalid or missing returns HTTP 400 Bad Request (AntiForgeryValidationException), request is not processed; if valid, form processing continues
- **Priority:** high
- **Verification:** Security test: submit POST without token, verify 400 Bad Request. Submit with valid token (captured from form), verify request succeeds. Verify token is unique per session (CSRF protection).
- **Related rules:** BR-014
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-011: Create New Catalog Item Flow

- **Given** An admin navigates to /Catalog/Create and completes the form with valid data
- **When** CatalogController.Create(GET) loads form, admin fills Name='Test Item', Price=25.50, CatalogBrandId=2, CatalogTypeId=1, AvailableStock=100, submits POST with valid anti-forgery token
- **Then** POST handler validates ModelState (all required fields, price format, stock range), calls service.CreateCatalogItem(catalogItem), service persists item (legacy: assigns ID via HiLo generator, ported: EF Core assigns IDENTITY), HTTP redirect returns to /Catalog/Index, new item appears in catalog list
- **Priority:** high
- **Verification:** Integration test: load /Catalog/Create, submit valid form, verify HTTP 302 redirect to Index. Query database, verify new item exists with correct Name, Price, Brand, Type. Verify item appears in paginated list.
- **Related rules:** BR-011
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-012: Edit Catalog Item Flow

- **Given** An admin navigates to /Catalog/Edit/{id} for an existing item
- **When** CatalogController.Edit(GET, id=5) loads the form, admin modifies Price from 19.99 to 24.99, updates AvailableStock from 50 to 75, submits POST with valid anti-forgery token
- **Then** POST handler validates ModelState, calls service.UpdateCatalogItem(catalogItem) with EntityState.Modified, service merges changes into DbContext, SaveChanges persists updates, HTTP redirect returns to /Catalog/Index, modified item reflects new values in catalog
- **Priority:** high
- **Verification:** Integration test: load /Catalog/Edit/5, verify form pre-populated with current values. Modify fields, submit, verify redirect to Index. Query item 5, verify Price and AvailableStock updated. Load Edit/5 again, verify new values displayed.
- **Related rules:** BR-011
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-013: Delete Catalog Item Flow

- **Given** An admin navigates to /Catalog/Delete/{id} to remove an item
- **When** CatalogController.Delete(GET, id=3) displays confirmation, admin clicks delete, POST to DeleteConfirmed(id=3) with valid anti-forgery token
- **Then** DeleteConfirmed handler calls service.RemoveCatalogItem(id), service loads item from DbContext, removes item, SaveChanges commits deletion, HTTP redirect returns to /Catalog/Index, deleted item no longer appears in catalog
- **Priority:** high
- **Verification:** Integration test: load /Catalog/Delete/3, verify confirmation page shows item details. Submit delete, verify HTTP 302 redirect. Query item 3 from database, verify it does not exist. Load /Catalog/Index, verify item 3 missing from list.
- **Related rules:** BR-011
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-014: Image MIME Type Resolution for Picture Serving

- **Given** A client requests an image via /items/{itemId}/pic
- **When** PicController.Index(catalogItemId=2) is invoked, item has PictureFileName='test.png'
- **Then** PicController.GetImageMimeTypeFromImageFileExtension(imageFileExtension) extracts extension '.png' and returns 'image/png', file is read from disk, response is returned with Content-Type header set to 'image/png', image displays correctly in browser
- **Priority:** medium
- **Verification:** Integration test: load /items/1/pic, verify HTTP 200 response. Check Content-Type header, assert matches expected MIME type for image format. Test multiple extensions (.jpg, .png, .gif, etc.), verify each returns correct MIME type.
- **Related rules:** BR-012
- **Related journeys:** UJ-001
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-015: REST API GET /api/brands Endpoint

- **Given** A client requests the catalog brands API endpoint
- **When** GET /api/brands is invoked
- **Then** BrandsController.Index() calls service.GetCatalogBrands(), returns IActionResult Ok(brands) with JSON-serialized list of CatalogBrand objects (Id, Brand properties), HTTP 200 response with Content-Type: application/json, client receives all available catalog brands
- **Priority:** medium
- **Verification:** Integration test: GET /api/brands, verify HTTP 200. Parse JSON response, verify it contains array of objects with Id and Brand properties. Verify all 5 preconfigured brands present (Azure, .NET, Visual Studio, SQL Server, Other).
- **Related rules:** BR-013
- **Related journeys:** None identified
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-016: REST API DELETE /api/brands/{id} Endpoint

- **Given** A client requests deletion of a brand via REST API
- **When** DELETE /api/brands/{id} is invoked with id=2 (.NET brand)
- **Then** BrandsController.Delete(id=2) calls service.GetCatalogBrands().FirstOrDefault(b => b.Id == 2), if found removes brand and returns Ok(), if not found returns NotFound(), HTTP 404 response if brand not found, HTTP 200 if deleted
- **Priority:** medium
- **Verification:** Integration test: DELETE /api/brands/2, verify HTTP 200 Ok response. GET /api/brands, verify brand 2 no longer in list. DELETE /api/brands/999, verify HTTP 404 NotFound.
- **Related rules:** BR-013
- **Related journeys:** None identified
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-017: Reference Data Seeding: Catalog Brands

- **Given** A new database is initialized or EF Core migration 'Initial' is applied
- **When** CatalogDBContext applies HasData() configuration for CatalogBrand
- **Then** 5 catalog brands are inserted (Id 1-5): Azure, .NET, Visual Studio, SQL Server, Other; each brand retains its seeded ID and Name across environment resets, brands are available in dropdown selectors on Create/Edit forms
- **Priority:** high
- **Verification:** Integration test: apply migration, query CatalogBrand table, verify exactly 5 rows exist with expected names and IDs. Load /Catalog/Create, inspect ViewBag.CatalogBrandId SelectList, verify all 5 brands present in dropdown.
- **Related rules:** BR-013
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-018: Reference Data Seeding: Catalog Types

- **Given** A new database is initialized or EF Core migration 'Initial' is applied
- **When** CatalogDBContext applies HasData() configuration for CatalogType
- **Then** 4 catalog types are inserted (Id 1-4): Mug, T-Shirt, Sheet, USB Memory Stick; types are available in dropdown selectors on Create/Edit forms, type IDs persist across environment resets
- **Priority:** high
- **Verification:** Integration test: apply migration, query CatalogType table, verify 4 rows with expected types and IDs. Load /Catalog/Create, verify ViewBag.CatalogTypeId SelectList contains all 4 types.
- **Related rules:** BR-013
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-019: Model Validation Error Display on Create Form Failure

- **Given** An admin submits a catalog item creation form with invalid data (e.g., Name=null, Price=invalid format)
- **When** CatalogController.Create(POST, catalogItem) is called with invalid ModelState
- **Then** [ValidateAntiForgeryToken] passes, ModelState.IsValid returns false, controller repopulates ViewBag.CatalogBrandId and ViewBag.CatalogTypeId SelectLists, returns View(catalogItem) with the same form, HTML form helper displays validation error messages for each invalid field (e.g., 'Name is required', 'Price must match pattern'), user can correct and resubmit
- **Priority:** high
- **Verification:** Integration test: POST /Catalog/Create with missing Name, verify HTTP 200 form re-render (not redirect). Inspect HTML, verify validation error messages displayed. Verify form retains submitted values for resubmission. Test price regex error, verify 'positive number with maximum two decimals' error shown.
- **Related rules:** BR-005, BR-001
- **Related journeys:** UJ-002
- **Related APIs:** None identified
- **Related NFRs:** None identified

### AC-020: Catalog Item Details View

- **Given** A user clicks 'Details' link for a catalog item or navigates to /Catalog/Details/{id}
- **When** CatalogController.Details(id=5) is invoked
- **Then** If id is null, returns BadRequest(). If item not found, returns NotFound(). If found, service.FindCatalogItem(id) retrieves item, AddUriPlaceHolder() sets PictureUri, View displays item details (Name, Description, Price, Brand, Type, Stock levels, Picture), user can navigate back or edit
- **Priority:** high
- **Verification:** Integration test: GET /Catalog/Details/5, verify HTTP 200 and item details displayed. GET /Catalog/Details/null or /Catalog/Details/999, verify HTTP 400/404. Verify image URI constructed as /Pics/5.png.
- **Related rules:** BR-011
- **Related journeys:** UJ-001
- **Related APIs:** None identified
- **Related NFRs:** None identified
