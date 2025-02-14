


var count_of_hours_expected = JSON.parse(document.getElementById('hrs_temp_individual_expected').textContent);
var count_of_hours_delivered = JSON.parse(document.getElementById('hrs_temp_individual_delivered').textContent);
var labels_temp_individual = JSON.parse(document.getElementById('labels_temp_individual').textContent);
var hrs_expected_upper_boundary = JSON.parse(document.getElementById('hrs_expected_upper_boundary').textContent);
var hrs_expected_lower_boundary = JSON.parse(document.getElementById('hrs_expected_lower_boundary').textContent);

const data_temp_individual = {
  labels: labels_temp_individual,
  datasets: [{
    label: 'Expected',
    data: count_of_hours_expected,
    fill: false,
    showLine: false,
    pointStyle: false,
    pointRadius: 0,
    tension: 0
    },{
    label: 'Delivered',
    data: count_of_hours_delivered,
    fill: false,
    borderColor: 'rgb(175, 18, 192)',
    tension: 0
  },
  {
    label: 'Expected',
    data: hrs_expected_upper_boundary,
    fill: false,
    borderColor: 'rgb(115, 143, 31)',
    tension: 0
  },
  {
    label: 'Expected range',
    data: hrs_expected_lower_boundary,
    fill: '-1',
    borderColor: 'rgb(115, 143, 31)',
    backgroundColor: 'rgba(189, 235, 52, 0.5)',
    tension: 0
  },
]
};


const config_temp_individual = {
    type: 'line',
    data: data_temp_individual,
    options : {
      scales:{
          y : {
            title: {
              display: true,
              text  : 'Number of hours',
              font: {
                size: 18
            }
          },
          ticks: {
            font: {
              size: 18
            }
          }
        },
        x : {
          title: {
            display: true,
            text  : 'Academic year',
            font: {
              size: 18
            }
          },
          ticks: {
            font: {
              size: 18
          }
        }
        }
      },
      plugins:{
        legend :{
          labels:{
            filter: item => item.text !== 'Expected',
            font : {
              size: 25
            },
          },
          position: 'right'
        }

      }

    }
  };

const temporal_individual_chart = new Chart(
    document.getElementById('temporal-individual-staff-chart'),
    config_temp_individual
  );