import { useState, useEffect, useCallback, useRef } from 'react'
import { supabase } from '../supabase.js'
import { fetchLeaveEntries, cycleEntry, upsertRange } from '../lib/leaveApi.js'
import { fetchPreferences } from '../lib/prefsApi.js'
import { getYearStats, getMonthData } from '../lib/leaveCalc.js'
import { today, toISODate, addDays, getMonthStartDate, getMonthEndDate } from '../lib/dateUtils.js'
import { getUKPublicHolidaysInRange } from '../lib/ukHolidays.js'
import MonthPicker from '../components/MonthPicker.jsx'
import YearStats from '../components/YearStats.jsx'

const LEAVE_COLORS = {
    vacation: {
        full: 'bg-cyan-500/30 border-cyan-400/60 text-cyan-200',
        half: 'bg-cyan-500/15 border-cyan-400/40 text-cyan-300',
        label: 'Vacation',
        dot: 'bg-cyan-400',
    },
    sick: {
        full: 'bg-fuchsia-500/30 border-fuchsia-400/60 text-fuchsia-200',
        half: 'bg-fuchsia-500/15 border-fuchsia-400/40 text-fuchsia-300',
        label: 'Sick',
        dot: 'bg-fuchsia-400',
    },
}

function DayCell({ cell, onLeftClick, onRightClick, onDragStart, onDragEnter, isDragHighlight, leaveType }) {
    if (!cell) {
        return <div className="h-14 md:h-16" />
    }

    const { date, dateStr, entry, isWeekend, isToday, isPast, publicHoliday } = cell
    const colors = entry ? LEAVE_COLORS[entry.leave_type] : null
    const isHighlighted = isDragHighlight && !isWeekend
    const isBlocked = isWeekend || publicHoliday

    const cellClass = [
        'h-14 md:h-16 rounded-lg border transition-all duration-100 select-none relative overflow-hidden',
        isToday ? 'ring-2 ring-cyan-400/70' : '',
        isBlocked ? 'opacity-30 cursor-default' : 'cursor-pointer',
        isPast && !entry && !isWeekend && !publicHoliday ? 'opacity-50' : '',
        entry
            ? (entry.half_day ? colors.half : colors.full)
            : isHighlighted
                ? 'bg-cyan-500/20 border-cyan-400/40 border'
                : publicHoliday
                    ? 'bg-emerald-500/20 border-emerald-400/50 hover:border-emerald-400/60'
                    : 'bg-gray-900/40 border-gray-700/40 hover:border-cyan-500/40 hover:bg-gray-800/50',
    ].filter(Boolean).join(' ')

    const handleRight = (e) => {
        e.preventDefault()
        if (!isBlocked) onRightClick(dateStr)
    }

    return (
        <div
            className={cellClass}
            onClick={() => !isBlocked && onLeftClick(dateStr)}
            onContextMenu={handleRight}
            onMouseDown={() => !isBlocked && onDragStart(date)}
            onMouseEnter={() => !isBlocked && onDragEnter(date)}
        >
            <div className={`absolute top-1 left-1.5 text-xs font-medium ${isToday ? 'text-cyan-300 font-bold' : isPast ? 'text-gray-500' : 'text-gray-400'}`}>
                {date.getDate()}
            </div>

            {entry && (
                <div className="absolute bottom-1 right-1.5 flex flex-col items-end gap-0.5">
                    {entry.half_day && (
                        <span className="text-[8px] uppercase tracking-widest opacity-70">½</span>
                    )}
                    <span className="text-[8px] uppercase tracking-widest opacity-70">
                        {entry.leave_type === 'sick' ? 'S' : 'V'}
                    </span>
                </div>
            )}

            {publicHoliday && !entry && (
                <div className="absolute bottom-1 left-1.5 right-1.5 text-[7px] uppercase tracking-wide text-emerald-300 text-center leading-tight">
                    {publicHoliday}
                </div>
            )}
        </div>
    )
}

