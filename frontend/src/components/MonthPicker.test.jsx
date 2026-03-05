import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MonthPicker from './MonthPicker.jsx'

describe('MonthPicker', () => {
    const defaultProps = {
        year: 2025,
        month: 3,
        onChange: () => {},
    }

    it('displays the current year and month', () => {
        render(<MonthPicker {...defaultProps} />)
        expect(screen.getByText('March 2025')).toBeInTheDocument()
    })

    it('has previous month button', () => {
        render(<MonthPicker {...defaultProps} />)
        expect(screen.getByText('‹')).toBeInTheDocument()
    })

    it('has next month button', () => {
        render(<MonthPicker {...defaultProps} />)
        expect(screen.getAllByText('›').length).toBeGreaterThanOrEqual(1)
    })
})
