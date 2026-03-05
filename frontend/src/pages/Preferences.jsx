import { useState, useEffect } from 'react'
import { fetchPreferences, savePreferences } from '../lib/prefsApi.js'

const YEAR_STARTS = [
    { label: 'January 1st (Calendar year)', month: 1, day: 1 },
    { label: 'April 1st (UK tax year)', month: 4, day: 1 },
    { label: 'July 1st', month: 7, day: 1 },
    { label: 'October 1st', month: 10, day: 1 },
]

export default function Preferences() {
    const [prefs, setPrefs] = useState(null)
    const [saving, setSaving] = useState(false)
    const [saved, setSaved] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchPreferences().then(setPrefs).catch(e => setError(e.message))
    }, [])

    const handleChange = field => e => {
        setPrefs(p => ({ ...p, [field]: Number(e.target.value) }))
        setSaved(false)
    }

    const handleYearStart = (month, day) => {
        setPrefs(p => ({ ...p, year_start_month: month, year_start_day: day }))
        setSaved(false)
    }

    const handleSave = async (e) => {
        e.preventDefault()
        setSaving(true)
        setError(null)
        try {
            await savePreferences({
                annual_leave_allowance: prefs.annual_leave_allowance,
                carryover_max: prefs.carryover_max,
                carryover_days: prefs.carryover_days,
                week_start: prefs.week_start,
                year_start_month: prefs.year_start_month,
                year_start_day: prefs.year_start_day,
            })
            setSaved(true)
        } catch (e) {
            setError(e.message)
        }
        setSaving(false)
    }

    if (!prefs) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="text-cyan-400 text-sm animate-pulse">Loading preferences…</div>
            </div>
        )
    }

    return (
        <div className="max-w-lg mx-auto">
            <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-fuchsia-400 tracking-wider mb-6">
                Preferences
            </h2>

            <form onSubmit={handleSave} className="space-y-6">
                <div className="card-dark rounded-xl p-6 space-y-5">
                    <h3 className="text-sm font-semibold text-cyan-300 uppercase tracking-widest border-b border-cyan-500/20 pb-2">Leave Allowance</h3>

                    <div>
                        <label className="block text-xs text-gray-400 mb-1">Annual leave days</label>
                        <input
                            type="number"
                            min="0"
                            max="365"
                            value={prefs.annual_leave_allowance}
                            onChange={handleChange('annual_leave_allowance')}
                            className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-cyan-100 text-sm focus:border-cyan-400 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-gray-400 mb-1">Carryover days (from last year)</label>
                        <input
                            type="number"
                            min="0"
                            max={prefs.carryover_max}
                            value={prefs.carryover_days}
                            onChange={handleChange('carryover_days')}
                            className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-cyan-100 text-sm focus:border-cyan-400 focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-xs text-gray-400 mb-1">Maximum carryover allowed</label>
                        <input
                            type="number"
                            min="0"
                            max="365"
                            value={prefs.carryover_max}
                            onChange={handleChange('carryover_max')}
                            className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-cyan-100 text-sm focus:border-cyan-400 focus:outline-none"
                        />
                    </div>
                </div>

                <div className="card-dark rounded-xl p-6 space-y-5">
                    <h3 className="text-sm font-semibold text-cyan-300 uppercase tracking-widest border-b border-cyan-500/20 pb-2">Calendar</h3>

                    <div>
                        <label className="block text-xs text-gray-400 mb-1">Week starts on</label>
                        <div className="flex gap-2">
                            {[{ label: 'Monday', value: 1 }, { label: 'Sunday', value: 0 }].map(opt => (
                                <button
                                    key={opt.value}
                                    type="button"
                                    onClick={() => { setPrefs(p => ({ ...p, week_start: opt.value })); setSaved(false) }}
                                    className={`flex-1 py-2 text-sm rounded-lg border transition-all ${prefs.week_start === opt.value
                                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300'
                                        : 'border-gray-600/50 text-gray-400 hover:border-cyan-500/50 hover:text-cyan-300'}`}
                                >
                                    {opt.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs text-gray-400 mb-2">Leave year starts</label>
                        <div className="space-y-2">
                            {YEAR_STARTS.map(ys => (
                                <button
                                    key={`${ys.month}-${ys.day}`}
                                    type="button"
                                    onClick={() => handleYearStart(ys.month, ys.day)}
                                    className={`w-full text-left px-3 py-2 text-sm rounded-lg border transition-all ${prefs.year_start_month === ys.month && prefs.year_start_day === ys.day
                                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300'
                                        : 'border-gray-600/50 text-gray-400 hover:border-cyan-500/50 hover:text-cyan-300'}`}
                                >
                                    {ys.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {error && <div className="text-xs p-3 rounded-lg border bg-red-900/30 border-red-500/50 text-red-400">{error}</div>}
                {saved && <div className="text-xs p-3 rounded-lg border bg-green-900/30 border-green-500/50 text-green-400">Preferences saved!</div>}

                <button
                    type="submit"
                    disabled={saving}
                    className="w-full bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-white py-2.5 rounded-lg text-sm font-medium hover:from-cyan-400 hover:to-fuchsia-400 transition-all neon-button-cyan disabled:opacity-50"
                >
                    {saving ? 'Saving…' : 'Save Preferences'}
                </button>
            </form>
        </div>
    )
}
