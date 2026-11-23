<?php
// <AI-Generated START>
// Held-out tests: same spec as the visible tests, new inputs. Never copied into the model's workdir.

declare(strict_types=1);

namespace Tests;

use App\Booking\BookAppointmentRequest;
use App\Booking\BookingService;
use App\Booking\Clock;
use App\Booking\InMemoryAppointmentRepository;
use App\Booking\ValidationException;
use DateTimeImmutable;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class HiddenBookingTest extends TestCase
{
    private const VALID = [
        'patient_id' => 1,
        'provider_id' => 7,
        'start' => '2026-03-03T10:00:00-07:00',
        'duration_minutes' => 30,
    ];
    private const HOURS = ['start' => "The start must be within the provider's working hours."];
    private const START_FORMAT = ['start' => 'The start must be an ISO 8601 date-time with a UTC offset.'];

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

    private function errorsFor(array $overrides): array
    {
        return (new BookAppointmentRequest())->validate(array_merge(self::VALID, $overrides));
    }

    private function assertBookingFails(array $overrides, array $errors): void
    {
        try {
            $this->service->book(array_merge(self::VALID, $overrides));
            $this->fail('Expected ValidationException');
        } catch (ValidationException $e) {
            $this->assertEquals($errors, $e->errors());
        }
    }

    public function testZeroDigitStringAndArrayIdsAreNotPositiveIntegers(): void
    {
        $this->assertEquals(
            ['patient_id' => 'The patient_id must be a positive integer.',
             'provider_id' => 'The provider_id must be a positive integer.'],
            $this->errorsFor(['patient_id' => '0', 'provider_id' => [7]]),
        );
    }

    public function testOnlyFirstFailingRulePerField(): void
    {
        $this->assertEquals(['duration_minutes' => 'The duration_minutes field is required.'],
            $this->errorsFor(['duration_minutes' => '']));
    }

    public static function moreBadStarts(): array
    {
        return [
            'not a leap year' => ['2026-02-29T10:00:00Z'],
            'second 60' => ['2026-03-03T10:00:60Z'],
            'minute 60' => ['2026-03-03T10:60:00Z'],
            'trailing text' => ['2026-03-03T10:00:00Zjunk'],
            'array' => [['2026-03-03T10:00:00Z']],
        ];
    }

    #[DataProvider('moreBadStarts')]
    public function testMoreBadStarts(mixed $start): void
    {
        $this->assertEquals(self::START_FORMAT, $this->errorsFor(['start' => $start]));
    }

    public function testLeapDayAndExtremeOffsetAreValid(): void
    {
        $this->assertSame([], $this->errorsFor(['start' => '2028-02-29T10:00:00Z']));
        $this->assertSame([], $this->errorsFor(['start' => '2026-03-03T10:00:00+14:00']));
    }

    public function testBooleanDurationIsInvalid(): void
    {
        $this->assertEquals(['duration_minutes' => 'The selected duration_minutes is invalid.'],
            $this->errorsFor(['duration_minutes' => true]));
        $this->assertSame([], $this->errorsFor(['duration_minutes' => '60']));
    }

    public function testReasonEdgeCases(): void
    {
        $this->assertSame([], $this->errorsFor(['reason' => '']));
        $this->assertSame([], $this->errorsFor(['reason' => str_repeat('é', 200)]));
        $this->assertEquals(['reason' => 'The reason must be a string.'], $this->errorsFor(['reason' => ['x']]));
    }

    public function testRequestErrorsWinOverUnknownProvider(): void
    {
        $this->assertBookingFails(['provider_id' => 99, 'duration_minutes' => 10],
            ['duration_minutes' => 'The selected duration_minutes is invalid.']);
    }

    public function testUnknownProviderWinsOverPastStart(): void
    {
        $this->assertBookingFails(['provider_id' => 99, 'start' => '2026-03-01T10:00:00Z'],
            ['provider_id' => 'The selected provider_id is invalid.']);
    }

    public function testEndingExactlyAt17IsAllowedAndFridayIsAWorkday(): void
    {
        $a = $this->service->book(array_merge(self::VALID, ['start' => '2026-03-06T16:00:00-07:00', 'duration_minutes' => 60]));
        $this->assertSame('2026-03-07T00:00:00+00:00', $a->end->format('Y-m-d\TH:i:sP'));
    }

    public function testSundayIsOutsideWorkingHours(): void
    {
        $this->assertBookingFails(['start' => '2026-03-08T10:00:00-07:00'], self::HOURS);
    }

    public function testBerlinWorkingHoursAcrossEuDst(): void
    {
        // Friday before EU DST: 07:00Z is 08:00 CET. Monday after: 07:00Z is 09:00 CEST.
        $this->assertBookingFails(['provider_id' => 8, 'start' => '2026-03-27T07:00:00Z'], self::HOURS);
        $a = $this->service->book(array_merge(self::VALID, ['provider_id' => 8, 'start' => '2026-03-30T07:00:00Z']));
        $this->assertSame('2026-03-30T07:00:00+00:00', $a->start->format('Y-m-d\TH:i:sP'));
    }

    public function testContainedIntervalIsAProviderClash(): void
    {
        $this->service->book(array_merge(self::VALID, ['duration_minutes' => 60]));
        $this->assertBookingFails(['patient_id' => 2, 'start' => '2026-03-03T10:15:00-07:00', 'duration_minutes' => 15],
            ['start' => 'The provider is not available at that time.']);
    }

    public function testFailedBookingDoesNotConsumeAnId(): void
    {
        $this->assertBookingFails(['start' => '2026-03-08T10:00:00-07:00'], self::HOURS);
        $this->assertSame(1, $this->service->book(self::VALID)->id);
    }

    public function testCancelledAppointmentDoesNotBlockThePatientElsewhere(): void
    {
        $a = $this->service->book(self::VALID);
        $this->service->cancel($a->id);
        $b = $this->service->book(array_merge(self::VALID, ['provider_id' => 9]));
        $this->assertSame(2, $b->id);
        $this->assertSame(9, $b->providerId);
    }
}
// <AI-Generated END>
