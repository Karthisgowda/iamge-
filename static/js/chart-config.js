/**
 * Creates a bar chart to display image recognition results
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} data - Chart data with labels and values
 */
function createResultsChart(ctx, data) {
    // Create gradient for bars
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(13, 110, 253, 0.8)');
    gradient.addColorStop(1, 'rgba(13, 110, 253, 0.2)');
    
    // Create the chart
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Confidence Score',
                data: data.data,
                backgroundColor: gradient,
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1,
                borderRadius: 5,
                hoverBackgroundColor: 'rgba(13, 110, 253, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return `Confidence: ${context.raw.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Confidence (%)',
                        color: '#adb5bd'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    // Add animation once chart is rendered
    chart.options.animation = {
        onComplete: function() {
            const chartArea = chart.chartArea;
            ctx.save();
            ctx.fillStyle = 'rgba(13, 110, 253, 0.1)';
            ctx.fillRect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);
            ctx.restore();
        }
    };
}

/**
 * Creates a doughnut chart to visualize distribution of tags
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} data - Chart data with labels and values
 */
function createDoughnutChart(ctx, data) {
    // Generate colors for segments
    const colors = generateColorPalette(data.labels.length);
    
    // Create the chart
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: colors.background,
                borderColor: colors.border,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                animateRotate: true,
                animateScale: true
            },
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${value.toFixed(2)}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Generates a color palette for charts
 * @param {number} count - Number of colors needed
 * @returns {Object} Object with background and border color arrays
 */
function generateColorPalette(count) {
    const backgroundColors = [];
    const borderColors = [];
    
    // Base colors to interpolate between
    const baseColors = [
        [13, 110, 253],   // Primary blue
        [25, 135, 84],    // Success green
        [255, 193, 7],    // Warning yellow
        [220, 53, 69],    // Danger red
        [13, 202, 240],   // Info cyan
        [108, 117, 125],  // Secondary gray
        [173, 181, 189]   // Light gray
    ];
    
    // Generate additional colors if needed
    for (let i = 0; i < count; i++) {
        let colorIndex = i % baseColors.length;
        let opacity = 0.7;
        
        // Get base color
        let [r, g, b] = baseColors[colorIndex];
        
        // Add variation for repeated colors
        if (i >= baseColors.length) {
            const variation = Math.floor(i / baseColors.length) * 30;
            r = Math.max(0, Math.min(255, r + variation));
            g = Math.max(0, Math.min(255, g - variation));
            b = Math.max(0, Math.min(255, b + variation));
        }
        
        backgroundColors.push(`rgba(${r}, ${g}, ${b}, ${opacity})`);
        borderColors.push(`rgba(${r}, ${g}, ${b}, 1)`);
    }
    
    return {
        background: backgroundColors,
        border: borderColors
    };
}
