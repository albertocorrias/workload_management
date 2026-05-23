
var all_slo_plot_data = JSON.parse(document.getElementById("all_slo_data_for_plot").textContent);
var all_slo_IDs = JSON.parse(document.getElementById("all_slo_ids").textContent);

for (let i = 0; i < all_slo_IDs.length; i++) {

    let index = String(all_slo_IDs[i]);
    var mlo_direct_measures = all_slo_plot_data[i][1];
    var mlo_survey_measures = all_slo_plot_data[i][2];
    var slo_survey_measures = all_slo_plot_data[i][3];
    var label_years = all_slo_plot_data[i][0];

    const data = {
      labels: label_years,
      datasets: [{
        label: 'CLO direct measures',
        data: mlo_direct_measures,
        fill: false,
        borderColor: 'rgba(91, 160, 0, 0.7)',
        backgroundColor: 'rgba(91, 160, 0, 0.7)'
      },
      {
        label: 'CLO survey measures',
        data: mlo_survey_measures,
        fill: false,
        borderColor: 'rgba(151, 60, 71, 0.7)',
        backgroundColor: 'rgba(151, 60, 71, 0.7)'
      },
      {
        label: 'SLO survey measures',
        data: slo_survey_measures,
        fill: false,
        borderColor: 'rgba(11, 60, 171, 0.7)',
        backgroundColor: 'rgba(11, 60, 171, 0.7)'
      }
    ]
    };

    const config = {
      type: 'line',
      data: data,
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title:{
                display: true,
                text:'SLO achievement (%)',                
                font: {size: 17}
            },
          }
        },
        plugins: {
          legend: {
              display: true,
          }
      }
      },
    };
    
    let root_name = "slo_measures_chart-"
    let element_id =  root_name.concat(index)
    const myChart = new Chart(
        document.getElementById(element_id),
        config
      );
}