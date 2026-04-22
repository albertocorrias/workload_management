

var survey_results = JSON.parse(document.getElementById('overall_plot_data').textContent);
var survey_labels = JSON.parse(document.getElementById('chart_labels').textContent);
var shorter_question_texts = JSON.parse(document.getElementById('shorter_question_texts').textContent);
var bar_background_colors = ['rgb(0, 0, 71)' ,
                             'rgba(20, 2, 81, 0.9)',
                             'rgba(40, 40, 91, 0.8)',
                             'rgba(60, 60, 101, 0.7)',
                             'rgba(80, 80, 121, 0.6)',
                             'rgba(100, 100, 131, 0.5)',
                             'rgba(120, 120, 141, 0.4)',
                             'rgba(140, 140, 151, 0.3)',
                             'rgba(160, 160, 161, 0.2)',
                             'rgba(180, 180, 171, 0.1)', ]


const labels = shorter_question_texts
var mydataset = []
for (let i = 0; i < survey_results.length; i++) {
    mydataset.push({
        label: survey_labels[i],
        data: survey_results[i],
        backgroundColor: bar_background_colors[i],

    })
}
const data = {
labels: labels,
datasets: mydataset,
};

const config = {
    type: 'bar',
    data: data,
    options: {

    indexAxis: 'y',
      plugins: {
        title: {
          display: false
        },
        legend: {
            display: true,
            position:'top',
          },
      },
      responsive: true,
      scales: {
        x: {
          stacked: true,
          min: 0,
          max: 100
        },
        y: {
          stacked: true
        }
      },
    }
  };

  const myChart = new Chart(
    document.getElementById('survey_summary_results_chart'),
    config
  );
