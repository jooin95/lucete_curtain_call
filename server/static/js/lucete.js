let time = 1;

$(function() {
    $(document).ready(function() {


    });
//    function update() {
//    $('#current_time').html(moment().format('YYYY년 MM월 DD일 HH시 mm분 ss초'));
//
//    }
//    setInterval(update, 1000);
//    $('#startDate').datetimepicker({
//        format: 'YYYY-MM-DD',
//        defaultDate: '2020-04-15'
//    });
//    $('#finishDate').datetimepicker({
//        format: 'YYYY-MM-DD',
//        defaultDate: '2020-05-01'
//    });

    $('#process1').click(function(e) {
//        playAlert = setInterval(function () {
            $.ajax({
                url: '/vis/start_server/',
                method: 'POST',
                dataType: 'json',
                data: {},
                beforeSend: function () {
                },
                success: function (data) {
                    alert(data);
                }
            });
//        },5000);

    });
    $('#process2').click(function(e) {
//        playAlert = setInterval(function () {
            $.ajax({
                url: '/vis/stop_server/',
                method: 'POST',
                dataType: 'json',
                data: {},
                beforeSend: function () {
                },
                success: function (data) {
                    alert('server finish');
                }
            });
//        },5000);

    });
    $('#process3').click(function(e) {
//        playAlert = setInterval(function () {
            $.ajax({
                url: '/vis/weather_upload/',
                method: 'POST',
                dataType: 'json',
                data: {},
                beforeSend: function () {
                },
                success: function (data) {
                    alert('upload finish');
                }
            });
//        },5000);

    });
    $('#process4').click(function(e) {
//        playAlert = setInterval(function () {
            $.ajax({
                url: '/vis/test_send/',
                method: 'POST',
                dataType: 'json',
                data: {},
                beforeSend: function () {
                },
                success: function (data) {

                }
            });
//        },5000);

    });
    $('#process5').click(function(e) {
//        playAlert = setInterval(function () {
            $.ajax({
                url: '/vis/test_send/',
                method: 'POST',
                dataType: 'json',
                data: {},
                beforeSend: function () {
                },
                success: function (data) {

                }
            });
//        },5000);

    });
});
