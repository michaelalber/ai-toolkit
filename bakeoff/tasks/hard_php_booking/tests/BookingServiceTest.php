<?php

declare(strict_types=1);

namespace Tests;

use App\Booking\Appointment;
use App\Booking\BookingService;
use App\Booking\Clock;
use App\Booking\InMemoryAppointmentRepository;
use App\Booking\ValidationException;
use DateTimeImmutable;
use PHPUnit\Framework\TestCase;

final class BookingServiceTest extends TestCase
{
    private InMemoryAppointmentRepository $repo;
    private BookingService $service;

    protected function setUp(): void
    {
        $this->repo = new InMemoryAppointmentRepository();
        $clock = new class implements Clock {
            public function now(): DateTimeImmutable
            {
                return new DateTimeImmutable('2026-03-02T12:00:00Z'); // Monday
            }
        };
        $this->service = new BookingService(
            $this->repo,
            [7 => 'America/Denver', 8 => 'Europe/Berlin', 9 => 'America/Denver'],
            $clock,
        );
    }

    private function input(array $overrides = []): array
    {
        return array_merge([
            'patient_id' => 1,
            'provider_id' => 7,
            'start' => '2026-03-03T10:00:00-07:00', // Tuesday 10:00 in Denver (MST)
            'duration_minutes' => 30,
        ], $overrides);
    }

    private function assertBookingFails(array $input, array $errors): void
    {
        try {
            $this->service->book($input);
            $this->fail('Expected ValidationException');
        } catch (ValidationException $e) {
            $this->assertEquals($errors, $e->errors());
        }
    }

    private const HOURS = ['start' => "The start must be within the provider's working hours."];
    private const PROVIDER_BUSY = ['start' => 'The provider is not available at that time.'];
    private const PATIENT_BUSY = ['start' => 'The patient already has an appointment at that time.'];

    public function testBooksAndStoresInUtc(): void
    {
        $a = $this->service->book($this->input(['reason' => 'checkup']));

        $this->assertSame(1, $a->id);
        $this->assertSame('2026-03-03T17:00:00+00:00', $a->start->format('Y-m-d\TH:i:sP'));
        $this->assertSame('2026-03-03T17:30:00+00:00', $a->end->format('Y-m-d\TH:i:sP'));
        $this->assertSame(0, $a->start->getOffset());
        $this->assertSame('checkup', $a->reason);
        $this->assertFalse($a->cancelled);
        $this->assertSame($a, $this->repo->find(1));
    }

    public function testDigitStringIdsBecomeInts(): void
    {
        $a = $this->service->book($this->input(['patient_id' => '12', 'provider_id' => '7']));
        $this->assertSame(12, $a->patientId);
        $this->assertSame(7, $a->providerId);
        $this->assertNull($a->reason);
    }

    public function testRequestErrorsArePassedThroughAndNothingIsSaved(): void
    {
        $this->assertBookingFails(
            $this->input(['duration_minutes' => 20, 'patient_id' => 0]),
            ['duration_minutes' => 'The selected duration_minutes is invalid.',
             'patient_id' => 'The patient_id must be a positive integer.'],
        );
        $this->assertSame([], $this->repo->forProvider(7));
    }

    public function testUnknownProvider(): void
    {
        $this->assertBookingFails($this->input(['provider_id' => 99]),
            ['provider_id' => 'The selected provider_id is invalid.']);
    }

    public function testStartMustBeAfterNow(): void
    {
        // Also outside working hours: the "after now" rule is checked first.
        $this->assertBookingFails($this->input(['start' => '2026-03-02T11:00:00Z']),
            ['start' => 'The start must be a date after now.']);
        $this->assertBookingFails($this->input(['start' => '2026-03-02T12:00:00Z']),
            ['start' => 'The start must be a date after now.']);
    }

    public function testWorkingHoursBoundaries(): void
    {
        $this->assertBookingFails($this->input(['start' => '2026-03-03T08:30:00-07:00']), self::HOURS);
        $this->assertBookingFails($this->input(['start' => '2026-03-03T16:45:00-07:00']), self::HOURS);
        $a = $this->service->book($this->input(['start' => '2026-03-03T16:30:00-07:00']));
        $this->assertSame('2026-03-04T00:00:00+00:00', $a->end->format('Y-m-d\TH:i:sP'));
        $b = $this->service->book($this->input(['start' => '2026-03-03T09:00:00-07:00', 'patient_id' => 2]));
        $this->assertSame(2, $b->id);
    }

