$(function(){

    var columns = [
        {title: gettext('Date'), targets: [0], data: "date", render: function(data, type, row){
            return moment(data).format("DD/MM/YYYY HH:mm:ss")
        }},
        {title: gettext("User"), targets: [1], data: 'user'},
        {title: gettext("Workspace"), targets: [2], data: 'workspace'},
        {title: gettext("Action"), targets: [3], data: 'action'},
    ];

    var icon_calendar = "<i class='fa fa-calendar'></i>&nbsp;&nbsp;";

    $('#reportrange_history').html(icon_calendar + gettext('Today'));
    reportrange = $('#reportrange_history').daterangepicker({
        format             : 'MM/DD/YYYY HH:mm:ss',
        minDate            : '01/01/1970',
        showDropdowns      : true,
        showWeekNumbers    : true,
        timePicker         : true,
        timePickerIncrement: 1,
        timePicker12Hour   : false,
        ranges             : ranges,
        opens              : 'right',
        buttonClasses      : ['btn', 'btn-sm'],
        applyClass         : 'btn-primary',
        cancelClass        : 'btn-default',
        separator          : gettext(' to '),
        locale: {
            applyLabel      : apply_label,
            cancelLabel     : cancel_label,
            fromLabel       : from_label,
            toLabel         : to_label,
            customRangeLabel: custom_label,
            daysOfWeek      : daysOfWeek,
            monthNames      : monthNames,
            firstDay        : 1,
        }
    }, function(start, end, label) {
        start_time = start.valueOf();
        end_time   = end.valueOf();

        if (label === custom_label)
            label = start.format("DD/MM/YYYY HH:mm:ss") + " <i class='fa fa-arrow-right'></i> " + end.format("DD/MM/YYYY HH:mm:ss")

        $('#reportrange_history').html(icon_calendar + label);
        $('#table-history').DataTable().draw();
    });

    $('#table-history').dataTable({
        destroy: true,
        processing: true,
        serverSide: true,
        iDisplayLength: 50,
        orderMulti: true,
        order: [[0, 'asc']],
        dom: '<"top">rt<"bottom"p><"clear">',
        columnDefs: columns,

        ajax: {
            url: "",
            type: 'GET',
            data: function(d){
                d.columns = JSON.stringify(["date", "user", "workspace", "Action"])

                var users = $('#users').val();
                if (!users)
                    users = [];
                
                d.users = JSON.stringify(users);

                var workspaces = $('#workspaces').val();
                if (!workspaces)
                    workspaces = [];
                
                d.workspaces = JSON.stringify(workspaces);

                var startDate = $('#reportrange_history').data('daterangepicker').startDate;
                var endDate = $('#reportrange_history').data('daterangepicker').endDate;

                d.startDate = startDate.format();
                d.endDate = endDate.format();
            }
        }
    })

    $('.reload').on('change', function(){
        $('#table-history').DataTable().draw();
    })
})