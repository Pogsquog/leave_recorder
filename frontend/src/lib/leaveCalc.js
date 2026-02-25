/**
 * Leave calculation logic - JS port of apps/leave/models.py LeaveCalculator
 */
import { getMonthStartDate, getMonthEndDate, toISODate, today, monthCalendar, isWeekend } from './dateUtils.js'

/**
 * Compute year stats for the given preferences and leave entries array.
 * entries: array of { date: 'YYYY-MM-DD', leave_type, half_day }
 * prefs: { annual_leave_allowance, carryover_days, carryover_max, year_start_month, year_start_day }
 */
export function getYearStats(prefs, entries) {
    const totalAllowance = prefs.annual_leave_allowance + (prefs.carryover_days || 0)
    const { startDate, endDate } = getYearRange(prefs)
    const now = today()

    const yearEntries = entries.filter(e => {
        const d = e.date
        return d >= toISODate(startDate) && d <= toISODate(endDate)
    })

    const todayStr = toISODate(now)
    const takenEntries = yearEntries.filter(e => e.date <= todayStr)
    const bookedEntries = yearEntries.filter(e => e.date > todayStr)

    const countDays = (arr) =>
        arr.reduce((sum, e) => sum + (e.half_day ? 0.5 : 1), 0)

    const takenDays = countDays(takenEntries)
    const bookedDays = countDays(bookedEntries)
    const remainingDays = totalAllowance - takenDays - bookedDays
    const daysUntilYearEnd = endDate >= now
        ? Math.floor((endDate - now) / (1000 * 60 * 60 * 24))
        : 0

    return {
        totalAllowance,
        takenDays,
        bookedDays,
        remainingDays,
        daysUntilYearEnd,
        yearStart: toISODate(startDate),
        yearEnd: toISODate(endDate),
    }
}

/**
 * Returns { startDate, endDate } for the current leave year.
 */
export function getYearRange(prefs, year = null) {
    const now = today()
    const m = prefs.year_start_month
    const d = prefs.year_start_day

    if (year === null) {
        const candidate = new Date(now.getFullYear(), m - 1, d)
        year = now < candidate ? now.getFullYear() - 1 : now.getFullYear()
    }

    const startDate = new Date(year, m - 1, d)
    const nextStart = new Date(year + 1, m - 1, d)
    const endDate = new Date(nextStart.getTime() - 86400000)
    return { startDate, endDate }
}

/**
 * Compute month data for the calendar grid.
 * Returns weeks array matching the structure used in the UI.
 */
export function getMonthData(year, month, entries, prefs) {
    const entriesByDate = {}
    entries.forEach(e => { entriesByDate[e.date] = e })

    const weeks = monthCalendar(year, month, prefs?.week_start ?? 1)
    const todayStr = toISODate(today())

    return weeks.map(week =>
        week.map(date => {
            if (!date) return null
            const dateStr = toISODate(date)
            return {
                date,
                dateStr,
                entry: entriesByDate[dateStr] || null,
                isWeekend: isWeekend(date, prefs?.week_start ?? 1),
                isToday: dateStr === todayStr,
                isPast: dateStr < todayStr,
            }
        })
    )
}
