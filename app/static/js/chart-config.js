/**
 * ONDC Seller App - Chart Configurations
 * 
 * This file contains functions to initialize and configure charts for the dashboard
 * using Chart.js library.
 */

// Colors for charts
const chartColors = {
  primary: '#3B82F6',
  primaryLight: 'rgba(59, 130, 246, 0.5)',
  primaryLighter: 'rgba(59, 130, 246, 0.1)',
  secondary: '#10B981',
  secondaryLight: 'rgba(16, 185, 129, 0.5)',
  accent: '#F59E0B',
  accentLight: 'rgba(245, 158, 11, 0.5)',
  error: '#EF4444',
  errorLight: 'rgba(239, 68, 68, 0.5)',
  gray: '#9CA3AF',
  grayLight: 'rgba(156, 163, 175, 0.5)'
};

// Common chart options
const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 1000,
    easing: 'easeOutQuart'
  },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        boxWidth: 6,
        font: {
          family: "'Open Sans', sans-serif",
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      titleFont: {
        family: "'Open Sans', sans-serif",
        size: 13
      },
      bodyFont: {
        family: "'Open Sans', sans-serif",
        size: 12
      },
      padding: 10,
      cornerRadius: 4,
      boxPadding: 4
    }
  },
  layout: {
    padding: {
      top: 10,
      right: 16,
      bottom: 10,
      left: 10
    }
  }
};

/**
 * Initialize the Daily Sales Chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} data - The daily sales data
 */
function initDailySalesChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const labels = data.map(item => item.date);
  const values = data.map(item => item.amount);
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Daily Sales',
        data: values,
        backgroundColor: chartColors.primaryLight,
        borderColor: chartColors.primary,
        borderWidth: 2,
        pointBackgroundColor: chartColors.primary,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      ...commonOptions,
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: function(value) {
              return '₹' + value.toLocaleString('en-IN');
            }
          }
        }
      },
      plugins: {
        ...commonOptions.plugins,
        tooltip: {
          ...commonOptions.plugins.tooltip,
          callbacks: {
            label: function(context) {
              return 'Sales: ₹' + context.parsed.y.toLocaleString('en-IN');
            }
          }
        }
      }
    }
  });
}

/**
 * Initialize the Weekly Sales Chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} data - The weekly sales data
 */
function initWeeklySalesChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const labels = data.map(item => item.week);
  const values = data.map(item => item.amount);
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Weekly Sales',
        data: values,
        backgroundColor: chartColors.primaryLight,
        borderColor: chartColors.primary,
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      ...commonOptions,
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: function(value) {
              return '₹' + value.toLocaleString('en-IN');
            }
          }
        }
      },
      plugins: {
        ...commonOptions.plugins,
        tooltip: {
          ...commonOptions.plugins.tooltip,
          callbacks: {
            label: function(context) {
              return 'Sales: ₹' + context.parsed.y.toLocaleString('en-IN');
            }
          }
        }
      }
    }
  });
}

/**
 * Initialize the Monthly Sales Chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} data - The monthly sales data
 */
function initMonthlySalesChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const labels = data.map(item => item.month);
  const values = data.map(item => item.amount);
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Monthly Sales',
        data: values,
        backgroundColor: 'transparent',
        borderColor: chartColors.secondary,
        borderWidth: 3,
        pointBackgroundColor: chartColors.secondary,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4
      }]
    },
    options: {
      ...commonOptions,
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: function(value) {
              return '₹' + value.toLocaleString('en-IN');
            }
          }
        }
      },
      plugins: {
        ...commonOptions.plugins,
        tooltip: {
          ...commonOptions.plugins.tooltip,
          callbacks: {
            label: function(context) {
              return 'Sales: ₹' + context.parsed.y.toLocaleString('en-IN');
            }
          }
        }
      }
    }
  });
}

/**
 * Initialize the Order Status Distribution Chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - The order status distribution data
 */
function initOrderStatusChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(data),
      datasets: [{
        data: Object.values(data),
        backgroundColor: [
          chartColors.primaryLight,
          chartColors.accentLight,
          chartColors.secondaryLight,
          chartColors.errorLight,
          chartColors.grayLight
        ],
        borderColor: [
          chartColors.primary,
          chartColors.accent,
          chartColors.secondary,
          chartColors.error,
          chartColors.gray
        ],
        borderWidth: 1
      }]
    },
    options: {
      ...commonOptions,
      cutout: '70%',
      plugins: {
        ...commonOptions.plugins,
        tooltip: {
          ...commonOptions.plugins.tooltip,
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed || 0;
              const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
              const percentage = Math.round((value / total) * 100);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

/**
 * Initialize the Top Products Chart
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} data - The top products data
 */
function initTopProductsChart(canvasId, data) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  
  const labels = data.map(item => item.name);
  const values = data.map(item => item.sales);
  
  new Chart(ctx, {
    type: 'horizontalBar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Sales Amount',
        data: values,
        backgroundColor: chartColors.primaryLight,
        borderColor: chartColors.primary,
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      ...commonOptions,
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            callback: function(value) {
              return '₹' + value.toLocaleString('en-IN');
            }
          }
        },
        y: {
          grid: {
            display: false
          }
        }
      },
      plugins: {
        ...commonOptions.plugins,
        tooltip: {
          ...commonOptions.plugins.tooltip,
          callbacks: {
            label: function(context) {
              return 'Sales: ₹' + context.parsed.x.toLocaleString('en-IN');
            }
          }
        }
      }
    }
  });
}

// Export functions to make them available globally
window.initDailySalesChart = initDailySalesChart;
window.initWeeklySalesChart = initWeeklySalesChart;
window.initMonthlySalesChart = initMonthlySalesChart;
window.initOrderStatusChart = initOrderStatusChart;
window.initTopProductsChart = initTopProductsChart;
