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
        $.ajax({
            url: '/vis/data_insert/',
            method: 'POST',
            dataType: 'json',
            data: {},
            beforeSend: function () {
            },
            success: function (data) {

            }
        },1000);
    });
});
