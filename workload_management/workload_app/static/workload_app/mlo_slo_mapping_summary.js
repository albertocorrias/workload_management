

var strengths_results = JSON.parse(document.getElementById('big_mlo_slo_table_totals_strengths').textContent);
var n_mlo_results = JSON.parse(document.getElementById('big_mlo_slo_table_totals_n_mlo').textContent);
var slo_labels = JSON.parse(document.getElementById('slo_identifiers').textContent);

var bar_background_colors = ['rgba(0, 0, 71, 0.7)',
                             'rgba(0, 0, 71, 0.7)',
                             'rgba(0, 0, 71, 0.7)',
                             'rgba(0, 0, 71, 0.7)',
                             'rgba(0, 0, 71, 0.7)',
                             'rgba(0, 0, 71, 0.7)', ]
var bar_background_colors_2 = ['rgba(91, 60, 71, 0.7)',
                             'rgba(91, 60, 71, 0.7)',
                             'rgba(91, 60, 71, 0.7)',
                             'rgba(91, 60, 71, 0.7)',
                             'rgba(91, 60, 71, 0.7)',
                             'rgba(91, 60, 71, 0.7)', ]
const data = {
    labels: slo_labels,
    
    datasets: [{
        data: strengths_results,
        label: 'Overall mapping strength',
        backgroundColor: bar_background_colors,
        yAxisID: 'y',
    }, 
    {
        data: n_mlo_results,
        label: 'Overall # of MLOs',
        backgroundColor: bar_background_colors_2,
        yAxisID: 'y2',
    }, 

]
};

const config = {
    type: 'bar',
    data: data,
    options: {

    scales: {
        x:{
            title:{
                text: 'SLO',
                display: true,
                font: {size: 17}
            }
        },
        y: {
            beginAtZero: true,
            title:{
                display: true,
                text:'Overall mapping strength',
                color:bar_background_colors[0],
                font: {size: 17}
            },
            ticks:{
                color:bar_background_colors[0],
            },
            position: 'left',
        },
        y2: {
            beginAtZero: true,
            title:{
                display: true,
                text:'Overall # MLOs',
                color:bar_background_colors_2[0],
                font: {size: 17}
            },
            position: 'right',
            ticks:{
                color:bar_background_colors_2[0],
            },
            grid: {
                drawOnChartArea: false, // only want the grid lines for one axis to show up
              },
        }
    },
    plugins: {
        legend: {
            display: true,
        },
    }
    },
};

let element_id =  "mlo_slo_summary_charts";
const myChart = new Chart(
    document.getElementById(element_id),
    config
    );
