"use client";

import { Paper } from "../types";
import { ExternalLink, Download } from "lucide-react";

interface PaperCardProps {
    paper: Paper;
}

function getConferenceBadgeClass(conference: string): string {
    const conf = conference?.toUpperCase() || "";
    if (conf.includes("IEEE S&P") || conf.includes("IEEE SP")) return "badge-ieee-sp";
    if (conf.includes("ACM CCS") || conf.includes("CCS")) return "badge-acm-ccs";
    if (conf.includes("NDSS")) return "badge-ndss";
    if (conf.includes("USENIX")) return "badge-usenix";
    if (conf.includes("CVPR")) return "badge-cvpr";
    if (conf.includes("ICCV")) return "badge-iccv";
    if (conf.includes("ECCV")) return "badge-eccv";
    if (conf.includes("NEURIPS") || conf.includes("NIPS")) return "badge-neurips";
    if (conf.includes("ICML")) return "badge-icml";
    if (conf.includes("ICLR")) return "badge-iclr";
    if (conf.includes("IEEE VIS") || conf.includes("VIS")) return "badge-ieee-vis";
    return "badge-default";
}

export function PaperCard({ paper }: PaperCardProps) {
    return (
        <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block rounded-xl border border-border/60 bg-bg-card transition-all duration-200 hover:bg-bg-card-hover hover:border-accent-blue/30 cursor-pointer"
            style={{ padding: '16px 20px', textDecoration: 'none' }}
        >
            {/* Title */}
            <h3 className="text-xl font-semibold text-text-primary leading-snug" style={{ transition: 'color 0.15s' }}>
                {paper.title}
            </h3>

            {/* Conference Badge + Year */}
            <div className="flex items-center gap-4 mt-4">
                <span
                    className={`${getConferenceBadgeClass(paper.conference)} inline-block rounded-md text-sm font-bold tracking-wide`}
                    style={{ padding: '4px 6px' }}
                >
                    {paper.conference}
                </span>
                <span className="text-base text-text-secondary">{paper.year}</span>
                {paper.similarity && (
                    <span className="text-sm font-semibold text-accent-green">
                        {Math.round(paper.similarity)}% match
                    </span>
                )}
            </div>

            {/* Authors */}
            <p className="mt-4 text-[15px] text-text-secondary leading-relaxed">
                {paper.authors}
            </p>
        </a>
    );
}
