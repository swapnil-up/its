export type Severity = 'low' | 'medium' | 'high' | 'critical';

export type Status = 'new' | 'in_progress' | 'resolved' | 'closed';

export interface Issue {
    id: string
    title: string
    description: string
    severity: Severity
    status: Status
    assigned_to: string | null
    created_by: string
    created_at: string
    updated_at: string
}

export interface IssueFilters{
    search: string 
    severity: Severity | null
    status: Status | null
}