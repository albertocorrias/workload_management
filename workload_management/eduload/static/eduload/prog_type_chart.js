

var count_of_hours_prog = JSON.parse(document.getElementById('hours_prog').textContent);
var prog_labels = JSON.parse(document.getElementById('labels_prog').textContent);

const data_prog = {
  labels: prog_labels,
  datasets: [{
    label: 'My First Dataset',
    data: count_of_hours_prog,
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

const config_prog = {
  type: 'doughnut',
  data: data_prog,
  options: {
  responsive : true,
  maintainAspectRatio: true,
  plugins: {
      legend: {position: 'bottom'},
      title: {
        display: true,
        text: 'Hours by programme',
        position: 'top'
    }
  }
}
};

const myChartProg = new Chart(
    document.getElementById('prog_type_chart'),
    config_prog
  );
