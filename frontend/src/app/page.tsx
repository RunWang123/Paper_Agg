"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { PaperCard } from "@/components/PaperCard";
import { Paper } from "@/types";
import { Loader2, Sparkles, Menu, X } from "lucide-react";

const CONFERENCES = [
  "ACM CCS",
  "CVPR",
  "ECCV",
  "ICCV",
  "ICLR",
  "ICML",
  "IEEE S&P",
  "NDSS",
  "NeurIPS",
  "USENIX Security",
];

const API_BASE = "http://150.136.114.211:8000";

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSmartSearch, setIsSmartSearch] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [minYear, setMinYear] = useState("");
  const [maxYear, setMaxYear] = useState("");
  const [selectedConferences, setSelectedConferences] = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleConference = (conf: string) => {
    setSelectedConferences((prev) =>
      prev.includes(conf) ? prev.filter((c) => c !== conf) : [...prev, conf]
    );
  };

  const clearFilters = () => {
    setSearchQuery("");
    setMinYear("");
    setMaxYear("");
    setSelectedConferences([]);
    setPage(1);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      let url = "";
      if (isSmartSearch && searchQuery.trim()) {
        const params = new URLSearchParams({ q: searchQuery, limit: "50" });
        if (minYear) params.append("min_year", minYear);
        if (maxYear) params.append("max_year", maxYear);
        selectedConferences.forEach((c) => params.append("conferences", c));
        url = `${API_BASE}/api/semantic-search?${params.toString()}`;
      } else {
        const params = new URLSearchParams({ page: page.toString(), limit: "6" });
        if (searchQuery.trim()) params.append("q", searchQuery);
        if (minYear) params.append("min_year", minYear);
        if (maxYear) params.append("max_year", maxYear);
        selectedConferences.forEach((c) => params.append("conferences", c));
        url = `${API_BASE}/api/search?${params.toString()}`;
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error(`Error: ${res.status}`);
      const data = await res.json();

      if (isSmartSearch && searchQuery.trim()) {
        setPapers(data.papers || []);
        setTotalCount(data.count || 0);
        setTotalPages(1);
      } else {
        setPapers(data.papers || []);
        setTotalPages(data.total_pages || 1);
        setTotalCount(data.total_count || 0);
      }
    } catch (error) {
      console.error("Failed to fetch papers:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
      fetchData();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery, isSmartSearch, minYear, maxYear, selectedConferences]);

  useEffect(() => {
    if (page > 1) fetchData();
  }, [page]);

  const handleRefresh = async () => {
    await fetch(`${API_BASE}/api/refresh`, { method: "POST" });
    fetchData();
  };

  return (
    <main className="min-h-screen bg-bg-primary">
      <Navbar onRefresh={handleRefresh} />

      {/* Mobile hamburger button */}
      <div
        className="lg:hidden"
        style={{ padding: '12px 16px 0' }}
      >
        <button
          onClick={() => setSidebarOpen(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            borderRadius: '10px',
            border: '1px solid rgba(51, 65, 85, 0.5)',
            background: 'rgba(26, 35, 50, 0.8)',
            color: '#94a3b8',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          <Menu style={{ width: '18px', height: '18px' }} />
          Filters
        </button>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="lg:hidden"
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 50,
            display: 'flex',
          }}
        >
          {/* Backdrop */}
          <div
            onClick={() => setSidebarOpen(false)}
            style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(4px)',
            }}
          />
          {/* Slide-out panel */}
          <div
            style={{
              position: 'relative',
              width: '280px',
              maxWidth: '85vw',
              height: '100vh',
              background: '#1a2332',
              borderRight: '1px solid rgba(51, 65, 85, 0.6)',
              overflowY: 'auto',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '24px',
            }}
          >
            {/* Close button */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#e2e8f0' }}>Filters</span>
              <button
                onClick={() => setSidebarOpen(false)}
                style={{ padding: '4px', color: '#94a3b8', cursor: 'pointer', background: 'none', border: 'none' }}
              >
                <X style={{ width: '20px', height: '20px' }} />
              </button>
            </div>

            {/* Search */}
            <input
              type="text"
              placeholder="Search keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-border bg-bg-primary text-sm text-text-primary placeholder:text-text-muted focus:border-accent-blue focus:outline-none transition-colors"
              style={{ padding: '10px 14px' }}
            />

            {/* Semantic Toggle */}
            <button
              onClick={() => setIsSmartSearch(!isSmartSearch)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
                width: '100%',
                border: isSmartSearch ? '1px solid rgba(59, 130, 246, 0.5)' : '1px solid rgba(51, 65, 85, 0.5)',
                background: isSmartSearch ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                color: isSmartSearch ? '#60a5fa' : '#94a3b8',
              }}
            >
              <Sparkles style={{ width: '14px', height: '14px' }} />
              {isSmartSearch ? 'Semantic ON' : 'Semantic'}
            </button>

            {/* Year Range */}
            <div>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '10px' }}>Year Range</h3>
              <div className="flex items-center gap-3">
                <input type="number" placeholder="Min" value={minYear} onChange={(e) => setMinYear(e.target.value)}
                  className="w-full rounded-lg border border-border bg-bg-primary text-sm text-text-primary placeholder:text-text-muted focus:border-accent-blue focus:outline-none"
                  style={{ padding: '8px 12px' }} />
                <span style={{ color: '#64748b' }}>–</span>
                <input type="number" placeholder="Max" value={maxYear} onChange={(e) => setMaxYear(e.target.value)}
                  className="w-full rounded-lg border border-border bg-bg-primary text-sm text-text-primary placeholder:text-text-muted focus:border-accent-blue focus:outline-none"
                  style={{ padding: '8px 12px' }} />
              </div>
            </div>

            {/* Conferences */}
            <div>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px' }}>Conferences</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {CONFERENCES.map((conf) => (
                  <label key={conf} className="flex items-center gap-3 cursor-pointer text-sm text-text-secondary hover:text-text-primary transition-colors select-none">
                    <input type="checkbox" checked={selectedConferences.includes(conf)} onChange={() => toggleConference(conf)} className="h-4 w-4 rounded border-border" />
                    {conf}
                  </label>
                ))}
              </div>
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => { setPage(1); fetchData(); setSidebarOpen(false); }}
                style={{ width: '100%', padding: '12px', borderRadius: '8px', background: '#22c55e', fontSize: '13px', fontWeight: 600, color: 'black', border: 'none', cursor: 'pointer' }}
              >
                Apply Filters
              </button>
              <button
                onClick={() => { clearFilters(); setSidebarOpen(false); }}
                style={{ width: '100%', padding: '8px', fontSize: '13px', color: '#64748b', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Clear
              </button>
            </div>

            <div style={{ textAlign: 'center' }}>
              <span style={{ fontSize: '11px', color: '#64748b' }}>{totalCount.toLocaleString()} papers</span>
            </div>
          </div>
        </div>
      )}

      <div className="mx-auto flex flex-col lg:flex-row" style={{ maxWidth: '1400px', paddingTop: '40px', paddingBottom: '40px', paddingLeft: '24px', paddingRight: '24px', gap: '40px' }}>

        {/* ── Desktop Sidebar (hidden on mobile) ── */}
        <aside className="hidden lg:block" style={{ width: '280px', flexShrink: 0 }}>
          <div style={{ position: 'sticky', top: '40px', borderRadius: '12px', border: '1px solid rgba(51, 65, 85, 0.5)', background: '#1a2332', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>

            {/* Search */}
            <div>
              <input
                type="text"
                placeholder="Search keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-border bg-bg-primary text-sm text-text-primary placeholder:text-text-muted focus:border-accent-blue focus:outline-none transition-colors"
                style={{ padding: '10px 14px' }}
              />
            </div>

            {/* Semantic Toggle */}
            <div>
              <button
                onClick={() => setIsSmartSearch(!isSmartSearch)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '10px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  width: '100%',
                  border: isSmartSearch ? '1px solid rgba(59, 130, 246, 0.5)' : '1px solid rgba(51, 65, 85, 0.5)',
                  background: isSmartSearch ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                  color: isSmartSearch ? '#60a5fa' : '#94a3b8',
                }}
              >
                <Sparkles style={{ width: '14px', height: '14px' }} />
                {isSmartSearch ? 'Semantic ON' : 'Semantic'}
              </button>
            </div>

            {/* Year Range */}
            <div>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '10px' }}>Year Range</h3>
              <div className="flex items-center gap-3">
                <input type="number" placeholder="Min" value={minYear} onChange={(e) => setMinYear(e.target.value)}
                  className="w-full rounded-lg border border-border bg-bg-primary text-sm text-text-primary placeholder:text-text-muted focus:border-accent-blue focus:outline-none"
                  style={{ padding: '8px 12px' }} />
                <span style={{ color: '#64748b' }}>–</span>
                <input type="number" placeholder="Max" value={maxYear} onChange={(e) => setMaxYear(e.target.value)}
                  className="w-full rounded-lg border border-border bg-bg-primary text-sm text-text-primary placeholder:text-text-muted focus:border-accent-blue focus:outline-none"
                  style={{ padding: '8px 12px' }} />
              </div>
            </div>

            {/* Conferences */}
            <div>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '12px' }}>Conferences</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {CONFERENCES.map((conf) => (
                  <label key={conf} className="flex items-center gap-3 cursor-pointer text-sm text-text-secondary hover:text-text-primary transition-colors select-none">
                    <input type="checkbox" checked={selectedConferences.includes(conf)} onChange={() => toggleConference(conf)} className="h-4 w-4 rounded border-border" />
                    {conf}
                  </label>
                ))}
              </div>
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button
                onClick={() => { setPage(1); fetchData(); }}
                style={{ width: '100%', padding: '12px', borderRadius: '8px', background: '#22c55e', fontSize: '13px', fontWeight: 600, color: 'black', border: 'none', cursor: 'pointer' }}
              >
                Apply Filters
              </button>
              <button
                onClick={clearFilters}
                style={{ width: '100%', padding: '8px', fontSize: '13px', color: '#64748b', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Clear
              </button>
            </div>

            <div style={{ textAlign: 'center' }}>
              <span style={{ fontSize: '11px', color: '#64748b' }}>{totalCount.toLocaleString()} papers</span>
            </div>
          </div>
        </aside>

        {/* ── Main Content ── */}
        <section className="flex-1 min-w-0">

          {/* Paper List */}
          {loading ? (
            <div className="flex h-64 items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-accent-blue" />
            </div>
          ) : papers.length === 0 ? (
            <div className="flex h-64 flex-col items-center justify-center text-text-muted">
              <p className="text-lg">No papers found.</p>
              <p className="text-sm mt-1">Try adjusting your search or filters.</p>
            </div>
          ) : (
            <>
              <div className="flex flex-col gap-8">
                {papers.map((paper) => (
                  <PaperCard key={paper.id} paper={paper} />
                ))}
              </div>

              {/* Pagination */}
              {!isSmartSearch && totalPages > 1 && (
                <div className="flex items-center justify-center gap-4" style={{ marginTop: '31px' }}>
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="rounded-lg border border-border bg-bg-card px-5 py-2.5 text-sm font-medium text-text-secondary hover:text-text-primary hover:border-text-muted disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <span className="text-sm font-medium text-text-secondary tabular-nums">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="rounded-lg border border-border bg-bg-card px-5 py-2.5 text-sm font-medium text-text-secondary hover:text-text-primary hover:border-text-muted disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}
