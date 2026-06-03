# Laravel API Endpoint Template

Full content for a versioned, documented, secured endpoint. Replace `User`/`user`/`users`. All files
begin with `declare(strict_types=1);`. OpenAPI annotations use `darkaonline/l5-swagger` (swagger-php
attributes); `knuckleswtf/scribe` is an annotation-light alternative noted at the bottom.

## `app/Http/Resources/V1/UserResource.php`

```php
<?php

declare(strict_types=1);

namespace App\Http\Resources\V1;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

/** @mixin \App\Models\User */
final class UserResource extends JsonResource
{
    /** @return array<string, mixed> */
    public function toArray(Request $request): array
    {
        return [
            'id'         => $this->id,
            'name'       => $this->name,
            'email'      => $this->email,
            'created_at' => $this->created_at?->toIso8601String(),
        ];
    }
}
```

## `app/Http/Requests/Api/V1/StoreUserRequest.php`

```php
<?php

declare(strict_types=1);

namespace App\Http\Requests\Api\V1;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rules\Password;

final class StoreUserRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()?->can('create', \App\Models\User::class) ?? false;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        return [
            'name'     => ['required', 'string', 'max:255'],
            'email'    => ['required', 'email', 'max:255', 'unique:users,email'],
            'password' => ['required', 'confirmed', Password::defaults()],
        ];
    }
}
```

## `app/Http/Controllers/Api/V1/UserController.php`

Thin actions; the OpenAPI contract lives on each method. Business logic is delegated to a service
(see `php-feature-slice`).

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\V1\StoreUserRequest;
use App\Http\Resources\V1\UserResource;
use App\Models\User;
use Illuminate\Http\Resources\Json\AnonymousResourceCollection;
use OpenApi\Attributes as OA;

#[OA\Info(version: '1.0.0', title: 'Example API')]
final class UserController extends Controller
{
    #[OA\Get(
        path: '/api/v1/users',
        summary: 'List users',
        security: [['sanctum' => []]],
        tags: ['Users'],
        responses: [new OA\Response(response: 200, description: 'Paginated users')],
    )]
    public function index(): AnonymousResourceCollection
    {
        return UserResource::collection(User::query()->latest()->paginate(20));
    }

    #[OA\Post(
        path: '/api/v1/users',
        summary: 'Create a user',
        security: [['sanctum' => []]],
        tags: ['Users'],
        responses: [
            new OA\Response(response: 201, description: 'Created'),
            new OA\Response(response: 422, description: 'Validation error'),
        ],
    )]
    public function store(StoreUserRequest $request): UserResource
    {
        $user = User::create($request->validated());

        return (new UserResource($user))->additional(['message' => 'created']);
    }

    public function show(User $user): UserResource
    {
        return new UserResource($user);
    }
}
```

## `app/Http/Controllers/Api/HealthController.php`

```php
<?php

declare(strict_types=1);

namespace App\Http\Controllers\Api;

use Illuminate\Http\JsonResponse;

final class HealthController
{
    public function __invoke(): JsonResponse
    {
        return response()->json([
            'status'  => 'ok',
            'version' => config('app.version', 'dev'),
            'time'    => now()->toIso8601String(),
        ]);
    }
}
```

## `routes/api.php`

```php
<?php

declare(strict_types=1);

use App\Http\Controllers\Api\HealthController;
use App\Http\Controllers\Api\V1\UserController;
use Illuminate\Support\Facades\Route;

Route::get('/health', HealthController::class);   // public liveness

Route::prefix('v1')
    ->middleware(['auth:sanctum', 'throttle:api'])
    ->group(function (): void {
        Route::apiResource('users', UserController::class)->only(['index', 'show', 'store']);
    });
```

## `tests/Feature/Api/V1/UserEndpointTest.php` (Pest)

```php
<?php

declare(strict_types=1);

use App\Models\User;
use function Pest\Laravel\getJson;
use function Pest\Laravel\postJson;

it('returns 401 without a token', function (): void {
    postJson('/api/v1/users', [])->assertUnauthorized();
});

it('creates a user with a valid token', function (): void {
    $actor = User::factory()->create();

    Laravel\Sanctum\Sanctum::actingAs($actor);

    postJson('/api/v1/users', [
        'name' => 'Ada', 'email' => 'ada@example.test',
        'password' => 'Sufficiently-long-1', 'password_confirmation' => 'Sufficiently-long-1',
    ])->assertCreated()->assertJsonPath('data.email', 'ada@example.test');
});

it('answers health publicly', function (): void {
    getJson('/api/health')->assertOk()->assertJsonPath('status', 'ok');
});
```

## Scribe alternative

If `knuckleswtf/scribe` is the documentation tool, drop the `OA\*` attributes and document with PHPDoc
tags (`@group`, `@authenticated`, `@bodyParam`) above each action, then run `php artisan scribe:generate`.
The route/request/resource structure is identical.
