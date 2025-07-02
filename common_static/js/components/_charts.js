/*
    Charts JS
*/
;
'Use Strict';

let __FELIX_CHARTS;
;(function() {
    let _this = '';
    let chart_class = '.felix-chart';

    __FELIX_CHARTS =
    {
        init: function()
        {
            _this = this;

            _this.loadCharts();
        },

        loadCharts: function() {
            $.each($(chart_class), function() {
                let elem = this;
                let labels = [];
                let data = [];
                let params = elem.dataset.params;
                let endpoint = elem.dataset.endpoint;
                let options = _this.getChartOptions(elem);

                if(params)
                    endpoint = endpoint + '?' + params;

                $.get(endpoint, function(response) {
                    $.each(response, function() {
                        labels.push(this[0]);
                        data.push(this[1]);
                    });

                    let dataset = {
                        label: elem.dataset.label,
                        backgroundColor: 'rgba(0, 123, 255, 0.5)',
                        borderColor: 'rgba(4, 96, 195, 0.5)',
                        data: data,
                        lineTension: 0
                    };

                    if(elem.dataset.fill == 'false') {
                        dataset['fill'] = false;
                    }

                    let chart = new Chart(elem.getContext('2d'), {
                        type: elem.dataset.type,
                        options: options,
                        data: {
                            labels: labels,
                            datasets: [dataset]
                        }
                    });

                    $(elem).siblings('.preloader').addClass('hide');
                });
            });
        },
        getChartOptions: function(elem) {
            let options = {
                legend: {
                    display: false
                },
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero:true,
                            userCallback: function(value, index, values) {
                                return accounting.format(value.toString());
                            }
                        }
                    }]
                }
            };

            if('tooltip_prefix' in elem.dataset && elem.dataset.tooltip_prefix) {
                options['tooltips'] = {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            return accounting.format(data.datasets[0].data[tooltipItem.index]) + elem.dataset.tooltip_prefix;
                        }
                    }
                };
            } else {
                options['tooltips'] = {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            return accounting.format(data.datasets[0].data[tooltipItem.index]);
                        }
                    }
                };
            }

            return options;
        }
    };

    jQuery(function() {
        __FELIX_CHARTS.init();
    });
})();
