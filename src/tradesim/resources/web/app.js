const $ = (id) => document.getElementById(id);
let latest = null;
const money = (value) => `$${Number(value || 0).toFixed(2)}`;

async function initialize() {
  const state = await fetch('/api/state').then((r) => r.json());
  $('ticker').innerHTML = state.tickers.map((ticker) => `<option>${ticker}</option>`).join('');
  $('strategy').insertAdjacentHTML('beforeend', state.strategies.map((strategy) => `<option value="${strategy}">${strategy[0].toUpperCase()}${strategy.slice(1)}</option>`).join(''));
  $('run').addEventListener('click', runBacktest);
  await runBacktest();
}

async function runBacktest() {
  const button = $('run');
  button.disabled = true;
  button.textContent = 'Running…';
  try {
    const response = await fetch('/api/backtest', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({
      ticker: $('ticker').value, strategy: $('strategy').value,
      maxTransactions: Number($('maxTransactions').value), transactionFee: Number($('transactionFee').value),
      cooldownDays: Number($('cooldownDays').value)
    })});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Backtest failed');
    latest = data;
    render(data);
  } catch (error) {
    $('runCount').textContent = error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = 'Run Backtest <span>→</span>';
  }
}

function render(data) {
  const results = data.results || [];
  const healthy = results.length > 0 && results.every((result) => result.status === 'valid');
  const incident = $('incident');
  incident.classList.toggle('healthy', healthy);
  incident.innerHTML = healthy
    ? '<b>✓ Backtesting Engine Healthy</b><span>All returned execution policies produced valid results.</span>'
    : '<b>⚠ Production Analytics Anomaly Detected</b><span>The backtesting service is reporting inconsistent results for one or more execution policies. Inspect the runs before trusting the analytics.</span>';
  const selected = results[0];
  const telemetry = selected?.telemetry || {};
  $('profit').textContent = money(telemetry.gross_profit);
  $('tradesCount').textContent = selected?.transaction_count ?? '—';
  $('drawdown').textContent = `${((selected?.max_drawdown || 0) * 100).toFixed(2)}%`;
  $('netProfit').textContent = money(selected?.total_profit);
  $('chartTitle').textContent = `${data.ticker} · Closing price`;
  $('runCount').textContent = `${results.length} polic${results.length === 1 ? 'y' : 'ies'} · ${data.prices.length} days`;
  renderChart(data.prices, results);
  const byStrategy = new Map(results.map((result) => [result.strategy, result]));
  const entries = results.flatMap((result) => result.transactions.map((trade) => ({...trade, strategy: result.strategy, status: result.status})));
  entries.sort((a, b) => a.day - b.day || a.strategy.localeCompare(b.strategy));
  $('ledger').innerHTML = entries.length ? entries.map((trade) => `<tr>
    <td>${trade.strategy}</td><td class="${trade.action === 'BUY' ? 'buy-text' : 'sell-text'}">${trade.action}</td>
    <td class="mono">${trade.day + 1}</td><td class="mono">${money(trade.price)}</td><td class="mono">${money(trade.fee)}</td>
    <td class="mono ${trade.realized_profit >= 0 ? 'positive' : 'negative'}">${trade.action === 'SELL' ? money(trade.realized_profit) : '—'}</td>
    <td class="status ${trade.status}">${trade.status}</td></tr>`).join('') : '<tr><td colspan="7" class="empty">No executions for this policy.</td></tr>';
}

function renderChart(prices, results) {
  const svg = $('chart');
  if (!prices.length) { svg.innerHTML = ''; return; }
  const W = 900, H = 300, left = 48, right = 18, top = 16, bottom = 30;
  const min = Math.min(...prices), max = Math.max(...prices), span = max - min || 1;
  const x = (i) => left + i * (W - left - right) / Math.max(prices.length - 1, 1);
  const y = (price) => top + (max - price) * (H - top - bottom) / span;
  const points = prices.map((price, i) => `${x(i).toFixed(1)},${y(price).toFixed(1)}`).join(' ');
  const fillPoints = results.flatMap((result) => result.transactions.map((trade) => ({...trade, strategy: result.strategy})));
  const grid = Array.from({length: 4}, (_, i) => {
    const val = max - span * i / 3, yy = y(val);
    return `<line class="grid-line" x1="${left}" y1="${yy}" x2="${W - right}" y2="${yy}"/><text class="axis-label" x="2" y="${yy + 3}">$${val.toFixed(0)}</text>`;
  }).join('');
  const dots = fillPoints.map((trade) => `<circle class="${trade.action === 'BUY' ? 'buy-point' : 'sell-point'}" cx="${x(trade.day)}" cy="${y(trade.price)}" r="5"><title>${trade.strategy} ${trade.action} · Day ${trade.day + 1} · ${money(trade.price)}</title></circle>`).join('');
  const dateMarks = [0, Math.floor((prices.length - 1) / 2), prices.length - 1].map((i) => `<text class="axis-label" text-anchor="${i === 0 ? 'start' : i === prices.length - 1 ? 'end' : 'middle'}" x="${x(i)}" y="${H - 5}">Day ${i + 1}</text>`).join('');
  svg.innerHTML = `<defs><linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#53d6a1" stop-opacity=".2"/><stop offset="1" stop-color="#53d6a1" stop-opacity="0"/></linearGradient></defs>${grid}<polygon class="chart-area" points="${left},${H - bottom} ${points} ${x(prices.length - 1)},${H - bottom}"/><polyline class="chart-line" points="${points}"/>${dots}${dateMarks}`;
}

initialize().catch((error) => { $('runCount').textContent = error.message; });
