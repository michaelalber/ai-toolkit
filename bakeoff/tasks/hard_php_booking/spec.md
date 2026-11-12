Plain PHP 8.4 appointment booking under `src/Booking/` (namespace `App\Booking`, autoloaded from `src/`). Implement `BookAppointmentRequest::validate()` and `BookingService`, and fix any bugs you find in existing classes. Run the tests with the `run_tests` tool (PHPUnit). Do not edit `tests/` or `phpunit.xml`.

**`BookAppointmentRequest::validate(array $input): array`** returns `field => message` (only the first failing rule per field; `[]` if valid). Unknown fields are ignored.
- `patient_id`, `provider_id`: missing/null/`''` -> `The {field} field is required.`; otherwise it must be a positive integer (an int, or a string of digits) -> `The {field} must be a positive integer.`
- `start`: required (same message form). Must be a string `YYYY-MM-DDTHH:MM:SS` followed by `Z` or `+HH:MM`/`-HH:MM`, and a real calendar date-time -> `The start must be an ISO 8601 date-time with a UTC offset.`
- `duration_minutes`: required. Must be 15, 30, 45 or 60 (int or digit string) -> `The selected duration_minutes is invalid.`
- `reason`: optional (absent or null is fine). Non-string -> `The reason must be a string.`; more than 200 characters -> `The reason may not be greater than 200 characters.`

**`BookingService::book(array $input): Appointment`**: on any failure throw `ValidationException` with exactly one error, checked in this order:
1. Request validation errors (all of them, as returned by `validate`).
2. `provider_id` not in the provider time-zone map -> `['provider_id' => 'The selected provider_id is invalid.']`
3. Start not strictly after `Clock::now()` -> `['start' => 'The start must be a date after now.']`
4. In the **provider's** time zone, the appointment must be Monday–Friday, start at or after 09:00 and end at or before 17:00 the same day -> `['start' => "The start must be within the provider's working hours."]`
5. Overlaps a non-cancelled appointment of the same provider -> `['start' => 'The provider is not available at that time.']`
6. Overlaps a non-cancelled appointment of the same patient with any provider -> `['start' => 'The patient already has an appointment at that time.']`

Intervals are `[start, end)`, so back-to-back appointments do not overlap. On success, save and return an `Appointment` with the next repository id, `start`/`end` in UTC, int ids, and `reason` (null if absent).

**`BookingService::cancel(int $id): Appointment`**: unknown id -> `\OutOfBoundsException`; already cancelled -> `\LogicException`; otherwise save and return the cancelled appointment. Cancelled appointments never block new bookings.
