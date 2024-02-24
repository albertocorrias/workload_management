

var survey_results = JSON.parse(document.getElementById('bar_chart_data').textContent);
var survey_labels = JSON.parse(document.getElementById('chart_labels').textContent);
var question_texts = JSON.parse(document.getElementById('question_texts').textContent);
var bar_background_colors = ['rgba(0, 0, 71, 0.7)',
                             'rgba(0, 0, 71, 0.6)',
                             'rgba(0, 0, 71, 0.5)',
                             'rgba(0, 0, 71, 0.4)',
                             'rgba(0, 0, 71, 0.3)',
                             'rgba(0, 0, 71, 0.2)', ]
for (let i = 0; i < survey_results.length; i++) {
    const data = {
      labels: survey_labels,
      datasets: [{
        label: question_texts[i],
        data: survey_results[i],
        backgroundColor: bar_background_colors,
      }]
    };

    const config = {
      type: 'bar',
      data: data,
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins: {
          legend: {
              display: false,
          }
      }
      },
    };
    
    let root_name = "survey_results_chart"
    let index = String(i)
    let element_id =  root_name.concat(index)
    const myChart = new Chart(
        document.getElementById(element_id),
        config
      );
}