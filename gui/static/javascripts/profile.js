$(function(){
    $('#generate_recovery_key').on('click', function(){
        $.post(
            generate_recovery_key_url,
            {
                passphrase: get_passphrase(),
                csrfmiddlewaretoken: getCookie('csrftoken')
            },

            function(response){
                if (!response.status){
                    notify('error', gettext('Error'), response.error)
                    return false;
                }

                var blob = new Blob([response.data], {type: "text/plain;charset=utf-8"})
                saveAs(blob, response.filename)
            }
        )
    })
})