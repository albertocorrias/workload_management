

var survey_results = JSON.parse(document.getElementById('bar_chart_data').textContent);
var survey_labels = JSON.parse(document.getElementById('chart_labels').textContent);
var question_texts = JSON.parse(document.getElementById('question_texts').textContent);
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