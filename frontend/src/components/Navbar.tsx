"use client";

import { RefreshCw, BookOpen } from "lucide-react";
import { useState } from "react";

interface NavbarProps {
    onRefresh: () => void;
}

export function Navbar({ onRefresh }: NavbarProps) {
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await onRefresh();
        setTimeout(() => setIsRefreshing(false), 2000);
    };

    return (
        <nav
            className="bg-bg-secondary"
            style={{
                borderBottom: '1px solid rgba(51, 65, 85, 0.6)',
                padding: '16px 32px',
            }}
        >
            <div
                className="flex items-center justify-between"
                style={{ maxWidth: '1400px', margin: '0 auto' }}
            >
                {/* Logo + Title */}
                <div className="flex items-center" style={{ gap: '12px' }}>
                    <div
                        style={{
                            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                            borderRadius: '10px',
                            padding: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <BookOpen style={{ width: '20px', height: '20px', color: 'white' }} />
                    </div>
                    <div>
                        <h1
                            className="text-text-primary"
                            style={{
                                fontSize: '18px',
                                fontWeight: 700,
                                letterSpacing: '-0.02em',
                                lineHeight: 1.2,
                            }}
                        >
                            Paper Aggregator
                        </h1>
                        <p
                            className="text-text-muted"
                            style={{ fontSize: '11px', letterSpacing: '0.02em' }}
                        >
                            Research paper discovery
                        </p>
                    </div>
                </div>

                {/* Right actions */}
                <div className="flex items-center" style={{ gap: '10px' }}>
                    <a
                        href="https://github.com/RunWang123/Paper_Agg"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-text-secondary hover:text-text-primary transition-colors"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            padding: '7px 14px',
                            borderRadius: '8px',
                            border: '1px solid rgba(51, 65, 85, 0.5)',
                            fontSize: '13px',
                        }}
                    >
                        <svg style={{ width: '15px', height: '15px' }} fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
                        GitHub
                    </a>
                    <button
                        onClick={handleRefresh}
                        className="transition-colors"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            background: 'linear-gradient(135deg, #22c55e, #10b981)',
                            padding: '7px 16px',
                            borderRadius: '8px',
                            fontSize: '13px',
                            fontWeight: 600,
                            color: 'black',
                            border: 'none',
                            cursor: 'pointer',
                        }}
                    >
                        <RefreshCw
                            style={{ width: '14px', height: '14px' }}
                            className={isRefreshing ? "animate-spin" : ""}
                        />
                        Update Now
                    </button>
                </div>
            </div>
        </nav>
    );
}
