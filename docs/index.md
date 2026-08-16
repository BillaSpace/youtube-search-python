---
title: yt-search-python
description: A modern YouTube search library for Python with sync and async APIs, playlists, transcripts, recommendations, Innertube support and stream URL handling.
---

<style>
:root {
  --bg: #0b0d10;
  --panel: rgba(255, 255, 255, 0.055);
  --panel-strong: rgba(255, 255, 255, 0.085);
  --border: rgba(255, 255, 255, 0.10);
  --border-strong: rgba(255, 255, 255, 0.16);
  --text: #f5f7fa;
  --muted: #a9b0ba;
  --soft: #d9dee5;
  --code-bg: #111419;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  color: var(--text);
  background:
    radial-gradient(900px 520px at 10% -10%, rgba(255,255,255,0.08), transparent 60%),
    radial-gradient(800px 420px at 100% 0%, rgba(255,255,255,0.05), transparent 60%),
    var(--bg);
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.65;
}

.ytsp-shell {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 72px;
}

.ytsp-nav {
  position: sticky;
  top: 16px;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 52px;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: rgba(13, 16, 20, 0.72);
  backdrop-filter: blur(18px) saturate(120%);
  -webkit-backdrop-filter: blur(18px) saturate(120%);
  box-shadow: 0 12px 40px rgba(0,0,0,0.20);
}

.ytsp-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.ytsp-mark {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background:
    linear-gradient(135deg, rgba(255,255,255,0.16), rgba(255,255,255,0.03));
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.10);
}

.ytsp-navlinks {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.ytsp-navlinks a {
  color: var(--muted);
  text-decoration: none;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 14px;
  transition: 160ms ease;
}

.ytsp-navlinks a:hover {
  color: var(--text);
  background: rgba(255,255,255,0.06);
}

.ytsp-hero {
  position: relative;
  overflow: hidden;
  padding: 58px;
  border: 1px solid var(--border);
  border-radius: 30px;
  background:
    linear-gradient(145deg, rgba(255,255,255,0.075), rgba(255,255,255,0.025));
  box-shadow: var(--shadow);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
}

.ytsp-hero::before {
  content: "";
  position: absolute;
  inset: -25% auto auto -10%;
  width: 460px;
  height: 460px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(255,255,255,0.08), transparent 68%);
  filter: blur(8px);
  pointer-events: none;
}

.ytsp-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  color: var(--soft);
  font-size: 13px;
  font-weight: 650;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.ytsp-kicker::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #e6e9ed;
  box-shadow: 0 0 0 5px rgba(255,255,255,0.06);
}

.ytsp-hero h1 {
  margin: 0;
  max-width: 860px;
  font-size: clamp(42px, 7vw, 76px);
  line-height: 0.98;
  letter-spacing: -0.055em;
  font-weight: 760;
}

.ytsp-hero p {
  max-width: 760px;
  margin: 24px 0 0;
  color: var(--muted);
  font-size: clamp(17px, 2vw, 20px);
}

.ytsp-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 30px;
}

.ytsp-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 16px;
  border: 1px solid var(--border-strong);
  border-radius: 13px;
  color: var(--text);
  background: rgba(255,255,255,0.075);
  text-decoration: none;
  font-weight: 650;
  transition: 180ms ease;
}

.ytsp-button:hover {
  transform: translateY(-1px);
  background: rgba(255,255,255,0.11);
  border-color: rgba(255,255,255,0.24);
}

.ytsp-button.secondary {
  color: var(--muted);
  background: transparent;
}

.ytsp-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 18px;
}

.ytsp-card {
  min-height: 178px;
  padding: 22px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background:
    linear-gradient(145deg, rgba(255,255,255,0.055), rgba(255,255,255,0.018));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 12px 36px rgba(0,0,0,0.16);
}

.ytsp-card h3 {
  margin: 0 0 8px;
  font-size: 17px;
  letter-spacing: -0.02em;
}

.ytsp-card p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.ytsp-section {
  margin-top: 58px;
}

.ytsp-section-head {
  margin-bottom: 18px;
}

.ytsp-section-head h2 {
  margin: 0;
  font-size: clamp(26px, 4vw, 38px);
  letter-spacing: -0.035em;
}

.ytsp-section-head p {
  margin: 8px 0 0;
  color: var(--muted);
}

.ytsp-code {
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--code-bg);
  box-shadow: 0 18px 50px rgba(0,0,0,0.22);
}

