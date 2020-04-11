$(function(){

    var columns = [
        {title: gettext('Date'), targets: [0], data: "date", render: function(data, type, row){
            return moment(data).format("DD/MM/YYYY HH:mm:ss")
        }},
        {title: gettext("User"), targets: [1], data: 'user'},
        {title: gettext("Workspace"), targets: [2], data: 'workspace'},
        {title: gettext("Action"), targets: [3], data: 'action'},
    ];

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
            }
        },
    })
})