import {z} from "zod"
export const RepoTypeSchema = z.object({
  id: z.number(),
  name: z.string(),
  full_name: z.string(),
  owner: z.object({
    login: z.string(),
  }),
  installation_id: z.union([z.string(),z.number()]),
})
export type RepoType = z.infer<typeof RepoTypeSchema>;
