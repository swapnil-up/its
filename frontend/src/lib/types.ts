export type Severity = 'low' | 'medium' | 'high' | 'critical';

export type Status = 'new' | 'in_progress' | 'resolved' | 'closed';

export interface Issue {
	id: string;
	title: string;
	description: string;
	severity: Severity;
	status: Status;
	created_at: string;
	updated_at: string;
	creator: User;
	assignee: User | null;
	attachments?: [Attachment];
}

export interface IssueFilters {
	search: string;
	severity: Severity | null;
	status: Status | null;
}

export interface User {
	id: string;
	email: string;
	full_name: string;
}

export interface Attachment {
	id: string;
	issue_id: string;
	filename: string;
	content_type: string;
	size: number;
	uploader: User;
	created_at: string;
	url: string;
}
