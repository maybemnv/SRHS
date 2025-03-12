// Initialize charts only if they exist on the page
document.addEventListener('DOMContentLoaded', function() {
    // Record Types Distribution Chart
    const recordTypesChart = document.getElementById('recordTypesChart');
    if (recordTypesChart) {
        const recordTypesCtx = recordTypesChart.getContext('2d');
        new Chart(recordTypesCtx, {
            type: 'doughnut',
            data: {
                labels: ['General', 'Lab Results', 'Prescriptions', 'Diagnosis'],
                datasets: [{
                    data: [4, 3, 2, 1],
                    backgroundColor: [
                        '#005EB8',
                        '#28A745',
                        '#FFC107',
                        '#DC3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Records Timeline Chart
    const recordsTimelineChart = document.getElementById('recordsTimelineChart');
    if (recordsTimelineChart) {
        const timelineCtx = recordsTimelineChart.getContext('2d');
        new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Records Added',
                    data: [2, 5, 3, 4, 6, 3],
                    borderColor: '#005EB8',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
});

// Form Validation
function validateForm() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});
