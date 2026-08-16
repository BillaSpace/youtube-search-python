---
title: yt-search-python
description: YouTube search library for Python with sync and async APIs, playlists, transcripts, recommendations, Innertube support and stream URL handling.
---

<style>
:root{
  --bg:#090b0e;
  --bg-soft:#0d1014;
  --glass:rgba(255,255,255,.055);
  --glass-strong:rgba(255,255,255,.08);
  --line:rgba(255,255,255,.10);
  --line-strong:rgba(255,255,255,.16);
  --text:#f4f6f8;
  --muted:#9ea6b0;
  --soft:#cfd5dc;
  --code:#0a0d11;
  --code-line:rgba(255,255,255,.075);
  --shadow:0 24px 70px rgba(0,0,0,.34);
  --radius:22px;
  --radius-sm:14px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;
  color:var(--text);
  background:
    radial-gradient(900px 520px at 8% -10%,rgba(255,255,255,.075),transparent 62%),
    radial-gradient(780px 440px at 100% 4%,rgba(255,255,255,.045),transparent 62%),
    linear-gradient(180deg,#090b0e 0%,#0b0e12 46%,#090b0e 100%);
  font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.62;
  overflow-wrap:anywhere;
}
a{color:inherit}
img{max-width:100%;height:auto}
.ytsp-wrap{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:24px 0 72px}
.ytsp-nav{
  position:sticky;top:14px;z-index:40;
  display:flex;align-items:center;justify-content:space-between;gap:18px;
  min-height:64px;padding:10px 12px 10px 14px;margin-bottom:28px;
  border:1px solid var(--line);border-radius:18px;
  background:rgba(10,13,17,.78);
  backdrop-filter:blur(20px) saturate(125%);
  -webkit-backdrop-filter:blur(20px) saturate(125%);
  box-shadow:0 14px 38px rgba(0,0,0,.22);
}
.ytsp-brand{display:flex;align-items:center;gap:11px;min-width:0;text-decoration:none}
.ytsp-logo{
  width:46px;height:36px;flex:0 0 auto;object-fit:cover;
  border-radius:10px;border:1px solid var(--line-strong);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
}
.ytsp-brand-copy{min-width:0}
.ytsp-brand-title{display:block;font-weight:760;letter-spacing:-.025em;white-space:nowrap}
.ytsp-brand-sub{display:block;color:var(--muted);font-size:11px;margin-top:-2px;white-space:nowrap}
.ytsp-navlinks{display:flex;align-items:center;justify-content:flex-end;gap:5px;flex-wrap:wrap}
.ytsp-navlinks a{
  color:var(--muted);text-decoration:none;font-size:13px;font-weight:600;
  padding:8px 10px;border:1px solid transparent;border-radius:10px;transition:.16s ease;
}
.ytsp-navlinks a:hover{color:var(--text);background:rgba(255,255,255,.055);border-color:var(--line)}
.ytsp-hero{
  position:relative;overflow:hidden;padding:clamp(30px,6vw,64px);
  border:1px solid var(--line);border-radius:30px;
  background:
    linear-gradient(145deg,rgba(255,255,255,.072),rgba(255,255,255,.018)),
    rgba(12,15,19,.72);
  box-shadow:var(--shadow);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
}
.ytsp-hero:before,.ytsp-hero:after{
  content:"";position:absolute;border-radius:999px;pointer-events:none;filter:blur(10px)
}
.ytsp-hero:before{width:460px;height:460px;left:-180px;top:-250px;background:radial-gradient(circle,rgba(255,255,255,.085),transparent 67%)}
.ytsp-hero:after{width:360px;height:360px;right:-180px;bottom:-210px;background:radial-gradient(circle,rgba(255,255,255,.05),transparent 68%)}
.ytsp-kicker{
  position:relative;z-index:1;display:inline-flex;align-items:center;gap:9px;
  color:var(--soft);font-size:12px;font-weight:700;letter-spacing:.085em;text-transform:uppercase
}
.ytsp-kicker:before{content:"";width:7px;height:7px;border-radius:50%;background:#dfe3e7;box-shadow:0 0 0 5px rgba(255,255,255,.055)}
.ytsp-hero h1{
  position:relative;z-index:1;max-width:900px;margin:17px 0 0;
  font-size:clamp(38px,7vw,78px);line-height:.98;letter-spacing:-.055em;font-weight:780
}
.ytsp-hero p{
  position:relative;z-index:1;max-width:800px;margin:24px 0 0;
  color:var(--muted);font-size:clamp(16px,2vw,20px)
}
.ytsp-actions{position:relative;z-index:1;display:flex;flex-wrap:wrap;gap:9px;margin-top:28px}
.ytsp-btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;
  padding:0 16px;border:1px solid var(--line-strong);border-radius:13px;
  background:rgba(255,255,255,.075);color:var(--text);text-decoration:none;font-size:14px;font-weight:680;
  transition:transform .16s ease,background .16s ease,border-color .16s ease
}
.ytsp-btn:hover{transform:translateY(-1px);background:rgba(255,255,255,.11);border-color:rgba(255,255,255,.24)}
.ytsp-btn.muted{background:transparent;color:var(--soft)}
.ytsp-btn .arrow{font-size:12px;opacity:.72}
.ytsp-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:16px}
.ytsp-stat,.ytsp-card{
  border:1px solid var(--line);background:linear-gradient(145deg,rgba(255,255,255,.052),rgba(255,255,255,.018));
  border-radius:18px;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)
}
.ytsp-stat{padding:18px}
.ytsp-stat strong{display:block;font-size:18px;letter-spacing:-.025em}
.ytsp-stat span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.ytsp-section{margin-top:56px;scroll-margin-top:96px}
.ytsp-section-head{display:flex;align-items:end;justify-content:space-between;gap:24px;margin-bottom:18px}
.ytsp-section-head h2{margin:0;font-size:clamp(27px,4vw,40px);letter-spacing:-.04em}
.ytsp-section-head p{max-width:650px;margin:6px 0 0;color:var(--muted)}
.ytsp-section-note{color:#7f8791;font-size:12px;white-space:nowrap}
.ytsp-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.ytsp-card{padding:21px;min-width:0}
.ytsp-card h3{margin:0 0 8px;font-size:16px;letter-spacing:-.02em}
.ytsp-card p{margin:0;color:var(--muted);font-size:13.5px}
.ytsp-code{
  width:100%;overflow:hidden;border:1px solid var(--code-line);border-radius:17px;
  background:var(--code);box-shadow:0 16px 42px rgba(0,0,0,.24)
}
.ytsp-codebar{
  height:40px;padding:0 13px;display:flex;align-items:center;gap:6px;
  border-bottom:1px solid var(--code-line);background:#0e1116
}
.ytsp-dot{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.22)}
.ytsp-file{margin-left:6px;color:#737b85;font:11px/1.2 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}
.ytsp-code pre{
  margin:0;padding:18px;overflow:auto;max-width:100%;white-space:pre;
  color:#d6dbe1;background:transparent!important;
  font:13px/1.72 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace
}
.ytsp-code code{background:transparent!important;color:inherit!important;padding:0!important;border:0!important}
.ytsp-code .kw{color:#f1f3f5;font-weight:700}.ytsp-code .str{color:#aeb6c0}.ytsp-code .num{color:#c7cdd5}.ytsp-code .cm{color:#68717a}
.ytsp-install{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.ytsp-note{
  padding:18px 20px;border:1px solid var(--line);border-radius:16px;
  background:rgba(255,255,255,.035);color:var(--muted);font-size:13.5px
}
.ytsp-note strong{color:var(--text)}
.ytsp-api-list{display:grid;grid-template-columns:1fr 1fr;gap:12px}
details.ytsp-api{
  min-width:0;border:1px solid var(--line);border-radius:18px;
  background:linear-gradient(145deg,rgba(255,255,255,.048),rgba(255,255,255,.016));
  overflow:hidden;transition:border-color .18s ease,background .18s ease
}
details.ytsp-api[open]{border-color:var(--line-strong);background:linear-gradient(145deg,rgba(255,255,255,.065),rgba(255,255,255,.019))}
details.ytsp-api>summary{
  list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:18px;
  min-height:72px;padding:16px 18px;user-select:none
}
details.ytsp-api>summary::-webkit-details-marker{display:none}
.ytsp-api-title{min-width:0}
.ytsp-api-title strong{display:block;font-size:15px;letter-spacing:-.015em}
.ytsp-api-title span{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.ytsp-chevron{flex:0 0 auto;width:28px;height:28px;border:1px solid var(--line);border-radius:9px;display:grid;place-items:center;color:#9098a2;transition:transform .18s ease}
details.ytsp-api[open]>summary .ytsp-chevron{transform:rotate(45deg)}
.ytsp-api-body{padding:0 18px 18px;border-top:1px solid rgba(255,255,255,.055)}
.ytsp-api-body>p{color:var(--muted);font-size:13.5px}
.ytsp-signature{
  display:block;margin:14px 0;padding:11px 12px;overflow:auto;border:1px solid var(--code-line);border-radius:11px;
  color:#cbd1d8;background:#0b0e12;font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;white-space:nowrap
}
details.ytsp-sub{
  margin-top:10px;border:1px solid rgba(255,255,255,.075);border-radius:13px;background:rgba(0,0,0,.13);overflow:hidden
}
details.ytsp-sub>summary{
  list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:12px 13px;color:var(--soft);font-size:12.5px;font-weight:700
}
details.ytsp-sub>summary::-webkit-details-marker{display:none}
details.ytsp-sub>summary:after{content:"+";color:#7f8791;font-size:16px;font-weight:400}
details.ytsp-sub[open]>summary:after{content:"−"}
.ytsp-sub-body{padding:0 12px 12px}
.ytsp-shape{
  margin:0;padding:16px;overflow:auto;border:1px solid var(--code-line);border-radius:12px;
  background:#0a0d11;color:#cfd5dc;
  font:12.5px/1.68 ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace;white-space:pre
}
.ytsp-badges{display:flex;gap:7px;flex-wrap:wrap;margin:12px 0 0}
.ytsp-chip{
  display:inline-flex;align-items:center;min-height:25px;padding:0 9px;border:1px solid var(--line);
  border-radius:999px;background:rgba(255,255,255,.035);color:#aeb6c0;font-size:11px;font-weight:650
}
.ytsp-support{
  display:grid;grid-template-columns:1fr 1fr;gap:12px;
  padding:20px;border:1px solid var(--line);border-radius:20px;background:rgba(255,255,255,.035)
}
.ytsp-support a{
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:15px 16px;border:1px solid var(--line);border-radius:14px;
  background:rgba(255,255,255,.035);text-decoration:none;color:var(--text);font-weight:680;transition:.16s ease
}
.ytsp-support a:hover{background:rgba(255,255,255,.075);border-color:var(--line-strong);transform:translateY(-1px)}
.ytsp-support small{display:block;color:var(--muted);font-weight:500;margin-top:2px}
.ytsp-support .go{color:#8c949e;font-size:13px}
.ytsp-footer{
  margin-top:58px;padding:24px 2px 0;border-top:1px solid var(--line);
  display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;color:#7e8791;font-size:12px
}
.ytsp-footer-links{display:flex;flex-wrap:wrap;gap:13px}
.ytsp-footer a{color:#b6bdc6;text-decoration:none}
.ytsp-inline{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;color:#d5dae0}
@media(max-width:980px){
  .ytsp-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .ytsp-api-list{grid-template-columns:1fr}
  .ytsp-stats{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:760px){
  .ytsp-wrap{width:min(100% - 20px,1180px);padding-top:10px}
  .ytsp-nav{position:static;align-items:flex-start;flex-direction:column;padding:11px;margin-bottom:16px}
  .ytsp-navlinks{width:100%;justify-content:flex-start;overflow-x:auto;flex-wrap:nowrap;padding-bottom:2px;scrollbar-width:none}
  .ytsp-navlinks::-webkit-scrollbar{display:none}
  .ytsp-navlinks a{white-space:nowrap}
  .ytsp-hero{border-radius:24px}
  .ytsp-install,.ytsp-support{grid-template-columns:1fr}
  .ytsp-section-head{align-items:flex-start;flex-direction:column;gap:4px}
  .ytsp-section-note{white-space:normal}
}
@media(max-width:560px){
  .ytsp-wrap{width:min(100% - 14px,1180px)}
  .ytsp-brand-sub{display:none}
  .ytsp-logo{width:42px;height:34px}
  .ytsp-hero{padding:28px 20px}
  .ytsp-hero h1{font-size:clamp(36px,13vw,52px)}
  .ytsp-actions{display:grid;grid-template-columns:1fr}
  .ytsp-btn{width:100%}
  .ytsp-grid,.ytsp-stats{grid-template-columns:1fr}
  details.ytsp-api>summary{padding:14px;min-height:68px}
  .ytsp-api-body{padding:0 14px 14px}
  .ytsp-code pre,.ytsp-shape{font-size:11.5px}
  .ytsp-footer{align-items:flex-start;flex-direction:column}
}
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*:before,*:after{transition:none!important;animation:none!important}
}
</style>

<div class="ytsp-wrap">

<nav class="ytsp-nav" aria-label="Primary">
  <a class="ytsp-brand" href="https://github.com/BillaSpace/yt-search-python">
    <img class="ytsp-logo" src="https://raw.githubusercontent.com/BillaSpace/yt-search-python/legacy/assets/yt-search-python-banner.jpg" alt="yt-search-python">
    <span class="ytsp-brand-copy">
      <span class="ytsp-brand-title">yt-search-python</span>
      <span class="ytsp-brand-sub">YouTube search &amp; content toolkit for Python</span>
    </span>
  </a>
  <div class="ytsp-navlinks">
    <a href="#install">Install</a>
    <a href="#api">API</a>
    <a href="#streaming">Streaming</a>
    <a href="#support">Support</a>
    <a href="https://pypi.org/project/yt-search-python/">PyPI</a>
    <a href="https://github.com/BillaSpace/yt-search-python">GitHub</a>
  </div>
</nav>

<section class="ytsp-hero">
  <div class="ytsp-kicker">Python 3.9+ · Sync + Async</div>
  <h1>YouTube search for Python, without the API-key overhead.</h1>
  <p>
    Search videos, playlists and channels; work with recommendations, suggestions,
    comments, transcripts, hashtags, Innertube data and stream formats from one compact
    Python library. The public API stays familiar while transport and resource ownership
    are centralized for long-running applications.
  </p>
  <div class="ytsp-actions">
    <a class="ytsp-btn" href="#install">Get started <span class="arrow">↓</span></a>
    <a class="ytsp-btn muted" href="https://github.com/BillaSpace/yt-search-python">Browse source <span class="arrow">↗</span></a>
    <a class="ytsp-btn muted" href="https://pypi.org/project/yt-search-python/">Open PyPI <span class="arrow">↗</span></a>
  </div>
</section>

<div class="ytsp-stats">
  <div class="ytsp-stat"><strong>Sync + Async</strong><span>Standard and future namespaces</span></div>
  <div class="ytsp-stat"><strong>No API key</strong><span>No YouTube Data API v3 quota</span></div>
  <div class="ytsp-stat"><strong>Innertube</strong><span>Search, playlists and content flows</span></div>
  <div class="ytsp-stat"><strong>Stream aware</strong><span>Formats, PO-token handoff and unresolved states</span></div>
</div>

<section class="ytsp-section" id="install">
  <div class="ytsp-section-head">
    <div>
      <h2>Install</h2>
      <p>Published on PyPI as <span class="ytsp-inline">yt-search-python</span>.</p>
    </div>
  </div>
  <div class="ytsp-install">
    <div class="ytsp-code">
      <div class="ytsp-codebar"><span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-file">terminal</span></div>
      <pre><code>pip install yt-search-python</code></pre>
    </div>
    <div class="ytsp-note">
      <strong>Async uses the same project.</strong><br>
      Import async classes from <span class="ytsp-inline">youtubesearchpython.future</span>.
      For transcript fallback support, install <span class="ytsp-inline">yt-search-python[transcript]</span>.
    </div>
  </div>
</section>

<section class="ytsp-section">
  <div class="ytsp-section-head">
    <div>
      <h2>Quick start</h2>
      <p>Simple search stays small; pagination is explicit.</p>
    </div>
  </div>
  <div class="ytsp-code">
    <div class="ytsp-codebar"><span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-dot"></span><span class="ytsp-file">search.py</span></div>
    <pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> VideosSearch

search = VideosSearch(<span class="str">"Arijit Singh"</span>, limit=<span class="num">10</span>)
print(search.result())

search.next()
print(search.result())</code></pre>
  </div>
</section>

<section class="ytsp-section" id="api">
  <div class="ytsp-section-head">
    <div>
      <h2>API reference</h2>
      <p>Open a method to see its signature. Examples and response shapes stay collapsed until you ask for them.</p>
    </div>
    <span class="ytsp-section-note">Tap / click any method</span>
  </div>

  <div class="ytsp-api-list">

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Search / VideosSearch</strong><span>General search, video-only search, live-only filtering and pagination</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">VideosSearch(query, limit=20, language="en", region="US", timeout=None, is_live=None)</code>
        <p>Use <span class="ytsp-inline">Search</span> for mixed results or <span class="ytsp-inline">VideosSearch</span> for videos. Call <span class="ytsp-inline">next()</span> for the next page. <span class="ytsp-inline">is_live=True</span> enables live-only search.</p>
        <div class="ytsp-badges"><span class="ytsp-chip">Sync</span><span class="ytsp-chip">Async</span><span class="ytsp-chip">Pagination</span><span class="ytsp-chip">Live filter</span></div>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">videos_search.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> VideosSearch

search = VideosSearch(<span class="str">"news"</span>, limit=<span class="num">10</span>, is_live=<span class="kw">True</span>)
first = search.result()

search.next()
second = search.result()</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "type": "video",
      "id": "VIDEO_ID",
      "title": "...",
      "publishedTime": "...",
      "duration": "...",
      "viewCount": {...},
      "thumbnails": [...],
      "channel": {...},
      "link": "https://www.youtube.com/watch?v=..."
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>ChannelsSearch / PlaylistsSearch</strong><span>Search channels or playlists with the same paginated interface</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">ChannelsSearch(query, limit=20, language="en", region="US", timeout=None)</code>
        <code class="ytsp-signature">PlaylistsSearch(query, limit=20, language="en", region="US", timeout=None)</code>
        <p>Both classes support <span class="ytsp-inline">result()</span> and <span class="ytsp-inline">next()</span> like the other search classes.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">typed_search.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> ChannelsSearch, PlaylistsSearch

channels = ChannelsSearch(<span class="str">"Google Developers"</span>, limit=<span class="num">5</span>)
playlists = PlaylistsSearch(<span class="str">"Python tutorial"</span>, limit=<span class="num">5</span>)

print(channels.result())
print(playlists.result())</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "type": "channel | playlist",
      "id": "...",
      "title": "...",
      "thumbnails": [...],
      "link": "..."
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>CustomSearch</strong><span>Apply YouTube search preference strings for custom filtering and sorting</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">CustomSearch(query, searchPreferences, limit=20, language="en", region="US", timeout=None)</code>
        <p>Use preference constants such as <span class="ytsp-inline">SearchMode</span>, <span class="ytsp-inline">VideoUploadDateFilter</span>, <span class="ytsp-inline">VideoDurationFilter</span> and <span class="ytsp-inline">VideoSortOrder</span> when constructing a custom search preference.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">custom_search.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> CustomSearch, SearchMode

search = CustomSearch(
    <span class="str">"Python"</span>,
    SearchMode.videos,
    limit=<span class="num">10</span>,
)
print(search.result())</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "type": "...",
      "id": "...",
      "title": "...",
      "...": "fields depend on the selected search mode"
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>ChannelSearch</strong><span>Search inside a specific channel browse ID</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">ChannelSearch(query, browseId, language="en", region="US", searchPreferences="EgZzZWFyY2g%3D", timeout=None)</code>
        <p>Useful when the query should be scoped to one channel rather than global YouTube search.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">channel_search.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> ChannelSearch

search = ChannelSearch(
    <span class="str">"Python"</span>,
    <span class="str">"UC_x5XG1OV2P6uZZ5FSM9Ttw"</span>,
)
print(search.result())
search.next()</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "id": "VIDEO_OR_PLAYLIST_ID",
      "title": "...",
      "thumbnails": [...],
      "link": "..."
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Video</strong><span>Video metadata, player information and format extraction</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Video.getInfo(videoLink, mode=ResultMode.dict, timeout=None, po_token=None, visitor_data=None, proxy=None)</code>
        <code class="ytsp-signature">Video.getFormats(videoLink, mode=ResultMode.dict, timeout=None, po_token=None, visitor_data=None, proxy=None)</code>
        <p>PO token and visitor data are optional inputs for sessions/clients where YouTube requires them.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">video.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Video

info = Video.getInfo(<span class="str">"pnxL4OOzPEc"</span>)
formats = Video.getFormats(
    <span class="str">"pnxL4OOzPEc"</span>,
    po_token=<span class="str">"TOKEN"</span>,
    visitor_data=<span class="str">"VISITOR_DATA"</span>,
)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "title": "...",
  "id": "VIDEO_ID",
  "duration": {...},
  "viewCount": {...},
  "channel": {...},
  "description": "...",
  "thumbnails": [...],
  "formats": [...]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Playlist</strong><span>Regular playlists plus native YouTube Mix / Radio playlists</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Playlist.get(playlistLink, mode=ResultMode.dict, timeout=None)</code>
        <code class="ytsp-signature">Playlist.getInfo(...) · Playlist.getVideos(...) · Playlist(link).getNextVideos()</code>
        <p>Regular playlists support continuation pages. Mix/Radio playlists (<span class="ytsp-inline">RD...</span>) use YouTube's native next flow and preserve returned order.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">playlist.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Playlist

data = Playlist.get(<span class="str">"PLAYLIST_ID"</span>)

playlist = Playlist(<span class="str">"PLAYLIST_ID"</span>)
next_page = playlist.getNextVideos()

mix = Playlist.get(
    <span class="str">"https://youtube.com/playlist?list=RDpnxL4OOzPEc&amp;playnext=1"</span>
)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "id": "PLAYLIST_ID",
  "title": "...",
  "channel": {...},
  "thumbnails": [...],
  "videos": [
    {
      "id": "VIDEO_ID",
      "title": "...",
      "duration": "...",
      "thumbnails": [...]
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Recommendations</strong><span>Related videos with stable ordering and duplicate removal</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Recommendations.get(videoId, timeout=None)</code>
        <p>The source video is skipped and duplicate IDs are removed without re-sorting YouTube's returned order.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">recommendations.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Recommendations

related = Recommendations.get(<span class="str">"pnxL4OOzPEc"</span>)
print(related)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">[
  {
    "id": "RELATED_VIDEO_ID",
    "title": "...",
    "thumbnails": [...],
    "channel": {...},
    "link": "..."
  }
]</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Suggestions</strong><span>Query suggestions with language / region support and reusable sessions</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Suggestions.get(query, language="en", region="US", timeout=None, mode=ResultMode.dict)</code>
        <code class="ytsp-signature">Suggestions.session(language="en", region="US", timeout=None)</code>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">suggestions.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Suggestions

print(Suggestions.get(<span class="str">"Guru Randhawa"</span>))

session = Suggestions.session(language=<span class="str">"en"</span>, region=<span class="str">"US"</span>)
print(session.get(<span class="str">"Python"</span>))</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    "suggestion one",
    "suggestion two",
    "..."
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Comments</strong><span>Video comments with continuation support</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Comments.get(videoLink, mode=ResultMode.dict, timeout=None)</code>
        <code class="ytsp-signature">Comments(videoLink).getNextComments()</code>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">comments.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Comments

first = Comments.get(<span class="str">"pnxL4OOzPEc"</span>)

comments = Comments(<span class="str">"pnxL4OOzPEc"</span>)
comments.init()
next_page = comments.getNextComments()</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "content": "...",
      "author": {...},
      "publishedTime": "...",
      "likeCount": "...",
      "replyCount": "..."
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Transcript</strong><span>Native caption/player flow with optional legacy fallback extra</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Transcript.get(videoLink, params=None, mode=ResultMode.dict, timeout=None)</code>
        <p>Use <span class="ytsp-inline">params</span> for the desired caption language/track parameters. The optional <span class="ytsp-inline">transcript</span> extra preserves the legacy fallback path.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">transcript.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Transcript

transcript = Transcript.get(
    <span class="str">"pnxL4OOzPEc"</span>,
    params=<span class="str">"en"</span>,
)
print(transcript)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "text": "...",
      "start": "...",
      "duration": "..."
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Channel</strong><span>Channel info or playlists with explicit request type</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Channel.get(channelId, mode=ResultMode.dict, timeout=None)</code>
        <code class="ytsp-signature">Channel(channel_id, request_type=ChannelRequestType.playlists, timeout=None)</code>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">channel.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Channel, ChannelRequestType

info = Channel.get(<span class="str">"UC_x5XG1OV2P6uZZ5FSM9Ttw"</span>)

channel = Channel(
    <span class="str">"UC_x5XG1OV2P6uZZ5FSM9Ttw"</span>,
    request_type=ChannelRequestType.playlists,
)
channel.init()
channel.next()</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "id": "CHANNEL_ID",
  "title": "...",
  "description": "...",
  "thumbnails": [...],
  "playlists": [...]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Hashtag</strong><span>Hashtag content with limit, language and region controls</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">Hashtag.get(hashtag, mode=ResultMode.dict, limit=60, language="en", region="US", timeout=None)</code>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">hashtag.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> Hashtag

music = Hashtag.get(
    <span class="str">"music"</span>,
    limit=<span class="num">10</span>,
    language=<span class="str">"en"</span>,
    region=<span class="str">"US"</span>,
)
print(music)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "result": [
    {
      "type": "video | short",
      "id": "...",
      "title": "...",
      "thumbnails": [...]
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api" id="streaming">
      <summary><span class="ytsp-api-title"><strong>StreamURLFetcher</strong><span>Direct/already-signed formats, unresolved cipher reporting and PO-token handoff</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">StreamURLFetcher(proxy=None, cookies_file=None, po_token=None, visitor_data=None)</code>
        <code class="ytsp-signature">get(videoFormats_or_id, itag, po_token=None) · getAll(videoFormats_or_id, po_token=None)</code>
        <p>The fetcher does not depend on yt-dlp. Formats that still require encrypted player-JavaScript deciphering are surfaced under <span class="ytsp-inline">unresolved</span>; URLs that retain an <span class="ytsp-inline">n</span> challenge are marked throttled.</p>
        <p>PO-token generation and session-aware caching can be handled separately by <a href="https://github.com/BillaSpace/ytsp-po-token-provider"><strong>ytsp-po-token-provider ↗</strong></a>.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">stream.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> StreamURLFetcher

fetcher = StreamURLFetcher(
    po_token=<span class="str">"YOUR_PO_TOKEN"</span>,
    visitor_data=<span class="str">"YOUR_VISITOR_DATA"</span>,
)

url = fetcher.get(<span class="str">"pnxL4OOzPEc"</span>, <span class="num">18</span>)
all_formats = fetcher.getAll(<span class="str">"pnxL4OOzPEc"</span>)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">{
  "streams": [
    {
      "itag": 18,
      "url": "https://...",
      "mimeType": "...",
      "throttled": false
    }
  ],
  "unresolved": [
    {
      "itag": "...",
      "reason": "signature deciphering required"
    }
  ]
}</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Async API</strong><span>Same high-level API under youtubesearchpython.future</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <p>Search classes load the first page on the first awaited <span class="ytsp-inline">next()</span>. Content methods such as <span class="ytsp-inline">Video.getInfo</span>, <span class="ytsp-inline">Playlist.get</span>, <span class="ytsp-inline">Recommendations.get</span> and <span class="ytsp-inline">StreamURLFetcher.getAll</span> are awaitable in the future namespace.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">async_search.py</span></div><pre><code><span class="kw">import</span> asyncio
<span class="kw">from</span> youtubesearchpython.future <span class="kw">import</span> VideosSearch

<span class="kw">async def</span> main():
    search = VideosSearch(<span class="str">"Arijit Singh"</span>, limit=<span class="num">10</span>)
    first = <span class="kw">await</span> search.next()
    second = <span class="kw">await</span> search.next()
    print(first, second)

asyncio.run(main())</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">Same logical result structures as the synchronous API.
The difference is lifecycle: network operations are awaited.</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>Result modes &amp; filters</strong><span>ResultMode, SearchMode, upload date, duration, sort order and channel request types</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">ResultMode.dict · ResultMode.json</code>
        <code class="ytsp-signature">SearchMode.videos · channels · playlists · livestreams</code>
        <code class="ytsp-signature">VideoUploadDateFilter.lastHour · today · thisWeek · thisMonth · thisYear</code>
        <code class="ytsp-signature">VideoDurationFilter.short · long</code>
        <code class="ytsp-signature">VideoSortOrder.relevance · uploadDate · viewCount · rating</code>
        <code class="ytsp-signature">ChannelRequestType.info · playlists</code>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">modes.py</span></div><pre><code><span class="kw">from</span> youtubesearchpython <span class="kw">import</span> (
    ResultMode,
    SearchMode,
    VideoSortOrder,
)

<span class="cm"># Result mode is accepted by content APIs.</span>
<span class="cm"># Search/filter constants expose the preference values used by YouTube search.</span>

print(ResultMode.dict)
print(SearchMode.videos)
print(VideoSortOrder.relevance)</code></pre></div></div></details>
        <details class="ytsp-sub"><summary>Response shape</summary><div class="ytsp-sub-body"><pre class="ytsp-shape">ResultMode.dict -> Python dictionaries/lists
ResultMode.json -> JSON string output where supported</pre></div></details>
      </div>
    </details>

    <details class="ytsp-api">
      <summary><span class="ytsp-api-title"><strong>HTTP lifecycle</strong><span>Managed clients with optional explicit teardown</span></span><span class="ytsp-chevron">+</span></summary>
      <div class="ytsp-api-body">
        <code class="ytsp-signature">close_clients() · await aclose_clients()</code>
        <p>Normal sync applications require no explicit shutdown call. Async clients are owned by their event loops and close when their loop shuts down gracefully. Explicit teardown remains available for tests or unusual lifecycle control.</p>
        <details class="ytsp-sub"><summary>Example</summary><div class="ytsp-sub-body"><div class="ytsp-code"><div class="ytsp-codebar"><span class="ytsp-file">cleanup.py</span></div><pre><code><span class="cm"># Optional forced teardown only</span>
<span class="kw">from</span> youtubesearchpython <span class="kw">import</span> close_clients
close_clients()

<span class="cm"># Async:</span>
<span class="kw">from</span> youtubesearchpython.future <span class="kw">import</span> aclose_clients
<span class="kw">await</span> aclose_clients()</code></pre></div></div></details>
      </div>
    </details>

  </div>
</section>

<section class="ytsp-section">
  <div class="ytsp-section-head">
    <div>
      <h2>Designed for long-running services</h2>
      <p>Transport ownership is centralized instead of letting independent components accumulate their own client pools.</p>
    </div>
  </div>
  <div class="ytsp-grid">
    <div class="ytsp-card"><h3>Centralized transport</h3><p>One canonical HTTP layer reduces duplicate client creation and makes resource ownership predictable.</p></div>
    <div class="ytsp-card"><h3>Async lifecycle</h3><p>Async clients are associated with their owning event loop and clean up with normal loop shutdown.</p></div>
    <div class="ytsp-card"><h3>Compatibility</h3><p>Python 3.9+, runtime-tested on Python 3.13.5 and audited against Python 3.14 asyncio removals/deprecations.</p></div>
  </div>
</section>

<section class="ytsp-section" id="support">
  <div class="ytsp-section-head">
    <div>
      <h2>Support</h2>
      <p>Choose the right Telegram destination. The labels are clickable; raw URLs stay out of the interface.</p>
    </div>
  </div>
  <div class="ytsp-support">
    <a href="https://t.me/BillaCore" aria-label="Open Support Chat on Telegram">
      <span><strong>Support Chat</strong><small>Questions, setup help and troubleshooting</small></span>
      <span class="go">Open ↗</span>
    </a>
    <a href="https://t.me/BillaSpace" aria-label="Open Support Channel on Telegram">
      <span><strong>Support Channel</strong><small>Updates, releases and project announcements</small></span>
      <span class="go">Open ↗</span>
    </a>
  </div>
</section>

<footer class="ytsp-footer">
  <span>yt-search-python · maintained by BillaSpace</span>
  <span class="ytsp-footer-links">
    <a href="https://github.com/BillaSpace/yt-search-python">GitHub</a>
    <a href="https://pypi.org/project/yt-search-python/">PyPI</a>
    <a href="https://github.com/BillaSpace/ytsp-po-token-provider">PO Token Provider</a>
    <a href="https://t.me/BillaCore">Support Chat</a>
    <a href="https://t.me/BillaSpace">Support Channel</a>
  </span>
</footer>

</div>
