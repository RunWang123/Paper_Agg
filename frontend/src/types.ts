export interface Paper {
    id: number;
    title: string;
    authors: string;
    conference: string;
    year: number;
    url: string;
    pdf_url?: string;
    tags?: string;
    source_url?: string;
    similarity?: number; // For semantic search results
}

export interface SearchResponse {
    papers: Paper[];
    total_count: number;
    page: number;
    limit: number;
    total_pages: number;
}
