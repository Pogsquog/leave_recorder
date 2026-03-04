/**
 * UK Public Holidays calculator
 * 
 * Calculates bank/public holidays for England and Wales.
 * Note: Scotland and Northern Ireland have different holidays.
 */

/**
 * Returns Easter Sunday for the given year (Western Christianity)
 */
function getEasterSunday(year) {
    const a = year % 19
    const b = Math.floor(year / 100)
    const c = year % 100
    const d = Math.floor(b / 4)
    const e = b % 4
    const f = Math.floor((b + 8) / 25)
    const g = Math.floor((b - f + 1) / 3)
    const h = (19 * a + b - d - g + 15) % 30
    const i = Math.floor(c / 4)
    const k = c % 4
    const l = (32 + 2 * e + 2 * i - h - k) % 7
    const m = Math.floor((a + 11 * h + 22 * l) / 451)
    const month = Math.floor((h + l - 7 * m + 114) / 31)
    const day = ((h + l - 7 * m + 114) % 31) + 1

    return new Date(year, month - 1, day)
}

/**
 * Add days to a date
 */
function addDays(date, days) {
    const result = new Date(date)
    result.setDate(result.getDate() + days)
    return result
}

/**
 * Get the next weekday (Monday) if date falls on weekend
 */
function nextWeekday(date) {
    const d = new Date(date)
    const day = d.getDay()
    if (day === 6) { // Saturday
        return addDays(d, 2)
    } else if (day === 0) { // Sunday
        return addDays(d, 1)
    }
    return d
}

/**
 * Returns array of UK public holidays for the given year
 * Each entry: { date: 'YYYY-MM-DD', name: string }
 */
export function getUKPublicHolidays(year) {
    const holidays = []

    // New Year's Day (Jan 1)
    const newYear = nextWeekday(new Date(year, 0, 1))
    holidays.push({ date: newYear.toISOString().split('T')[0], name: "New Year's Day" })

    // Good Friday (Friday before Easter)
    const easter = getEasterSunday(year)
    const goodFriday = addDays(easter, -2)
    holidays.push({ date: goodFriday.toISOString().split('T')[0], name: "Good Friday" })

    // Easter Monday (Monday after Easter)
    const easterMonday = addDays(easter, 1)
    holidays.push({ date: easterMonday.toISOString().split('T')[0], name: "Easter Monday" })

    // Early May Bank Holiday (first Monday in May)
    const mayEarly = new Date(year, 4, 1)
    const mayEarlyDay = mayEarly.getDay()
    const mayEarlyOffset = mayEarlyDay === 0 ? 1 : (8 - mayEarlyDay) % 7
    const mayEarlyHoliday = addDays(mayEarly, mayEarlyOffset === 0 ? 7 : mayEarlyOffset)
    holidays.push({ date: mayEarlyHoliday.toISOString().split('T')[0], name: "Early May Bank Holiday" })

    // Spring Bank Holiday (last Monday in May)
    const maySpring = new Date(year, 4, 31)
    const maySpringDay = maySpring.getDay()
    const maySpringOffset = maySpringDay === 1 ? 0 : (maySpringDay + 6) % 7
    const maySpringHoliday = addDays(maySpring, -maySpringOffset)
    holidays.push({ date: maySpringHoliday.toISOString().split('T')[0], name: "Spring Bank Holiday" })

    // Summer Bank Holiday (last Monday in August) - England, Wales, Northern Ireland
    const augSummer = new Date(year, 7, 31)
    const augSummerDay = augSummer.getDay()
    const augSummerOffset = augSummerDay === 1 ? 0 : (augSummerDay + 6) % 7
    const augSummerHoliday = addDays(augSummer, -augSummerOffset)
    holidays.push({ date: augSummerHoliday.toISOString().split('T')[0], name: "Summer Bank Holiday" })

    // Christmas Day (Dec 25)
    const christmas = nextWeekday(new Date(year, 11, 25))
    holidays.push({ date: christmas.toISOString().split('T')[0], name: "Christmas Day" })

    // Boxing Day (Dec 26)
    const boxingDay = nextWeekday(new Date(year, 11, 26))
    holidays.push({ date: boxingDay.toISOString().split('T')[0], name: "Boxing Day" })

    // Sort by date
    holidays.sort((a, b) => new Date(a.date) - new Date(b.date))

    return holidays
}

/**
 * Check if a date string is a UK public holiday
 * Returns holiday name or null
 */
export function isUKPublicHoliday(dateStr, year = null) {
    const checkYear = year || new Date(dateStr).getFullYear()
    const holidays = getUKPublicHolidays(checkYear)
    const holiday = holidays.find(h => h.date === dateStr)
    return holiday ? holiday.name : null
}

/**
 * Get all UK public holidays for a date range
 */
export function getUKPublicHolidaysInRange(startDate, endDate) {
    const startYear = startDate.getFullYear()
    const endYear = endDate.getFullYear()
    const allHolidays = []

    for (let year = startYear; year <= endYear; year++) {
        allHolidays.push(...getUKPublicHolidays(year))
    }

    return allHolidays.filter(h => {
        const hDate = new Date(h.date)
        return hDate >= startDate && hDate <= endDate
    })
}
