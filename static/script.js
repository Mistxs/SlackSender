$(document).ready(function() {
    $('#search_button').on('click', function() {
        $('#oldres').hide();
        var start_date = $('#start_date').val();
        var end_date = $('#end_date').val();
        var city1Id = $('#city1-input').attr('data-city-id');
        var city2Id = $('#city2-input').attr('data-city-id');

        $('#progress_bar').val(0);
        $('#progress').show();
        $('#oldres tbody').empty(); // Очищаем предыдущие типы вагонов

        var eventSource = new EventSource(`/search?start_date=${start_date}&end_date=${end_date}&city1=${city1Id}&city2=${city2Id}`, { withCredentials: true });

        eventSource.onmessage = function(event) {
            var response = JSON.parse(event.data);
            var progress = response.progress;
            $('#progress_bar').val(progress);

            if (progress === 100) {
                eventSource.close();
                $('#progress').hide();

                var data = response.data;
                displayResults(data);
            }
        };
    });


    $(function () {
            $(".city-input").autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "/autocomplete",
                        data: { search: request.term },
                        dataType: "json",
                        success: function (data) {
                            response(data);
                        }
                    });
                },
                minLength: 2,
                select: function(event, ui) {
                    $(this).val(ui.item.label);
                    $(this).attr('data-city-id', ui.item.value);
                    return false;
                }
            });


        });

});

function displayResults(data) {
    var resultsTable = $('#oldres');
    $('#oldres').show();

    // Добавляем даты в заголовок
    var theadRow = resultsTable.find('thead tr');
    theadRow.empty();
    theadRow.append('<th>Вагон \ Дата</th>');

    for (var date in data) {
        var dateCell = $(`<th>${date}</th>`);
        theadRow.append(dateCell);

        var tickets = data[date];

        for (var ticketType in tickets) {
    console.log(ticketType);
    if (ticketType.includes('ПЛАЦ') || ticketType.includes('СИД') || ticketType.includes('КУПЕ')) {
        var ticket = tickets[ticketType];
                var ticketRow = resultsTable.find(`tr[data-type="${ticketType}"]`);
                var ticketCell = $(`<td class="ticket-info" data-date="${date}" data-type="${ticketType}"></td>`);

                ticketCell.html(ticket.price)
                    .attr('title', `Train: ${ticket.train}\nDeparture: ${ticket.departure}\nArrival: ${ticket.arrival}`);

                if (!ticketRow.length) {
                    ticketRow = $(`<tr data-type="${ticketType}"><td>${ticketType}</td></tr>`);
                    resultsTable.find('tbody').append(ticketRow);
                }

                ticketRow.append(ticketCell);
            }
        }
    }
}
