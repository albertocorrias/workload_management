

var count_of_hours = JSON.parse(document.getElementById('hour_counts').textContent);
var mod_labels = JSON.parse(document.getElementById('chart_labels').textContent);

const data = {
  labels: mod_labels,
  datasets: [{
    label: 'My First Dataset',
    data: count_of_hours,
    backgroundColor: [
      'rgb(255, 99, 132)',
      'rgb(54, 162, 235)',
      'rgb(255, 205, 86)',
      'rgb(155, 105, 186)',
		'rgb(75, 15, 106)',
		'rgb(3, 145, 156)',
    ],
    hoverOffset: 4
  }]
};

const config = {
  type: 'doughnut',
  data: data,
  options: {
  responsive : true,
  maintainAspectRatio: true,
  plugins: {
      legend: {position: 'bottom'},
      title: {
        display: true,
        text: 'Hours by area',
        position: 'top'
    }
  }
}
};

const myChart = new Chart(
    document.getElementById('module_type_chart'),
    config
  );
