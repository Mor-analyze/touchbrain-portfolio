function openModal(id) {
    document.getElementById(id).classList.add('open');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}
window.addEventListener('click', function(e) {
    document.querySelectorAll('.modal-overlay.open').forEach(function(m) {
        if (e.target === m) m.classList.remove('open');
    });
});

// ── Sortable tables ──────────────────────────────
function initSortableTables() {
    document.querySelectorAll('table').forEach(function(table) {
        var headers = table.querySelectorAll('th');
        headers.forEach(function(th, colIndex) {
            // Skip action columns (last column with buttons)
            if (th.textContent.trim() === '') return;

            th.style.cursor = 'pointer';
            th.style.userSelect = 'none';
            th.setAttribute('title', 'Click to sort');

            // Add sort indicator
            var indicator = document.createElement('span');
            indicator.style.marginLeft = '4px';
            indicator.style.opacity = '0.4';
            indicator.style.fontSize = '10px';
            indicator.textContent = '⇅';
            th.appendChild(indicator);

            var ascending = true;

            th.addEventListener('click', function() {
                var tbody = table.querySelector('tbody');
                var rows = Array.from(tbody.querySelectorAll('tr'));

                // Reset all indicators
                headers.forEach(function(h) {
                    var ind = h.querySelector('span');
                    if (ind) { ind.textContent = '⇅'; ind.style.opacity = '0.4'; }
                });

                // Sort rows
                rows.sort(function(a, b) {
                    var aCell = a.querySelectorAll('td')[colIndex];
                    var bCell = b.querySelectorAll('td')[colIndex];
                    if (!aCell || !bCell) return 0;
                    var aText = aCell.textContent.trim().toLowerCase();
                    var bText = bCell.textContent.trim().toLowerCase();

                    // Try numeric sort first
                    var aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
                    var bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return ascending ? aNum - bNum : bNum - aNum;
                    }

                    // Date sort
                    var aDate = new Date(aText);
                    var bDate = new Date(bText);
                    if (!isNaN(aDate) && !isNaN(bDate)) {
                        return ascending ? aDate - bDate : bDate - aDate;
                    }

                    // Text sort
                    if (aText < bText) return ascending ? -1 : 1;
                    if (aText > bText) return ascending ? 1 : -1;
                    return 0;
                });

                // Update indicator
                var ind = th.querySelector('span');
                if (ind) {
                    ind.textContent = ascending ? '↑' : '↓';
                    ind.style.opacity = '1';
                    ind.style.color = '#C9A84C';
                }

                // Re-append sorted rows
                rows.forEach(function(row) { tbody.appendChild(row); });
                ascending = !ascending;
            });
        });
    });
}

// Run on page load
document.addEventListener('DOMContentLoaded', initSortableTables);