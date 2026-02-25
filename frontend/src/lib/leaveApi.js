import { supabase } from '../supabase.js'
import { toISODate } from './dateUtils.js'

/**
 * Fetch all leave entries for the current user, optionally filtered by date range.
 */
export async function fetchLeaveEntries({ startDate, endDate } = {}) {
    let query = supabase
        .from('leave_entries')
        .select('*')
        .order('date')

    if (startDate) query = query.gte('date', toISODate(startDate))
    if (endDate) query = query.lte('date', toISODate(endDate))

    const { data, error } = await query
    if (error) throw error
    return data
}

/**
 * Toggle a leave entry: cycles through full-day → half-day → deleted.
 * Returns the new state: { entry: {...} | null }
 */
export async function cycleEntry(dateStr, leaveType = 'vacation', userId) {
    const { data: existing } = await supabase
        .from('leave_entries')
        .select('*')
        .eq('date', dateStr)
        .single()

    if (!existing) {
        const { data, error } = await supabase
            .from('leave_entries')
            .insert({ date: dateStr, leave_type: leaveType, half_day: false, user_id: userId })
            .select()
            .single()
        if (error) throw error
        return { entry: data, action: 'created' }
    } else if (!existing.half_day) {
        const { data, error } = await supabase
            .from('leave_entries')
            .update({ half_day: true })
            .eq('id', existing.id)
            .select()
            .single()
        if (error) throw error
        return { entry: data, action: 'half_day' }
    } else {
        const { error } = await supabase
            .from('leave_entries')
            .delete()
            .eq('id', existing.id)
        if (error) throw error
        return { entry: null, action: 'deleted' }
    }
}

/**
 * Toggle half-day on an existing entry, or create a half-day entry if none exists.
 */
export async function toggleHalfDay(dateStr, leaveType = 'vacation', userId) {
    const { data: existing } = await supabase
        .from('leave_entries')
        .select('*')
        .eq('date', dateStr)
        .single()

    if (!existing) {
        const { data, error } = await supabase
            .from('leave_entries')
            .insert({ date: dateStr, leave_type: leaveType, half_day: true, user_id: userId })
            .select()
            .single()
        if (error) throw error
        return { entry: data, action: 'created_half' }
    } else {
        const newHalfDay = !existing.half_day
        const { data, error } = await supabase
            .from('leave_entries')
            .update({ half_day: newHalfDay })
            .eq('id', existing.id)
            .select()
            .single()
        if (error) throw error
        return { entry: data, action: newHalfDay ? 'half_day' : 'full_day' }
    }
}

/**
 * Upsert leave entries for a range of dates. Skips weekends.
 * If all dates in range already have the given leave_type, deletes them all (toggle off).
 */
export async function upsertRange(dates, leaveType = 'vacation', userId, existingEntries) {
    const existingDates = new Set(existingEntries.map(e => e.date))
    const dateStrs = dates.map(d => toISODate(d))
    const allSet = dateStrs.every(d => existingDates.has(d))

    if (allSet) {
        const { error } = await supabase
            .from('leave_entries')
            .delete()
            .in('date', dateStrs)
        if (error) throw error
        return { action: 'deleted', count: dateStrs.length }
    }

    const toCreate = dateStrs
        .filter(d => !existingDates.has(d))
        .map(d => ({ date: d, leave_type: leaveType, half_day: false, user_id: userId }))

    const { error } = await supabase
        .from('leave_entries')
        .insert(toCreate)
    if (error) throw error
    return { action: 'created', count: toCreate.length }
}

/**
 * Delete a single leave entry by date string.
 */
export async function deleteEntry(dateStr) {
    const { error } = await supabase
        .from('leave_entries')
        .delete()
        .eq('date', dateStr)
    if (error) throw error
}
