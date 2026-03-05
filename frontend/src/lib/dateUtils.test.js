import { describe, it, expect } from 'vitest'
import {
    getMonthStartDate,
    getMonthEndDate,
    addDays,
    toISODate,
    parseISODate,
    datesEqual,
    monthCalendar,
    isWeekend,
} from './dateUtils.js'

describe('dateUtils', () => {
    describe('getMonthStartDate', () => {
        it('returns the first day of the month', () => {
            const d = getMonthStartDate(2025, 3)
            expect(d.getFullYear()).toBe(2025)
            expect(d.getMonth()).toBe(2)
            expect(d.getDate()).toBe(1)
        })
    })

    describe('getMonthEndDate', () => {
        it('returns the last day of the month', () => {
            const d = getMonthEndDate(2025, 3)
            expect(d.getFullYear()).toBe(2025)
            expect(d.getMonth()).toBe(2)
            expect(d.getDate()).toBe(31)
        })

        it('handles February correctly (non-leap year)', () => {
            const d = getMonthEndDate(2025, 2)
            expect(d.getDate()).toBe(28)
        })

        it('handles February correctly (leap year)', () => {
            const d = getMonthEndDate(2024, 2)
            expect(d.getDate()).toBe(29)
        })
    })

    describe('addDays', () => {
        it('adds days to a date', () => {
            const d = new Date(2025, 0, 1)
            const result = addDays(d, 5)
            expect(result.getDate()).toBe(6)
        })

        it('subtracts days with negative value', () => {
            const d = new Date(2025, 0, 10)
            const result = addDays(d, -5)
            expect(result.getDate()).toBe(5)
        })
    })

    describe('toISODate', () => {
        it('converts date to ISO string', () => {
            const d = new Date(2025, 2, 15)
            expect(toISODate(d)).toBe('2025-03-15')
        })
    })

    describe('parseISODate', () => {
        it('parses ISO date string', () => {
            const d = parseISODate('2025-03-15')
            expect(d.getFullYear()).toBe(2025)
            expect(d.getMonth()).toBe(2)
            expect(d.getDate()).toBe(15)
        })
    })

    describe('datesEqual', () => {
        it('returns true for equal dates', () => {
            const a = new Date(2025, 2, 15)
            const b = new Date(2025, 2, 15)
            expect(datesEqual(a, b)).toBe(true)
        })

        it('returns false for different dates', () => {
            const a = new Date(2025, 2, 15)
            const b = new Date(2025, 2, 16)
            expect(datesEqual(a, b)).toBe(false)
        })
    })

    describe('monthCalendar', () => {
        it('returns 6 weeks for March 2025', () => {
            const weeks = monthCalendar(2025, 3, 1)
            expect(weeks.length).toBe(6)
            expect(weeks[0].length).toBe(7)
        })

        it('first week has null padding for days before month start', () => {
            const weeks = monthCalendar(2025, 3, 1)
            // March 1, 2025 is a Saturday, so first 5 days (Mon-Fri) are null
            expect(weeks[0][0]).toBe(null)
            expect(weeks[0][1]).toBe(null)
            expect(weeks[0][2]).toBe(null)
            expect(weeks[0][3]).toBe(null)
            expect(weeks[0][4]).toBe(null)
            expect(weeks[0][5]?.getDate()).toBe(1)
            expect(weeks[0][6]?.getDate()).toBe(2)
        })

        it('last week has null padding for days after month end', () => {
            const weeks = monthCalendar(2025, 3, 1)
            const lastWeek = weeks[weeks.length - 1]
            expect(lastWeek[0]?.getDate()).toBe(31)
            expect(lastWeek[1]).toBe(null)
            expect(lastWeek[2]).toBe(null)
            expect(lastWeek[3]).toBe(null)
            expect(lastWeek[4]).toBe(null)
            expect(lastWeek[5]).toBe(null)
            expect(lastWeek[6]).toBe(null)
        })
    })

    describe('isWeekend', () => {
        it('returns true for Saturday', () => {
            const sat = new Date(2025, 2, 1)
            expect(isWeekend(sat, 1)).toBe(true)
        })

        it('returns true for Sunday', () => {
            const sun = new Date(2025, 2, 2)
            expect(isWeekend(sun, 1)).toBe(true)
        })

        it('returns false for weekday', () => {
            const mon = new Date(2025, 2, 3)
            expect(isWeekend(mon, 1)).toBe(false)
        })
    })
})