    public function testWeekendIsOutsideWorkingHours(): void
    {
        $this->assertBookingFails($this->input(['start' => '2026-03-07T10:00:00-07:00']), self::HOURS);
    }

    public function testWorkingHoursUseProviderZoneAcrossDst(): void
    {
        // Friday before US DST: 15:00Z is 08:00 MST. Monday after: 15:00Z is 09:00 MDT.
        $this->assertBookingFails($this->input(['start' => '2026-03-06T15:00:00Z']), self::HOURS);
        $a = $this->service->book($this->input(['start' => '2026-03-09T15:00:00Z']));
        $this->assertSame(1, $a->id);
    }

    public function testWorkingHoursUseProviderZoneNotInputOffset(): void
    {
        // Berlin provider: 08:00Z is 09:00 CET (ok); 16:00Z + 60 min ends 18:00 CET (not ok).
        $this->service->book($this->input(['provider_id' => 8, 'start' => '2026-03-03T08:00:00Z']));
        $this->assertBookingFails(
            $this->input(['provider_id' => 8, 'start' => '2026-03-03T09:00:00-07:00', 'duration_minutes' => 60]),
            self::HOURS,
        );
    }

    public function testProviderOverlapIsRejected(): void
    {
        $this->service->book($this->input());
        $this->assertBookingFails($this->input(['patient_id' => 2, 'start' => '2026-03-03T10:15:00-07:00']),
            self::PROVIDER_BUSY);
        $this->assertBookingFails($this->input(['patient_id' => 2, 'start' => '2026-03-03T09:45:00-07:00']),
            self::PROVIDER_BUSY);
    }

    public function testBackToBackIsAllowed(): void
    {
        $this->service->book($this->input());
        $after = $this->service->book($this->input(['patient_id' => 2, 'start' => '2026-03-03T10:30:00-07:00']));
        $before = $this->service->book($this->input(['patient_id' => 3, 'start' => '2026-03-03T09:30:00-07:00']));
        $this->assertSame([2, 3], [$after->id, $before->id]);
    }

    public function testPatientOverlapAcrossProviders(): void
    {
        $this->service->book($this->input(['duration_minutes' => 60]));
        $this->assertBookingFails($this->input(['provider_id' => 9, 'start' => '2026-03-03T10:30:00-07:00']),
            self::PATIENT_BUSY);
    }

    public function testProviderClashReportedBeforePatientClash(): void
    {
        $this->service->book($this->input());
        $this->assertBookingFails($this->input(), self::PROVIDER_BUSY);
    }

    public function testCancelledAppointmentsDoNotBlock(): void
    {
        $a = $this->service->book($this->input());
        $cancelled = $this->service->cancel($a->id);

        $this->assertTrue($cancelled->cancelled);
        $this->assertTrue($this->repo->find($a->id)->cancelled);
        $again = $this->service->book($this->input());
        $this->assertSame(2, $again->id);
    }

    public function testCancelUnknownAndTwice(): void
    {
        try {
            $this->service->cancel(42);
            $this->fail('Expected OutOfBoundsException');
        } catch (\OutOfBoundsException) {
        }
        $a = $this->service->book($this->input());
        $this->service->cancel($a->id);
        $this->expectException(\LogicException::class);
        $this->service->cancel($a->id);
    }

    public function testAppointmentOverlapIsEndExclusive(): void
    {
        $a = new Appointment(1, 1, 7, new DateTimeImmutable('2026-03-03T17:00:00Z'), new DateTimeImmutable('2026-03-03T17:30:00Z'));
        $this->assertFalse($a->overlaps(new DateTimeImmutable('2026-03-03T17:30:00Z'), new DateTimeImmutable('2026-03-03T18:00:00Z')));
        $this->assertFalse($a->overlaps(new DateTimeImmutable('2026-03-03T16:30:00Z'), new DateTimeImmutable('2026-03-03T17:00:00Z')));
        $this->assertTrue($a->overlaps(new DateTimeImmutable('2026-03-03T17:29:00Z'), new DateTimeImmutable('2026-03-03T18:00:00Z')));
    }
}
