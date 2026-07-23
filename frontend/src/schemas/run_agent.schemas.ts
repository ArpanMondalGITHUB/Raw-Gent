import {z} from "zod"

export const JobStatusSchema = z.enum([
    'queued',
    'running',
    'completed',
    'failed'
])
export type Jobstatus = z.infer<typeof JobStatusSchema>;

export const ChangeTypeSchema = z.enum([
    'created',
    'modified',
    'deleted'
])
export type ChangeType = z.infer<typeof ChangeTypeSchema>;

export const RoleTypeSchema = z.enum([
    'user',
    'agent'
])
export type RoleType = z.infer<typeof RoleTypeSchema>;

export const WebSocketMessageTypeSchema = z.enum([
    'user_message',
    'create_pr',
    'agent_message',
    'status_update',
    'error',
])
export type WebSocketMessageType = z.infer<typeof WebSocketMessageTypeSchema>;

export const RunAgentRequestSchema = z.object({
    prompt:z.string().min(1,"Prompt Is Required"),
    repo_name:z.string(),
    installation_id:z.number(),
    branches:z.string()
});
export type RunAgentRequest = z.infer<typeof RunAgentRequestSchema>;

export const RunAgentResponseSchema = z.object({
    job_id:z.string(),
    status:z.enum(["queued"])
});
export type RunAgentResponse = z.infer<typeof RunAgentResponseSchema>;

// job status update
export const FileChangeSchema = z.object({
    file_path: z.string(),
    original_content: z.string().nullable().optional(),
    modified_content: z.string(),
    change_type: ChangeTypeSchema,
    language: z.string()
})
export type FileChange = z.infer<typeof FileChangeSchema>;

export const PullRequestResultSchema = z.object({
    branch_name: z.string(),
    branch_url: z.string(),
    pr_url: z.string(),
    pr_number: z.number(),
    title: z.string(),
    body: z.string().nullable().optional(),
    additions: z.number().default(0),
    deletions: z.number().default(0),
})
export type PullRequestResult = z.infer<typeof PullRequestResultSchema>;

export const AgentMessageSchema = z.object({
    role: RoleTypeSchema,
    content: z.string(),
    timestamp: z.string()
})
export type AgentMessage = z.infer<typeof AgentMessageSchema>;

export const JobStatusResponseSchema = z.object({
    job_id: z.string(),
    status: JobStatusSchema,
    messages: z.array(AgentMessageSchema),
    file_changes: z.array(FileChangeSchema),
    pr_result: PullRequestResultSchema.nullable().optional(),
    current_step: z.string().nullable().optional(),
    error: z.string().nullable().optional(),
    created_at: z.string(),
    updated_at: z.string().nullable().optional(),
})
export type JobStatusResponse = z.infer<typeof JobStatusResponseSchema>;

export const WebScoketMessageResponseSchema = z.object({
    type : WebSocketMessageTypeSchema,
    content:z.string(),
    job_id:z.string().optional(),
    timestamp:z.string()
})
export type WebScoketMessageResponse = z.infer<typeof WebScoketMessageResponseSchema>;

