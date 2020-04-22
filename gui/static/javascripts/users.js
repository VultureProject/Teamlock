$(function(){
  $('.btn-add').on('click', function(){
    $.post(
      user_edit_url,
      {'csrfmiddlewaretoken': getCookie('csrftoken')},

      function(response){
        if (typeof(response) === "string"){
          $('#edit-modal-user').modal('show');
          $('#user-modal-content').html(response);
          init_control();
        } else {
          notify('error', 'Error', response['error']);
        }
      }
    )
  })

  $('#form-submit').on('click', function(){
    var btn = this;
    var txt = $(btn).html()
    $(btn).html('<i class="fa fa-spinner fa-spin"></i>');
    $(btn).prop('disabled', 'disabled');

    var data = $('#form_user').serialize();

    $('#load_ajax').html('<i class="fa fa-spinner fa-spin"></i>');
    $.post(
      $('#form_user').attr('action'),
      data,

      function(response){
        $('#load_ajax').html("");
        $(btn).html(txt);
        $(btn).prop('disabled', '');

        if (!response.status){
          if (typeof(response.error) === "string"){
            notify('error', 'Error', response.error);
            $('#edit-modal-user').modal('hide');
            
          } else {
            $.each(response['error'], function(key, value){
              $('#id_error_'+key).html(value[0]);
            })
          }

        } else {
          $('#edit-modal-user').modal('hide');
          notify('success', 'Success', '{% trans "User has been saved" %}');
          var users_table = $('#users').dataTable();
          if (response.user_id){
            var nodes = users_table.fnGetNodes();
            for (var i in nodes){
              var d = users_table.fnGetData(nodes[i]);
              if (d.id === response.user_id){
                var pos = users_table.fnGetPosition(nodes[i]);
                users_table.fnDeleteRow(pos);
                break;
              }
            }
          }

          users_table.fnAddData(response.user);
        }
      }
    )
  })

  function check_times(data){
    if ($.inArray(data, ["True", "true", true]) > -1)
      return "<i class='fa fa-check'></i>"

    return "<i class='fa fa-times'></i>"
  }

  var table = $('#users').DataTable({
    aaSorting    : [[1, "desc"]],
    sDom: '<"top"<"clear">>rt<"bottom"<"clear">>',
    oLanguage: {
      sLengthMenu: '_MENU_',
      oPaginate  : {
        sNext    : '',
        sPrevious: ''
      }
    },
    aoColumns    : [
      {mData: "id", name: "id", defaultContent: "", bVisible: false, aTargets: [0], sClass: "center", bSortable: false},
      {mData: "first_name", name: "first_name", defaultContent: "", bVisible: true, aTargets: [1], sClass: "center", bSortable: true},
      {mData: "last_name", name: "last_name", defaultContent: "", bVisible: true, aTargets: [2], sClass: "center", bSortable: true},
      {mData: "email", name: "email", defaultContent: "", bVisible: true, aTargets: [3], sClass: "center", bSortable: true},
      {mData: "configure", name: "configure", defaultContent: "", bVisible: true, aTargets: [4], sClass: "center", bSortable: true, mRender: function(data, type, row){
        try{
          return check_times(data);

        } catch (err){
          return data;
        }
      }},
      {mData: "is_superuser", name: "is_superuser", defaultContent: "", bVisible: true, aTargets: [5], sClass: "center", bSortable: true, mRender: function(data, type, row){
        try{
          return check_times(data);

        } catch (err){
          return data;
        }
      }},
      {mData: "is_locked", name: "is_locked", defaultContent: "", bVisible: true, aTargets: [6], sClass: "center", bSortable: true, mRender: function(data, type, row){
        try{
          return check_times(data);

        } catch (err){
          return data;
        }
      }},
      {mData: "action", name: "action", defaultContent: "", bVisible: true, aTargets: [7], sClass: "center", bSortable: false, sWidth: '10%', mRender: function(data, type, row){
        var action_lock = "lock";

        if (row.is_locked === "True")
          action_lock = "unlock";

        return "<button href='#' class='btn btn-xs btn-flat btn-warning lock-link' data-action='{0}'><i class='fa fa-{0}'></i></button>&nbsp;&nbsp;<button href='#' class='btn btn-xs btn-flat btn-danger delete-link'><i class='fa fa-trash'></i></button>".format(action_lock);
      }},
    ],

    "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
      var td_action = $(nRow).find('td').last();
      $(td_action).find('button.delete-link').on('click', function(e){
        e.preventDefault();
        e.stopPropagation();

        $.post(
          get_user_workspaces_url,
          {
            'csrfmiddlewaretoken': getCookie('csrftoken'),
            'user_id': aData['id']
          },

          function(response){
            if (!response.status){
              notify('error', gettext('Error'), response.error);
              return;
            }

            var confirm_text = gettext('Delete this users will remove the following Workspaces:') + "<br/>"
            for (var i in response.workspaces)
              confirm_text += "- " + response.workspaces[i] + "<br/>"

            var notice = new PNotify({
              title: gettext('Confirmation'),
              text: confirm_text,
              icon: 'fa fa-trash',
              hide: false,
              confirm: {
                  confirm: true
              },
              buttons: {
                  closer: false,
                  sticker: false
              },
              history: {
                  history: false
              }
            }).get().on('pnotify.confirm', function() {

              $.post(
                user_delete_url,
                {
                  'csrfmiddlewaretoken': getCookie('csrftoken'),
                  'user_id': aData['id']
                },

                function(response){
                  if (typeof(response) === 'string')
                    window.location.href = response;

                  if (!response['status']){
                    notify('error', 'Error', response['error']);
                  } else if (response['status']){
                    notify('success', 'success', response['success']);

                    var users_table = $('#users').dataTable();
                    var nodes       = users_table.fnGetNodes();
                    for (var i in nodes){
                      var d = users_table.fnGetData(nodes[i]);
                      if (d.id === aData['id']){
                        var pos = users_table.fnGetPosition(nodes[i]);
                        users_table.fnDeleteRow(pos);
                        break;
                      }
                    }
                  }
                }
              )
            });
          }
        )
      })

      $(td_action).find('button.lock-link').on('click', function(e){
        e.preventDefault();
        e.stopPropagation();

        var url = user_lock_url;
        var text = gettext('Lock user ?')
        if ($(this).data('action') === "unlock"){
          url = user_unlock_url;
          text = gettext('Unlock user ?')
        }

        new PNotify({
            title: gettext('Confirmation'),
            text: text,
            icon: 'fa fa-question-circle',
            hide: false,
            confirm: {
                confirm: true
            },
            buttons: {
                closer: false,
                sticker: false
            },
            history: {
                history: false
            }
        }).get().on('pnotify.confirm', function() {
          $.post(
            url,
            {
              'csrfmiddlewaretoken': getCookie('csrftoken'),
              'user_id': aData['id']
            },

            function(response){
              if (typeof(response) === 'string')
                window.location.href = response;

              if (!response['status'])
                notify('error', 'Error', response['error']);
              else if (response['status'])
                notify('success', 'success', response['success']);

              $("#users").dataTable().fnDraw();
            }
          )
        });
      })

      $(nRow).on('click', function(){
        $.post(
          user_edit_url,
          {
            'csrfmiddlewaretoken': getCookie('csrftoken'),
            'user_id': aData['id']
          },

          function(response){
            if (typeof(response) === "string"){
              $('#edit-modal-user').modal('show');
              $('#user-modal-content').html(response);
              init_control();
            } else {
              notify('error', 'Error', response['error']);
            }
          }
        )
      })
    }
  });

  $('#form-search').on('submit', function(e){
    e.preventDefault();
    var table = $('#users').dataTable();
    table.fnFilter($('#search-input').val());
  })
})