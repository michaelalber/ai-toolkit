<?php

declare(strict_types=1);

namespace Tests;

use App\Booking\BookAppointmentRequest;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class BookAppointmentRequestTest extends TestCase
{
    private const VALID = [
        'patient_id' => 1,
        'provider_id' => 7,
        'start' => '2026-03-03T10:00:00-07:00',
        'duration_minutes' => 30,
    ];

    private function errorsFor(array $overrides): array
    {
        return (new BookAppointmentRequest())->validate(array_merge(self::VALID, $overrides));
    }

    public function testValidInputHasNoErrors(): void
    {
        $this->assertSame([], (new BookAppointmentRequest())->validate(self::VALID));
    }

    public function testUnknownFieldsAreIgnored(): void
    {
        $this->assertSame([], $this->errorsFor(['extra' => 'x']));
    }

    public function testAllRequiredFieldsMissing(): void
    {
        $this->assertEquals([
            'patient_id' => 'The patient_id field is required.',
            'provider_id' => 'The provider_id field is required.',
            'start' => 'The start field is required.',
            'duration_minutes' => 'The duration_minutes field is required.',
        ], (new BookAppointmentRequest())->validate([]));
    }

    public function testNullAndEmptyStringCountAsMissing(): void
    {
        $this->assertEquals(
            ['patient_id' => 'The patient_id field is required.', 'start' => 'The start field is required.'],
            $this->errorsFor(['patient_id' => null, 'start' => '']),
        );
    }

    public static function badIds(): array
    {
        return [['abc'], [0], [-1], [1.5], ['1.5'], [' 3'], [true]];
    }

    #[DataProvider('badIds')]
    public function testIdsMustBePositiveIntegers(mixed $id): void
    {
        $this->assertEquals(
            ['patient_id' => 'The patient_id must be a positive integer.',
             'provider_id' => 'The provider_id must be a positive integer.'],
            $this->errorsFor(['patient_id' => $id, 'provider_id' => $id]),
        );
    }

    public function testDigitStringIdsAreAccepted(): void
    {
        $this->assertSame([], $this->errorsFor(['patient_id' => '12', 'provider_id' => '7']));
    }

    public static function badStarts(): array
    {
        return [
            'space separator' => ['2026-03-03 10:00:00Z'],
            'no offset' => ['2026-03-03T10:00:00'],
            'no seconds' => ['2026-03-03T10:00Z'],
            'impossible date' => ['2026-02-30T10:00:00Z'],
            'impossible hour' => ['2026-03-03T25:00:00Z'],
            'not a string' => [1772546400],
            'offset without colon' => ['2026-03-03T10:00:00+0200'],
        ];
    }

    #[DataProvider('badStarts')]
    public function testStartMustBeStrictIso8601WithOffset(mixed $start): void
    {
        $this->assertEquals(
            ['start' => 'The start must be an ISO 8601 date-time with a UTC offset.'],
            $this->errorsFor(['start' => $start]),
        );
    }

    public static function goodStarts(): array
    {
        return [['2026-03-03T10:00:00Z'], ['2026-03-03T10:00:00+05:30'], ['2026-03-03T23:59:59-07:00']];
    }

    #[DataProvider('goodStarts')]
    public function testGoodStarts(string $start): void
    {
        $this->assertSame([], $this->errorsFor(['start' => $start]));
    }

    public static function durations(): array
    {
        return [[15, true], [30, true], [45, true], [60, true], ['45', true], [20, false], [0, false], [90, false], ['thirty', false], [30.0, false]];
    }

    #[DataProvider('durations')]
    public function testDurationMustBeAllowedValue(mixed $duration, bool $ok): void
    {
        $expected = $ok ? [] : ['duration_minutes' => 'The selected duration_minutes is invalid.'];
        $this->assertEquals($expected, $this->errorsFor(['duration_minutes' => $duration]));
    }

    public function testReasonIsOptional(): void
    {
        $this->assertSame([], $this->errorsFor(['reason' => null]));
        $this->assertSame([], $this->errorsFor(['reason' => str_repeat('a', 200)]));
    }

    public function testReasonRules(): void
    {
        $this->assertEquals(['reason' => 'The reason must be a string.'], $this->errorsFor(['reason' => 5]));
        $this->assertEquals(
            ['reason' => 'The reason may not be greater than 200 characters.'],
            $this->errorsFor(['reason' => str_repeat('a', 201)]),
        );
    }
}
