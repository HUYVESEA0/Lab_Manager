document.addEventListener('DOMContentLoaded', function() {
    // Initialize sortable table headers
    const sortableTables = document.querySelectorAll('.admin-table');

    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th.sortable');

        headers.forEach(header => {
            header.addEventListener('click', function() {
                const columnIndex = Array.from(header.parentNode.children).indexOf(header);
                const isAsc = this.classList.contains('asc');

                // Update header classes
                headers.forEach(h => {
                    h.classList.remove('asc', 'desc');
                });

                this.classList.add(isAsc ? 'desc' : 'asc');

                // Sort table
                sortTable(table, columnIndex, !isAsc);
            });
        });
    });

    // Function to sort table
    function sortTable(table, columnIndex, asc) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));        // Sort the rows
        rows.sort((a, b) => {
            const cellA = a.querySelectorAll('td')[columnIndex].textContent.trim();
            const cellB = b.querySelectorAll('td')[columnIndex].textContent.trim();

            return asc
                ? cellA.localeCompare(cellB, undefined, {numeric: true})
                : cellB.localeCompare(cellA, undefined, {numeric: true});
        });

        // Remove existing rows
        while (tbody.firstChild) {
            tbody.removeChild(tbody.firstChild);
        }

        // Add sorted rows
        rows.forEach(row => {
            tbody.appendChild(row);
        });
    }
});
