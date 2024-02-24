


var count_of_hours_expected = JSON.parse(document.getElementById('hrs_temp_individual_expected').textContent);
var count_of_hours_delivered = JSON.parse(document.getElementById('hrs_temp_individual_delivered').textContent);
var labels_temp_individual = JSON.parse(document.getElementById('labels_temp_individual').textContent);


const data_temp_individual = {
  labels: labels_temp_individual,
  datasets: [{
    label: 'Expected',
    data: count_of_hours_expected,
    fill: false,
    borderColor: 'rgb(75, 192, 192)',
    tension: 0
    },{
    label: 'Delivered',
    data: count_of_hours_delivered,
    fill: false,
    borderColor: 'rgb(175, 18, 192)',
    tension: 0
  }]
};


const config_temp_individual = {
    type: 'line',
    data: data_temp_individual,
  };

const temporal_individual_chart = new Chart(
    document.getElementById('temporal-individual-staff-chart'),
    config_temp_individual
  );