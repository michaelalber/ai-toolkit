<?php

declare(strict_types=1);

namespace App\Booking;

final class BookAppointmentRequest
{
    /** @return array<string, string> field => first error message; empty when valid */
    public function validate(array $input): array
    {
        throw new \RuntimeException('Not implemented');
    }
}
