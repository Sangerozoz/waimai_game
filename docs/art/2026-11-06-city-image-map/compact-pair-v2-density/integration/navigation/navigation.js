'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const svg = $('map');
  const NS = 'http://www.w3.org/2000/svg';
  const state = {ready: false, graph: null, start: null, end: null, route: null,
    playing: false, traveled: 0, position: null, offroadRejections: 0,
    lastTimestamp: 0, message: '', selectedEdgeIds: []};
  const distance = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  const length = points => points.slice(1).reduce((sum, p, i) => sum + distance(points[i], p), 0);
  const pathData = points => points.map((p, i) => `${i ? 'L' : 'M'}${p[0]},${p[1]}`).join(' ');
  const close = (a, b) => distance(a, b) < 1e-6;

  function status(message, error = false) {
    state.message = message;
    $('status').textContent = message;
    $('status').classList.toggle('error', error);
  }

  function atDistance(points, requested) {
    let remaining = Math.max(0, Math.min(length(points), requested));
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1], b = points[i], segment = distance(a, b);
      if (remaining <= segment && segment > 0) {
        const t = remaining / segment;
        return [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])];
      }
      remaining -= segment;
    }
    return points[points.length - 1].slice();
  }

  function slicePolyline(points, from, to) {
    if (from > to) return slicePolyline(points, to, from).reverse();
    const result = [atDistance(points, from)];
    let covered = 0;
    for (let i = 1; i < points.length; i++) {
      covered += distance(points[i - 1], points[i]);
      if (covered > from + 1e-6 && covered < to - 1e-6) result.push(points[i].slice());
    }
    const last = atDistance(points, to);
    if (!close(result[result.length - 1], last)) result.push(last);
    return result;
  }

  function nearestRoad(p) {
    let best = null;
    for (const edge of state.graph.edges) {
      let covered = 0;
      for (let i = 1; i < edge.points.length; i++) {
        const a = edge.points[i - 1], b = edge.points[i];
        const dx = b[0] - a[0], dy = b[1] - a[1], squared = dx * dx + dy * dy;
        if (!squared) continue;
        const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / squared));
        const point = [a[0] + dx * t, a[1] + dy * t];
        const gap = distance(p, point);
        if (!best || gap < best.gap) best = {edgeId: edge.id, point, gap,
          along: covered + Math.sqrt(squared) * t};
        covered += Math.sqrt(squared);
      }
    }
    return best;
  }

  function solve(start, end) {
    const adjacency = new Map(state.graph.nodes.map(n => [String(n.id), []]));
    adjacency.set('S', []); adjacency.set('T', []);
    function add(a, b, points, edgeId) {
      const cost = length(points);
      adjacency.get(String(a)).push({to: String(b), points, cost, edgeId});
      adjacency.get(String(b)).push({to: String(a), points: points.slice().reverse(), cost, edgeId});
    }
    for (const edge of state.graph.edges) add(edge.from, edge.to, edge.points, edge.id);
    function attach(key, snap) {
      const edge = state.graph.edges.find(e => e.id === snap.edgeId);
      const total = length(edge.points);
      add(edge.from, key, slicePolyline(edge.points, 0, snap.along), edge.id);
      add(key, edge.to, slicePolyline(edge.points, snap.along, total), edge.id);
    }
    attach('S', start); attach('T', end);
    if (start.edgeId === end.edgeId) {
      const edge = state.graph.edges.find(e => e.id === start.edgeId);
      add('S', 'T', slicePolyline(edge.points, start.along, end.along), edge.id);
    }
    const queue = [{id: 'S', cost: 0}], costs = new Map([['S', 0]]), previous = new Map(), settled = new Set();
    while (queue.length) {
      queue.sort((a, b) => a.cost - b.cost);
      const current = queue.shift();
      if (settled.has(current.id)) continue;
      settled.add(current.id);
      if (current.id === 'T') break;
      for (const arc of adjacency.get(current.id)) {
        const candidate = current.cost + arc.cost;
        if (candidate + 1e-8 < (costs.get(arc.to) ?? Infinity)) {
          costs.set(arc.to, candidate); previous.set(arc.to, {from: current.id, arc});
          queue.push({id: arc.to, cost: candidate});
        }
      }
    }
    if (!costs.has('T')) return null;
    const arcs = [];
    let cursor = 'T';
    while (cursor !== 'S') {
      const item = previous.get(cursor);
      if (!item) return null;
      arcs.push(item.arc); cursor = item.from;
    }
    arcs.reverse();
    const points = [], edgeIds = [];
    for (const arc of arcs) {
      for (const p of arc.points) if (!points.length || !close(points[points.length - 1], p)) points.push(p.slice());
      if (edgeIds[edgeIds.length - 1] !== arc.edgeId) edgeIds.push(arc.edgeId);
    }
    return {points, length: costs.get('T'), edgeIds};
  }

  function element(tag, attrs, text) {
    const node = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, String(value));
    if (text) node.textContent = text;
    return node;
  }

  function paintPoints() {
    $('points').replaceChildren();
    for (const [snap, name, color] of [[state.start, 'A', '#35c981'], [state.end, 'B', '#ff6f64']]) {
      if (!snap) continue;
      const [x, y] = snap.point;
      $('points').append(element('circle', {cx: x, cy: y, r: 12, fill: color, class: 'point'}));
      $('points').append(element('text', {x: x + 18, y: y - 17, class: 'point-label'}, name));
    }
  }

  function paintTraveler() {
    const marker = $('traveler');
    if (!state.position) { marker.setAttribute('visibility', 'hidden'); return; }
    marker.setAttribute('visibility', 'visible');
    marker.setAttribute('cx', state.position[0]); marker.setAttribute('cy', state.position[1]);
  }

  function stop() { state.playing = false; $('play').textContent = '播放导航'; }

  function updateRoute() {
    stop(); state.traveled = 0;
    state.route = state.start && state.end ? solve(state.start, state.end) : null;
    state.selectedEdgeIds = state.route ? state.route.edgeIds.slice() : [];
    $('route').setAttribute('d', state.route ? pathData(state.route.points) : '');
    state.position = state.start ? state.start.point.slice() : null;
    $('play').disabled = !state.route || state.route.length < 1e-6;
    paintPoints(); paintTraveler();
    if (state.start && state.end) status(state.route ?
      `已连通 A → B：${Math.round(state.route.length)} 像素。播放后蓝色标记沿绿色路线移动。` : '两个位置无法连通。', !state.route);
    else status(state.start ? '起点 A 已选，请再点道路上的终点。' : '请依次在确认道路上点起点和终点，或点击“示例”。');
  }

  function setDemo() {
    if (!state.ready) return;
    state.start = nearestRoad(state.graph.example.startPixel); state.end = nearestRoad(state.graph.example.endPixel);
    updateRoute();
  }

  svg.addEventListener('click', event => {
    if (!state.ready) return;
    const matrix = svg.getScreenCTM();
    if (!matrix) return;
    const point = svg.createSVGPoint(); point.x = event.clientX; point.y = event.clientY;
    const pixel = point.matrixTransform(matrix.inverse());
    const snap = nearestRoad([pixel.x, pixel.y]);
    if (!snap || snap.gap > 36) {
      state.offroadRejections++;
      status('这里不在本次按图描出的路网上；请点道路中心附近。', true);
      return;
    }
    if (!state.start || state.end) { state.start = snap; state.end = null; }
    else state.end = snap;
    updateRoute();
  });

  $('demo').addEventListener('click', setDemo);
  $('reset').addEventListener('click', () => { state.start = null; state.end = null; updateRoute(); });
  $('play').addEventListener('click', () => {
    if (!state.route || state.route.length < 1e-6) return;
    if (state.playing) { stop(); status('已暂停；再次点击可继续。'); }
    else {
      if (state.traveled >= state.route.length) state.traveled = 0;
      state.playing = true; state.lastTimestamp = performance.now();
      $('play').textContent = '暂停导航'; status('导航播放中：蓝色标记只沿确认路线移动。');
    }
  });
  $('showNetwork').addEventListener('change', () => $('network').setAttribute('visibility', $('showNetwork').checked ? 'visible' : 'hidden'));

  function tick(now) {
    if (state.playing && state.route) {
      const dt = Math.min(.1, Math.max(0, (now - state.lastTimestamp) / 1000));
      state.traveled = Math.min(state.route.length, state.traveled + dt * 110 * Number($('speed').value));
      state.position = atDistance(state.route.points, state.traveled);
      paintTraveler();
      if (state.traveled >= state.route.length) { stop(); status('已沿路线到达 B。可重新选点或再次播放。'); }
    }
    state.lastTimestamp = now; requestAnimationFrame(tick);
  }

  globalThis.__navDemo = {getState: () => ({ready: state.ready, playing: state.playing,
    traveled: state.traveled, position: state.position ? state.position.slice() : null,
    start: state.start ? structuredClone(state.start) : null, end: state.end ? structuredClone(state.end) : null,
    route: state.route ? structuredClone(state.route) : null, offroadRejections: state.offroadRejections,
    nodeCount: state.graph?.nodes.length ?? 0, edgeCount: state.graph?.edges.length ?? 0,
    components: state.graph?.connectedComponents.length ?? 0, message: state.message,
    loadedImages: state.loadedImages ?? [], graphSourceSHA256: state.graph?.sourceTiledSHA256 ?? null})};

  async function initialize() {
    const graph = globalThis.__embeddedGraph || await (async () => { const r = await fetch('graph.json', {cache:'no-store'}); if (!r.ok) throw new Error('graph HTTP '+r.status); return r.json(); })();
    if (graph.connectedComponents.length !== 1 || graph.edges.some(e => e.name.includes('独立车道'))) throw new Error('路网未正确排除错误车道');
    // SVGImageElement has no HTMLImageElement.complete/naturalWidth contract.
    // Decode the same resource explicitly, even if its SVG load already fired.
    state.loadedImages = await Promise.all(graph.images.map(async spec => {
      const el = $(spec.elementId), href = el.getAttribute('href');
      const decoded = new Image(); decoded.src = href; await decoded.decode();
      if (decoded.naturalWidth !== spec.size[0] || decoded.naturalHeight !== spec.size[1]) throw new Error('区域图片尺寸不一致');
      const bytes = await (await fetch(href)).arrayBuffer();
      const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(v => v.toString(16).padStart(2,'0')).join('');
      if (digest !== spec.sha256) throw new Error('实际加载图片SHA不匹配');
      const rect = el.getBoundingClientRect(); if (!rect.width || !rect.height) throw new Error('区域图片未显示');
      return {elementId:spec.elementId, sha256:digest, nativeSourceSHA256:spec.nativeSourceSHA256, decodedSize:[decoded.naturalWidth,decoded.naturalHeight], displayed:true};
    }));
    state.graph = graph;
    for (const edge of graph.edges) $('network').append(element('path', {d: pathData(edge.points)}));
    state.ready = true;
    $('stats').textContent = `${graph.nodes.length} 节点 · ${graph.edges.length} 路段 · 1 个连通路网`;
    setDemo(); requestAnimationFrame(tick);
  }
  initialize().catch(error => status(`预览未就绪：${error.message}`, true));
})();
