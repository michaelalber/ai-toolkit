<?php

declare(strict_types=1);

namespace App\Booking;

use DateTimeImmutable;

final class BookAppointmentRequest
{
    private const DURATIONS = [15, 30, 45, 60];
    private const START_SHAPE = '/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$/';

    /** @return array<string, string> field => first error message; empty when valid */
    public function validate(array $input): array
    {
        $errors = [];
        foreach (['patient_id', 'provider_id'] as $field) {
            if (self::missing($input, $field)) {
                $errors[$field] = "The {$field} field is required.";
            } elseif (!self::isDigits($input[$field]) || (int) $input[$field] < 1) {
                $errors[$field] = "The {$field} must be a positive integer.";
            }
        }

        if (self::missing($input, 'start')) {
            $errors['start'] = 'The start field is required.';
        } elseif (!is_string($input['start']) || self::parseStart($input['start']) === null) {
            $errors['start'] = 'The start must be an ISO 8601 date-time with a UTC offset.';
        }

        if (self::missing($input, 'duration_minutes')) {
            $errors['duration_minutes'] = 'The duration_minutes field is required.';
        } elseif (!self::isDigits($input['duration_minutes'])
            || !in_array((int) $input['duration_minutes'], self::DURATIONS, true)) {
            $errors['duration_minutes'] = 'The selected duration_minutes is invalid.';
        }

        $reason = $input['reason'] ?? null;
        if ($reason !== null && !is_string($reason)) {
            $errors['reason'] = 'The reason must be a string.';
        } elseif ($reason !== null && mb_strlen($reason) > 200) {
            $errors['reason'] = 'The reason may not be greater than 200 characters.';
        }

        return $errors;
    }

    /** Strict parse of an already shape-checked start; null when not a real date-time. */
    public static function parseStart(string $value): ?DateTimeImmutable
    {
        if (preg_match(self::START_SHAPE, $value) !== 1) {
            return null;
        }
        $dt = DateTimeImmutable::createFromFormat('!Y-m-d\TH:i:sP', $value);
        $problems = DateTimeImmutable::getLastErrors();
        if ($dt === false || ($problems !== false && ($problems['warning_count'] > 0 || $problems['error_count'] > 0))) {
            return null;
        }
        return $dt;
    }

    private static function missing(array $input, string $field): bool
    {
        return !array_key_exists($field, $input) || $input[$field] === null || $input[$field] === '';
    }

    private static function isDigits(mixed $value): bool
    {
        return is_int($value) || (is_string($value) && preg_match('/^\d+$/', $value) === 1);
    }
}
