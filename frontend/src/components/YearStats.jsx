export default function YearStats({ stats }) {
    if (!stats) return null

    const { totalAllowance, takenDays, bookedDays, remainingDays, daysUntilYearEnd } = stats

    const items = [
        { label: 'Total allowance', value: totalAllowance, color: 'text-cyan-300' },
        { label: 'Taken', value: takenDays, color: 'text-fuchsia-400' },
        { label: 'Booked', value: bookedDays, color: 'text-purple-400' },
        { label: 'Remaining', value: remainingDays, color: remainingDays < 0 ? 'text-red-400' : 'text-green-400' },
        { label: 'Days to year end', value: daysUntilYearEnd, color: 'text-gray-400' },
    ]

    const usedFraction = totalAllowance > 0
        ? Math.min(1, (takenDays + bookedDays) / totalAllowance)
        : 0

    return (
        <div className="card-dark rounded-xl p-4 neon-border">
            <div className="grid grid-cols-5 divide-x divide-cyan-500/20">
                {items.map(({ label, value, color }) => (
                    <div key={label} className="px-3 first:pl-0 last:pr-0 text-center">
                        <div className={`text-2xl font-bold ${color}`}>
                            {typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(1)) : value}
                        </div>
                        <div className="text-xs text-gray-500 mt-0.5 leading-tight">{label}</div>
                    </div>
                ))}
            </div>

            <div className="mt-3">
                <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-fuchsia-500 rounded-full transition-all duration-500"
                        style={{ width: `${usedFraction * 100}%` }}
                    />
                </div>
            </div>
        </div>
    )
}
