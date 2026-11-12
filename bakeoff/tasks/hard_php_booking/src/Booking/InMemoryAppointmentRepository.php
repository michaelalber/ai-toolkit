<?php

declare(strict_types=1);

namespace App\Booking;

final class InMemoryAppointmentRepository implements AppointmentRepository
{
    /** @var array<int, Appointment> */
    private array $items = [];
    private int $lastId = 0;

    public function nextId(): int
    {
        return ++$this->lastId;
    }

    public function save(Appointment $appointment): void
    {
        $this->items[$appointment->id] = $appointment;
    }

    public function find(int $id): ?Appointment
    {
        return $this->items[$id] ?? null;
    }

    public function forProvider(int $providerId): array
    {
        return array_values(array_filter($this->items, fn (Appointment $a) => $a->providerId === $providerId));
    }

    public function forPatient(int $patientId): array
    {
        return array_values(array_filter($this->items, fn (Appointment $a) => $a->patientId === $patientId));
    }
}
