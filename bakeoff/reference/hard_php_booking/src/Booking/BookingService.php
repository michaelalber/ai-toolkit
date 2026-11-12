<?php

declare(strict_types=1);

namespace App\Booking;

use DateTimeImmutable;
use DateTimeZone;

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
        if ($errors = $this->request->validate($input)) {
            throw new ValidationException($errors);
        }
        $providerId = (int) $input['provider_id'];
        $patientId = (int) $input['patient_id'];
        $zone = $this->providerTimezones[$providerId] ?? null;
        if ($zone === null) {
            throw new ValidationException(['provider_id' => 'The selected provider_id is invalid.']);
        }

        $start = BookAppointmentRequest::parseStart($input['start'])->setTimezone(new DateTimeZone('UTC'));
        $end = $start->modify('+' . (int) $input['duration_minutes'] . ' minutes');

        if ($start <= $this->clock->now()) {
            self::fail('The start must be a date after now.');
        }
        if (!self::withinWorkingHours($start, $end, new DateTimeZone($zone))) {
            self::fail("The start must be within the provider's working hours.");
        }
        if (self::clashes($this->repository->forProvider($providerId), $start, $end)) {
            self::fail('The provider is not available at that time.');
        }
        if (self::clashes($this->repository->forPatient($patientId), $start, $end)) {
            self::fail('The patient already has an appointment at that time.');
        }

        $appointment = new Appointment(
            $this->repository->nextId(), $patientId, $providerId, $start, $end, $input['reason'] ?? null,
        );
        $this->repository->save($appointment);
        return $appointment;
    }

    public function cancel(int $id): Appointment
    {
        $appointment = $this->repository->find($id) ?? throw new \OutOfBoundsException("No appointment {$id}");
        if ($appointment->cancelled) {
            throw new \LogicException("Appointment {$id} is already cancelled");
        }
        $cancelled = $appointment->cancel();
        $this->repository->save($cancelled);
        return $cancelled;
    }

    private static function fail(string $message): never
    {
        throw new ValidationException(['start' => $message]);
    }

    private static function withinWorkingHours(DateTimeImmutable $start, DateTimeImmutable $end, DateTimeZone $zone): bool
    {
        $localStart = $start->setTimezone($zone);
        if ((int) $localStart->format('N') > 5) {
            return false;
        }
        return $localStart >= $localStart->setTime(9, 0) && $end <= $localStart->setTime(17, 0);
    }

    /** @param list<Appointment> $existing */
    private static function clashes(array $existing, DateTimeImmutable $start, DateTimeImmutable $end): bool
    {
        foreach ($existing as $a) {
            if (!$a->cancelled && $a->overlaps($start, $end)) {
                return true;
            }
        }
        return false;
    }
}
