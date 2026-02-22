import streamlit.components.v1 as components

from styles import ABOUT_CSS


def render_about_page():
    about_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{ABOUT_CSS}</style>
</head>
<body>
<div class="page">

  <p class="eyebrow">Hacklytics 2026 &nbsp;·&nbsp; Databricks &times; United Nations</p>
  <h1>H2C2</h1>
  <p class="subtitle">Humanitarian Health Command Center</p>
  <hr class="rule" />

  <p class="lead">
    Every year, billions of dollars in humanitarian aid are allocated without a clear picture of
    where the need is greatest. Funding reaches some regions generously while others &mdash;
    equally devastated &mdash; are barely touched. <b>H2C2 exists to close that gap.</b>
  </p>

  <p class="lead">
    We join the UN&rsquo;s Humanitarian Needs Overview (HNO) and Humanitarian Response Plan (HRP)
    datasets into a single live intelligence layer. The result is a <b>Health Vulnerability Index</b>
    &mdash; a real-time score that shows, for every crisis region on Earth, how far medical funding
    lags behind the severity of the situation on the ground.
  </p>

  <p class="lead">
    From that foundation we built three tools: an interactive 3D globe that makes the data
    impossible to ignore, a natural-language interface so any official can ask a question
    without writing a single line of SQL, and a machine-learning engine that flags
    inefficient projects and forecasts where the next health desert will emerge
    before it becomes a headline.
  </p>

  <div class="pillars">
    <div class="pillar">
      <p class="pillar-icon">01 &mdash; The Map</p>
      <h3>Live Crisis Globe</h3>
      <p>A 3D rotating Earth colored by vulnerability. Zoom from a global view down to
         individual states and districts. Every pulse on the map is a real crisis, ranked
         by need vs. funding.</p>
    </div>
    <div class="pillar">
      <p class="pillar-icon">02 &mdash; The Genie</p>
      <h3>Ask in Plain Language</h3>
      <p>Powered by Databricks AI/BI Genie. Type a question &mdash; &ldquo;Why is South Sudan
         critical?&rdquo; or &ldquo;Find projects over $500 per person&rdquo; &mdash; and the
         system writes the SQL and returns the answer instantly.</p>
    </div>
    <div class="pillar">
      <p class="pillar-icon">03 &mdash; The Engine</p>
      <h3>Forecast &amp; Benchmark</h3>
      <p>An ML layer that predicts funding gaps six months out and uses KNN to surface
         peer projects that are doing more with less &mdash; giving auditors a concrete
         benchmark to act on today.</p>
    </div>
  </div>

  <p class="stack-label">Built with</p>
  <div class="stack-row">
    <span class="stack-tag">Databricks</span>
    <span class="stack-tag">Delta Lake</span>
    <span class="stack-tag">Unity Catalog</span>
    <span class="stack-tag">AI/BI Genie</span>
    <span class="stack-tag">Spark MLlib</span>
    <span class="stack-tag">Streamlit</span>
    <span class="stack-tag">globe.gl</span>
    <span class="stack-tag">UN HDX Data</span>
  </div>

</div>
</body>
</html>"""
    components.html(about_html, height=820, scrolling=True)
