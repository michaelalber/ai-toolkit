<?php

declare(strict_types=1);

namespace App\Booking;

final class BookingService
{
    /** @param array<int, string> $providerTimezones provider id => IANA time zone */
    public function __construct(
        private readonly AppointmentRepository $repository,
        private readonly array $providerTimezones,
        private readonly Clock $clock,
        private readonly BookAppointmentRequest $request = new BookAppointmentRequest(),
    ) {
    }

    public function book(array $input): Appointment
    {
        throw new \RuntimeException('Not implemented');
    }

    public function cancel(int $id): Appointment
    {
        throw new \RuntimeException('Not implemented');
    }
}
