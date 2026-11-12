<?php

declare(strict_types=1);

namespace App\Booking;

use DateTimeImmutable;

final class Appointment
{
    public function __construct(
        public readonly int $id,
        public readonly int $patientId,
        public readonly int $providerId,
        public readonly DateTimeImmutable $start,
        public readonly DateTimeImmutable $end,
        public readonly ?string $reason = null,
        public readonly bool $cancelled = false,
    ) {
    }

    public function cancel(): self
    {
        return new self($this->id, $this->patientId, $this->providerId, $this->start, $this->end, $this->reason, true);
    }

    public function overlaps(DateTimeImmutable $start, DateTimeImmutable $end): bool
    {
        return $this->start <= $end && $start <= $this->end;
    }
}