.ytsp-codebar {
  display: flex;
  align-items: center;
  gap: 7px;
  height: 42px;
  padding: 0 15px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(255,255,255,0.025);
}

.ytsp-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.22);
}

.ytsp-filename {
  margin-left: 6px;
  color: #7f8791;
  font: 12px/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.ytsp-code pre {
  margin: 0;
  padding: 22px;
  overflow-x: auto;
  color: #d9dee5;
  font: 13.5px/1.75 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  tab-size: 4;
}

.ytsp-code .kw { color: #f0f2f5; font-weight: 650; }
.ytsp-code .fn { color: #c7cdd5; }
.ytsp-code .str { color: #9ba4ae; }
.ytsp-code .cm { color: #68717c; }

.ytsp-inline {
  padding: 3px 7px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  background: rgba(255,255,255,0.045);
  color: #dfe3e8;
  font: 0.9em ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.ytsp-split {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 16px;
}

.ytsp-list {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
}

.ytsp-list li + li {
  margin-top: 8px;
}

.ytsp-note {
  padding: 20px 22px;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: rgba(255,255,255,0.035);
  color: var(--muted);
}

.ytsp-note strong {
  color: var(--text);
}

.ytsp-footer {
  margin-top: 64px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
  color: #7f8791;
  font-size: 13px;
}

.ytsp-footer a {
  color: #b7bec7;
  text-decoration: none;
}

@media (max-width: 900px) {
  .ytsp-grid {
    grid-template-columns: 1fr 1fr;
  }

  .ytsp-split {
    grid-template-columns: 1fr;
  }

  .ytsp-hero {
    padding: 40px 28px;
  }
}

@media (max-width: 640px) {
  .ytsp-shell {
    width: min(100% - 20px, 1120px);
  }

  .ytsp-nav {
    position: static;
    align-items: flex-start;
    flex-direction: column;
  }

  .ytsp-grid {
    grid-template-columns: 1fr;
  }

  .ytsp-hero {
    border-radius: 24px;
  }
}
</style>

<div class="ytsp-shell">

  <nav class="ytsp-nav">
    <a class="ytsp-brand" href="https://github.com/BillaSpace/yt-search-python">
      <span class="ytsp-mark"></span>
      <span>yt-search-python</span>
    </a>
    <div class="ytsp-navlinks">
      <a href="#install">Install</a>
      <a href="#examples">Examples</a>
      <a href="#streaming">Streaming</a>
      <a href="https://pypi.org/project/yt-search-python/">PyPI</a>
      <a href="https://github.com/BillaSpace/yt-search-python">GitHub</a>
    </div>
  </nav>

  <section class="ytsp-hero">
    <div class="ytsp-kicker">Python 3.9+ · Sync + Async</div>
    <h1>YouTube search for Python, without the API key overhead.</h1>
    <p>
      A compact Python library for YouTube search, playlists, recommendations,
      transcripts, comments, channels, Innertube data and stream-format handling.
      Built for both synchronous scripts and long-running async services.
    </p>
    <div class="ytsp-actions">
      <a class="ytsp-button" href="https://pypi.org/project/yt-search-python/">Install from PyPI</a>
      <a class="ytsp-button secondary" href="https://github.com/BillaSpace/yt-search-python">View source</a>
    </div>
  </section>

  <section class="ytsp-section">
    <div class="ytsp-grid">
      <article class="ytsp-card">
        <h3>Sync + Async</h3>
        <p>Use the standard namespace for synchronous code or <span class="ytsp-inline">youtubesearchpython.future</span> for asyncio applications.</p>
      </article>
      <article class="ytsp-card">
        <h3>No Data API key</h3>
        <p>Search and content discovery without requiring a YouTube Data API v3 project, key or quota.</p>
      </article>
      <article class="ytsp-card">
        <h3>Modern transport</h3>
        <p>Centralized HTTP lifecycle management designed for bots, workers and services that stay online for long periods.</p>
      </article>
      <article class="ytsp-card">
        <h3>Native playlists</h3>
        <p>Regular playlists plus YouTube Mix / Radio handling through Innertube-oriented flows.</p>
      </article>
      <article class="ytsp-card">
        <h3>Transcripts + social</h3>
        <p>Comments, transcripts, channels, hashtags, suggestions and recommendations in one library.</p>
      </article>
      <article class="ytsp-card">
        <h3>Stream integration</h3>
        <p>Format inspection and stream URL handling with optional external PO-token provider support.</p>
      </article>
    </div>
  </section>

  <section class="ytsp-section" id="install">
    <div class="ytsp-section-head">
      <h2>Install</h2>
      <p>Published on PyPI as <span class="ytsp-inline">yt-search-python</span>.</p>
    </div>

    <div class="ytsp-code">
      <div class="ytsp-codebar">
        <span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-dot"></span>
        <span class="ytsp-filename">terminal</span>
      </div>
      <pre>pip install yt-search-python</pre>
    </div>
  </section>

  <section class="ytsp-section" id="examples">
    <div class="ytsp-section-head">
      <h2>Search in a few lines</h2>
      <p>The same project supports simple scripts and asyncio-based applications.</p>
    </div>

    <div class="ytsp-split">
      <div class="ytsp-code">
        <div class="ytsp-codebar">
          <span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-dot"></span>
          <span class="ytsp-filename">sync.py</span>
        </div>
        <pre><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> VideosSearch

search = VideosSearch(<span class="str">"Arijit Singh"</span>, limit=<span class="fn">10</span>)
result = search.result()

<span class="kw">for</span> video <span class="kw">in</span> result[<span class="str">"result"</span>]:
    print(video[<span class="str">"title"</span>])</pre>
      </div>

      <div class="ytsp-code">
        <div class="ytsp-codebar">
          <span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-dot"></span>
          <span class="ytsp-filename">async.py</span>
        </div>
        <pre><span class="kw">from</span> youtubesearchpython.future <span class="kw">import</span> VideosSearch

search = VideosSearch(<span class="str">"Arijit Singh"</span>, limit=<span class="fn">10</span>)
result = <span class="kw">await</span> search.next()

<span class="kw">for</span> video <span class="kw">in</span> result[<span class="str">"result"</span>]:
    print(video[<span class="str">"title"</span>])</pre>
      </div>
    </div>
  </section>

  <section class="ytsp-section" id="streaming">
    <div class="ytsp-section-head">
      <h2>StreamURLFetcher</h2>
      <p>Inspect formats and resolve supported stream URLs without bundling token generation into the core library.</p>
    </div>

    <div class="ytsp-code">
      <div class="ytsp-codebar">
        <span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-dot"></span>
        <span class="ytsp-filename">stream.py</span>
      </div>
      <pre><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> StreamURLFetcher

fetcher = StreamURLFetcher(
    po_token=<span class="str">"YOUR_PO_TOKEN"</span>,
    visitor_data=<span class="str">"YOUR_VISITOR_DATA"</span>,
)

url = fetcher.get(<span class="str">"VIDEO_ID"</span>, <span class="fn">18</span>)
print(url)</pre>
    </div>

    <div class="ytsp-note" style="margin-top:16px;">
      <strong>PO-token support stays modular.</strong>
      Token generation and session-aware caching can be handled by
      <a href="https://github.com/BillaSpace/ytsp-po-token-provider" style="color:#dfe3e8;">ytsp-po-token-provider</a>,
      keeping the main library focused on search, metadata and stream integration.
    </div>
  </section>

  <section class="ytsp-section">
    <div class="ytsp-section-head">
      <h2>Built for real services</h2>
      <p>Resource ownership is centralized instead of letting every component create its own client pool.</p>
    </div>

    <div class="ytsp-split">
      <div class="ytsp-card">
        <h3>Connection lifecycle</h3>
        <ul class="ytsp-list">
          <li>Centralized HTTP client management</li>
          <li>Bounded connection behavior</li>
          <li>Reduced stale socket / FD accumulation</li>
          <li>Automatic async cleanup with event-loop ownership</li>
        </ul>
      </div>

      <div class="ytsp-card">
        <h3>Compatibility</h3>
        <ul class="ytsp-list">
          <li>Python 3.9+</li>
          <li>Sync and asyncio namespaces</li>
          <li>Modern <span class="ytsp-inline">httpx</span> transport</li>
          <li>Designed with current and upcoming Python runtimes in mind</li>
        </ul>
      </div>
    </div>
  </section>

  <footer class="ytsp-footer">
    <span>yt-search-python · BillaSpace</span>
    <span>
      <a href="https://github.com/BillaSpace/yt-search-python">GitHub</a>
      &nbsp;·&nbsp;
      <a href="https://pypi.org/project/yt-search-python/">PyPI</a>
      &nbsp;·&nbsp;
      <a href="https://github.com/BillaSpace/ytsp-po-token-provider">PO Token Provider</a>
    </span>
  </footer>

</div>
