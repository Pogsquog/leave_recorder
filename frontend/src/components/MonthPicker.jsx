import { useState } from 'react'

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

export default function MonthPicker({ year, month, onChange }) {
    const [open, setOpen] = useState(false)

    const go = (dy, dm) => {
        let y = year, m = month + dm
        if (m > 12) { y += 1; m = 1 }
        if (m < 1) { y -= 1; m = 12 }
        y += dy
        onChange(y, m)
    }

    return (
        <div className="flex items-center gap-3">
            <button
                onClick={() => go(0, -1)}
                className="text-gray-400 hover:text-cyan-300 transition-colors px-2 py-1 rounded-lg hover:bg-cyan-500/10"
            >
                ‹
            </button>

            <div className="relative">
                <button
                    onClick={() => setOpen(o => !o)}
                    className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-fuchsia-400 hover:opacity-80 transition-opacity min-w-[12rem] text-center"
                >
                    {MONTHS[month - 1]} {year}
                </button>

                {open && (
                    <div className="absolute z-50 top-full mt-2 left-1/2 -translate-x-1/2 card-dark rounded-xl border border-cyan-500/30 p-4 shadow-2xl w-72">
                        <div className="flex items-center justify-between mb-3">
                            <button onClick={() => { go(-1, 0); setOpen(false) }} className="text-gray-400 hover:text-cyan-300 px-2">‹ {year - 1}</button>
                            <span className="text-cyan-300 font-semibold">{year}</span>
                            <button onClick={() => { go(1, 0); setOpen(false) }} className="text-gray-400 hover:text-cyan-300 px-2">{year + 1} ›</button>
                        </div>
                        <div className="grid grid-cols-3 gap-1">
                            {MONTHS.map((name, i) => (
                                <button
                                    key={i}
                                    onClick={() => { onChange(year, i + 1); setOpen(false) }}
                                    className={`py-1.5 text-xs rounded-lg transition-all ${i + 1 === month
                                        ? 'bg-cyan-500/30 text-cyan-300 border border-cyan-400/50'
                                        : 'text-gray-400 hover:bg-cyan-500/10 hover:text-cyan-300'}`}
                                >
                                    {name.slice(0, 3)}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <button
                onClick={() => go(0, 1)}
                className="text-gray-400 hover:text-cyan-300 transition-colors px-2 py-1 rounded-lg hover:bg-cyan-500/10"
            >
                ›
            </button>
        </div>
    )
}
