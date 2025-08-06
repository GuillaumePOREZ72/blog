export interface Post {
    id: string
    title: string
    content: string
    slug: string
    excerpt?: string
    tags: string[]
    is_published: boolean
    author_id: string
    author_email?: string
    featured_image?: string
    created_at?: string
    updated_at?: string
}

export interface PostCreate {
    title: string
    content: string
    slug: string
    excerpt?: string
    tags: string[]
    is_published: boolean
    featured_image?: string
}

export interface PostUpdate extends Partial<PostCreate> {
}

export interface APIResponse<T> {
    data: T
    message?: string
    success: boolean
}