export default function Calendar({ user }) {
    const now = today()
    const [year, setYear] = useState(now.getFullYear())
    const [month, setMonth] = useState(now.getMonth() + 1)
    const [entries, setEntries] = useState([])
    const [prefs, setPrefs] = useState(null)
    const [loading, setLoading] = useState(true)
    const [leaveType, setLeaveType] = useState('vacation')
    const [dragStart, setDragStart] = useState(null)
    const [dragEnd, setDragEnd] = useState(null)
    const [isDragging, setIsDragging] = useState(false)
    const [publicHolidays, setPublicHolidays] = useState({})

    const loadData = useCallback(async () => {
        setLoading(true)
        try {
            const [p, e] = await Promise.all([
                fetchPreferences(),
                fetchLeaveEntries(),
            ])
            setPrefs(p)
            setEntries(e)
        } catch (err) {
            console.error(err)
        }
        setLoading(false)
    }, [])

    useEffect(() => { loadData() }, [loadData])

    useEffect(() => {
        if (!prefs) return
        const monthStart = getMonthStartDate(year, month)
        const monthEnd = getMonthEndDate(year, month)
        const holidays = getUKPublicHolidaysInRange(monthStart, monthEnd)
        const holidayMap = {}
        holidays.forEach(h => {
            holidayMap[h.date] = h.name
        })
        setPublicHolidays(holidayMap)
    }, [year, month, prefs])

    const weekDays = prefs?.week_start === 0
        ? ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    const weeks = prefs ? getMonthData(year, month, entries, prefs, publicHolidays) : []
    const stats = prefs ? getYearStats(prefs, entries) : null

    const handleMonthChange = (y, m) => { setYear(y); setMonth(m) }
    const goToday = () => { setYear(now.getFullYear()); setMonth(now.getMonth() + 1) }

    const handleLeftClick = async (dateStr) => {
        if (isDragging) return
        const date = new Date(dateStr)
        const dow = date.getDay()
        const isWeekend = dow === 0 || dow === 6
        if (isWeekend || publicHolidays[dateStr]) return
        try {
            await cycleEntry(dateStr, leaveType, user.id)
            await loadData()
        } catch (err) { console.error(err) }
    }

    const handleRightClick = async (dateStr) => {
        if (publicHolidays[dateStr]) return
        try {
            const existing = entries.find(e => e.date === dateStr)
            if (!existing) return
            const { error } = await supabase
                .from('leave_entries')
                .update({ half_day: !existing.half_day })
                .eq('id', existing.id)
            if (!error) await loadData()
        } catch (err) { console.error(err) }
    }

    const handleDragStart = (date) => {
        setDragStart(date)
        setDragEnd(date)
        setIsDragging(true)
    }

    const handleDragEnter = (date) => {
        if (isDragging) setDragEnd(date)
    }

    const getDragDates = () => {
        if (!dragStart || !dragEnd) return []
        const [a, b] = dragStart <= dragEnd ? [dragStart, dragEnd] : [dragEnd, dragStart]
        const dates = []
        for (let d = new Date(a); d <= b; d = addDays(d, 1)) {
            const dow = d.getDay()
            const isWe = prefs?.week_start === 1
                ? dow === 0 || dow === 6
                : dow === 0 || dow === 6
            const dateStr = toISODate(d)
            const isPublicHoliday = publicHolidays[dateStr]
            if (!isWe && !isPublicHoliday) dates.push(new Date(d))
        }
        return dates
    }

    const dragDays = isDragging ? getDragDates() : []
    const dragDayStrs = new Set(dragDays.map(toISODate))

    const handleMouseUp = async () => {
        if (!isDragging || !dragStart) { setIsDragging(false); return }

        const dragDates = getDragDates()
        if (dragDates.length > 1) {
            try {
                const monthEntries = entries.filter(e => {
                    const start = getMonthStartDate(year, month)
                    const end = getMonthEndDate(year, month)
                    return e.date >= toISODate(start) && e.date <= toISODate(end)
                })
                await upsertRange(dragDates, leaveType, user.id, monthEntries)
                await loadData()
            } catch (err) { console.error(err) }
        }

        setIsDragging(false)
        setDragStart(null)
        setDragEnd(null)
    }

    return (
        <div className="space-y-4" onMouseUp={handleMouseUp} onMouseLeave={() => { if (isDragging) { setIsDragging(false); setDragStart(null); setDragEnd(null) } }}>
            {stats && <YearStats stats={stats} />}

            <div className="card-dark rounded-xl p-4 md:p-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-5">
                    <MonthPicker year={year} month={month} onChange={handleMonthChange} />

                    <div className="flex items-center gap-2 flex-wrap">
                        <button
                            onClick={goToday}
                            className="px-3 py-1.5 text-xs rounded-lg border border-gray-600/50 text-gray-400 hover:border-cyan-500/50 hover:text-cyan-300 transition-all"
                        >
                            Today
                        </button>

                        <div className="flex rounded-lg overflow-hidden border border-cyan-500/30">
                            {['vacation', 'sick'].map(lt => (
                                <button
                                    key={lt}
                                    onClick={() => setLeaveType(lt)}
                                    className={`px-3 py-1.5 text-xs font-medium transition-all ${leaveType === lt
                                        ? lt === 'vacation'
                                            ? 'bg-cyan-500/30 text-cyan-300'
                                            : 'bg-fuchsia-500/30 text-fuchsia-300'
                                        : 'text-gray-400 hover:text-gray-300'}`}
                                >
                                    {LEAVE_COLORS[lt].label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="mb-2 grid grid-cols-7 gap-1">
                    {weekDays.map(d => (
                        <div key={d} className="text-center text-xs text-gray-500 font-medium py-1">{d}</div>
                    ))}
                </div>

                {loading ? (
                    <div className="flex items-center justify-center py-16 text-cyan-400 text-sm animate-pulse">Loading…</div>
                ) : (
                    <div className="space-y-1">
                        {weeks.map((week, wi) => (
                            <div key={wi} className="grid grid-cols-7 gap-1">
                                {week.map((cell, di) => (
                                    <DayCell
                                        key={di}
                                        cell={cell}
                                        onLeftClick={handleLeftClick}
                                        onRightClick={handleRightClick}
                                        onDragStart={handleDragStart}
                                        onDragEnter={handleDragEnter}
                                        isDragHighlight={cell && isDragging && dragDayStrs.has(cell.dateStr)}
                                        leaveType={leaveType}
                                    />
                                ))}
                            </div>
                        ))}
                    </div>
                )}

                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-700/50">
                    {Object.entries(LEAVE_COLORS).map(([type, cfg]) => (
                        <div key={type} className="flex items-center gap-1.5 text-xs text-gray-400">
                            <div className={`w-2.5 h-2.5 rounded-sm ${cfg.dot}`} />
                            {cfg.label}
                        </div>
                    ))}
                    <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <div className="w-2.5 h-2.5 rounded-sm bg-emerald-500/30 border border-emerald-400/50" />
                        Public Holiday
                    </div>
                    <div className="text-xs text-gray-500 ml-auto">Left-click: toggle • Right-click: ½ day • Drag: range</div>
                </div>
            </div>
        </div>
    )
}
