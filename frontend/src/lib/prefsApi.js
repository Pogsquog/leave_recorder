import { supabase } from '../supabase.js'

const DEFAULT_PREFS = {
    annual_leave_allowance: 25,
    carryover_max: 5,
    carryover_days: 0,
    week_start: 1,
    year_start_month: 1,
    year_start_day: 1,
}

export async function fetchPreferences() {
    const { data, error } = await supabase
        .from('user_preferences')
        .select('*')
        .maybeSingle()

    if (error) throw error

    if (!data) {
        const { data: { user } } = await supabase.auth.getUser()
        const { data: created, error: err } = await supabase
            .from('user_preferences')
            .insert({ ...DEFAULT_PREFS, user_id: user.id })
            .select()
            .single()
        if (err) throw err
        return created
    }

    return data
}

export async function savePreferences(updates) {
    const { data: { user } } = await supabase.auth.getUser()
    const { data, error } = await supabase
        .from('user_preferences')
        .update(updates)
        .eq('user_id', user.id)
        .select()
        .single()
    if (error) throw error
    return data
}
