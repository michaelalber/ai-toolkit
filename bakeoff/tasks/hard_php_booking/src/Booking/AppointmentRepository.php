<?php

declare(strict_types=1);

namespace App\Booking;

interface AppointmentRepository
{
    public function nextId(): int;

    public function save(Appointment $appointment): void;

    public function find(int $id): ?Appointment;

    /** @return list<Appointment> including cancelled ones */
    public function forProvider(int $providerId): array;

    /** @return list<Appointment> including cancelled ones */
    public function forPatient(int $patientId): array;
}
