$(function(){
    // $('#generate_recovery_key').on('click', function(){
    //     $.post(
    //         generate_recovery_key_url,
    //         {
    //             passphrase: get_passphrase(),
    //             csrfmiddlewaretoken: getCookie('csrftoken')
    //         },

    //         function(response){
    //             if (!response.status){
    //                 notify('error', gettext('Error'), response.error)
    //                 return false;
    //             }

    //             var blob = new Blob([response.data], {type: "text/plain;charset=utf-8"})
    //             saveAs(blob, response.filename)
    //         }
    //     )
    // })

    var columns = [
        {title: gettext('Date'), targets: [0], data: "date", render: function(data, type, row){
            return moment(data).format("DD/MM/YYYY HH:mm:ss")
        }},
        {title: gettext("Browser"), targets: [1], data: 'browser', render: function(data, type, row){
            var mapping = {
                "Chrome": "chrome",
                "Firefox": "firefox",
                "Edge": "edge",
                "Safari": "safari",
                "Opera": "opera"
            }

            for (const [key, value] of Object.entries(mapping)) {
                if (data.includes(key))
                    return "<i class='fa fa-" + value + "'></i>&nbsp;&nbsp;&nbsp;" + data;
            }

        }},
        {title: gettext("OS"), targets: [2], data: 'os', render: function(data, type, row){
            var mapping = {
                "Mac OS X": "apple",
                "Windows": "windows",
                "Linux": "ubuntu",
                "Android": "android",
                "iOs": "ios"
            }

            for (const [key, value] of Object.entries(mapping)) {
                if (data.includes(key))
                    return "<i class='fa fa-" + value + "'></i>&nbsp;&nbsp;&nbsp;" + data;
            }
        }},
        {title: gettext("IP Address"), targets: [3], data: 'ip_address'},
    ];

    $('#table-session-history').dataTable({
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
                d.columns = JSON.stringify(["date", "browser", "os", "ip_address"])
            }
        },
    })
})