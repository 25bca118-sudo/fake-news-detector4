let verdictChartInstance = null;
let categoryChartInstance = null;

async function loadDashboard() {
    try {
        const res = await fetch('/api/analytics');
        const json = await res.json();
        if (!json.success) return;
        const data = json.data;

        // Top KPIs
        document.getElementById('dash-total').innerText = data.total_analyses;
        document.getElementById('dash-genuine').innerText = data.genuine_count;
        document.getElementById('dash-fake').innerText = data.fake_count;
        document.getElementById('dash-avg').innerText = `${data.avg_credibility_score} / 100`;

        // Verdict Donut Chart
        const vCtx = document.getElementById('verdictChart').getContext('2d');
        if (verdictChartInstance) verdictChartInstance.destroy();
        verdictChartInstance = new Chart(vCtx, {
            type: 'doughnut',
            data: {
                labels: ['Likely Genuine', 'Potentially Fake', 'Inconclusive'],
                datasets: [{
                    data: [data.genuine_count, data.fake_count, data.inconclusive_count],
                    backgroundColor: ['#10b981', '#f43f5e', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8' } }
                }
            }
        });

        // Category Bar Chart
        const cCtx = document.getElementById('categoryChart').getContext('2d');
        if (categoryChartInstance) categoryChartInstance.destroy();
        const catLabels = data.category_distribution.map(c => c.category);
        const catCounts = data.category_distribution.map(c => c.count);

        categoryChartInstance = new Chart(cCtx, {
            type: 'bar',
            data: {
                labels: catLabels,
                datasets: [{
                    label: 'Articles Analyzed',
                    data: catCounts,
                    backgroundColor: '#6366f1',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#1f293d' } }
                }
            }
        });

        // Render Benchmarks Table
        const tbody = document.getElementById('benchmark-tbody');
        tbody.innerHTML = '';
        (data.benchmarks || []).forEach(b => {
            const tr = document.createElement('tr');
            let arch = 'Traditional Statistical ML';
            if (b.model_name.includes('DistilBERT')) arch = 'Contextual Semantic Transformer';
            if (b.model_name.includes('Forest')) arch = 'Decision Tree Ensemble';

            tr.innerHTML = `
                <td><b>${b.model_name}</b></td>
                <td><span class="chip">${arch}</span></td>
                <td><b class="text-emerald">${(b.accuracy * 100).toFixed(1)}%</b></td>
                <td>${(b.precision_score * 100).toFixed(1)}%</td>
                <td>${(b.recall_score * 100).toFixed(1)}%</td>
                <td><b class="text-indigo">${(b.f1_score * 100).toFixed(1)}%</b></td>
                <td><span class="verdict-pill badge-genuine">Active In Pipeline</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Dashboard load failed:", err);
    }
}

document.addEventListener('DOMContentLoaded', loadDashboard);
