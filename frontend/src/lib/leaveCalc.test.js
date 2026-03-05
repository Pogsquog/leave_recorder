import { describe, it, expect } from 'vitest'
import { getYearStats, getYearRange } from './leaveCalc.js'
import { toISODate, today, addDays } from './dateUtils.js'

describe('leaveCalc', () => {
    const basePrefs = {
        annual_leave_allowance: 25,
        carryover_days: 0,
        carryover_max: 0,
        year_start_month: 1,
        year_start_day: 1,
    }

    describe('getYearRange', () => {
        it('returns Jan 1 to Dec 31 for standard year', () => {
            const prefs = { ...basePrefs, year_start_month: 1, year_start_day: 1 }
            const { startDate, endDate } = getYearRange(prefs, 2025)
            expect(startDate.getMonth()).toBe(0)
            expect(startDate.getDate()).toBe(1)
            expect(endDate.getMonth()).toBe(11)
            expect(endDate.getDate()).toBe(31)
        })

        it('returns Apr 1 to Mar 31 for UK tax year', () => {
            const prefs = { ...basePrefs, year_start_month: 4, year_start_day: 1 }
            const { startDate, endDate } = getYearRange(prefs, 2025)
            expect(startDate.getFullYear()).toBe(2025)
            expect(startDate.getMonth()).toBe(3)
            expect(startDate.getDate()).toBe(1)
            expect(endDate.getFullYear()).toBe(2026)
            expect(endDate.getMonth()).toBe(2)
            expect(endDate.getDate()).toBe(31)
        })
    })

    describe('getYearStats', () => {
        it('calculates remaining days correctly', () => {
            const currentYear = today().getFullYear()
            const entries = [
                { date: `${currentYear}-01-15`, leave_type: 'annual', half_day: false },
                { date: `${currentYear}-02-10`, leave_type: 'annual', half_day: true },
            ]
            const stats = getYearStats(basePrefs, entries)
            expect(stats.totalAllowance).toBe(25)
            expect(stats.takenDays).toBe(1.5)
            expect(stats.bookedDays).toBe(0)
            expect(stats.remainingDays).toBe(23.5)
        })

        it('includes carryover in total allowance', () => {
            const prefs = { ...basePrefs, carryover_days: 3, carryover_max: 5 }
            const entries = []
            const stats = getYearStats(prefs, entries)
            expect(stats.totalAllowance).toBe(28)
        })

        it('separates taken and booked days based on today', () => {
            const pastDate = toISODate(addDays(today(), -30))
            const futureDate = toISODate(addDays(today(), 30))
            const entries = [
                { date: pastDate, leave_type: 'annual', half_day: false },
                { date: futureDate, leave_type: 'annual', half_day: false },
            ]
            const stats = getYearStats(basePrefs, entries)
            expect(stats.takenDays).toBe(1)
            expect(stats.bookedDays).toBe(1)
        })
    })
})
