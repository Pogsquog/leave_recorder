/**
 * Date utility functions - JS port of apps/utils/dates.py
 */

export function getMonthStartDate(year, month) {
    return new Date(year, month - 1, 1)
}

export function getMonthEndDate(year, month) {
    return new Date(year, month, 0)
}

export function addDays(date, days) {
    const d = new Date(date)
    d.setDate(d.getDate() + days)
    return d
}

export function toISODate(date) {
    return date.toISOString().split('T')[0]
}

export function parseISODate(str) {
    const [y, m, d] = str.split('-').map(Number)
    return new Date(y, m - 1, d)
}

export function today() {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export function datesEqual(a, b) {
    return toISODate(a) === toISODate(b)
}

/**
 * Returns an array of weeks, each week an array of Date|null.
 * Week always has 7 entries; padding with null for days outside the month.
 * weekStart: 1 = Monday (default), 0 = Sunday
 */
export function monthCalendar(year, month, weekStart = 1) {
    const start = getMonthStartDate(year, month)
    const end = getMonthEndDate(year, month)

    let startDow = start.getDay()
    if (weekStart === 1) {
        startDow = (startDow + 6) % 7
    }

    const cells = []
    for (let i = 0; i < startDow; i++) cells.push(null)
    for (let d = new Date(start); d <= end; d = addDays(d, 1)) {
        cells.push(new Date(d))
    }
    while (cells.length % 7 !== 0) cells.push(null)

    const weeks = []
    for (let i = 0; i < cells.length; i += 7) {
        weeks.push(cells.slice(i, i + 7))
    }
    return weeks
}

/**
 * Returns true if the given date is a weekend, respecting weekStart.
 */
export function isWeekend(date, weekStart = 1) {
    const dow = date.getDay()
    if (weekStart === 1) {
        return dow === 0 || dow === 6
    } else {
        return dow === 0 || dow === 6
    }
}
