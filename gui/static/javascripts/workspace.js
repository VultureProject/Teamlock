function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function copy(text){
	$('#toCopy').val(text);
	$('#toCopy').show();
	toCopy.select();
	document.execCommand('copy');
	$('#toCopy').hide();
	return false;
}

function formatIcon (state) {
  if (!state.id) { return state.text; }
  var $state = $(
    '<span><i class="' + state.element.value.toLowerCase() + '">&nbsp;&nbsp;</i>' + state.text + '</span>'
  );
  return $state;
};

function get_workspaces(){
	if ($('#workspaces-select').data('select2')){
		$('#workspaces-select').select2('destroy');
		$('#workspaces-select').find('option').remove();
	}

	$.getJSON('/workspace', function(response){
		$('#workspaces-select').select2({
			data: response.workspaces
		});

		$('#workspaces-select').trigger('change');
	})
}

get_workspaces();
var workspace_vue;
var keys_table;
var folders;
var keys;


$('#btn-add-key').on('click', function(){
	var node = $('#tree').jstree('get_selected');

	workspace_vue.key = {
		id          : "",
		name        : "",
		login       : "",
		password    : "",
		uri         : "",
		ipv4        : "",
		ipv6        : "",
		os          : "",
		informations: "",
		folder      : node[0],
	}
	$('#modal-add-key').modal('show');	
})

$('#form-save-key').unbind('submit');
$('#form-save-key').on('submit', function(e){
	e.preventDefault();

	var txt = $('#btn-action-keyring').html();
	$('#btn-action-keyring').html('<i class="fa fa-spinner fa-spin"></i>');
	$('#btn-action-keyring').prop('disabled', true);

	var key = {
		id          : workspace_vue.key.id,
		name        : workspace_vue.key.name,
		login       : workspace_vue.key.login,
		password    : workspace_vue.key.password,
		uri         : workspace_vue.key.uri,
		ipv4        : workspace_vue.key.ipv4,
		ipv6        : workspace_vue.key.ipv6,
		os          : $('#os').val(),
		informations: workspace_vue.key.informations,
		folder      : workspace_vue.folder
	}

	$.post(
		'/workspace/savekey/', 
		{
			id                 : key.id,
			name               : key.name,
			login              : key.login,
			password           : key.password,
			uri                : key.uri,
			ipv4               : key.ipv4,
			ipv6               : key.ipv6,
			os                 : key.os,
			informations       : key.informations,
			folder             : key.folder,
			workspace_id       : $('#workspaces-select').val(),
			csrfmiddlewaretoken: getCookie('csrftoken'),
			passphrase         : get_passphrase()
		}, 

		function(response){
			$('#btn-action-keyring').html(txt);
			$('#btn-action-keyring').prop('disabled', false);

			if (response.status){
				notify('success', gettext('Success'), gettext('Key saved !'))
				var keys_table = $('#keys').dataTable();

				if (key.id !== ""){
					// Remove key from datatable and array
					var nodes = keys_table.fnGetNodes();
					for (var i in nodes){
						var d = keys_table.fnGetData(nodes[i]);
						if (d.id === key.id){
							var pos = keys_table.fnGetPosition(nodes[i]);
							keys_table.fnDeleteRow(pos);
							break;
						}
					}

					for (var i in keys){
						if (keys[i].id == key.id){
							keys.splice(i, 1);
							break;
						}
					}
				} else {
					// keys.push(key);
				}

				keys_table.fnAddData(response.data);
				$('#modal-add-key').modal('hide');
			} else {
				notify('error', gettext('Error'), response.error);
			}
		}
	)
})

$('#form-save-folder').unbind('submit');
$('#form-save-folder').on('submit', function(e){
	e.preventDefault();

	var txt = $('#btn-add-folder').html();
	$('#btn-add-folder').html('<i class="fa fa-spinner fa-spin"></i>');
	$('#btn-add-folder').prop('disabled', true);

	var data = {
		id                 : workspace_vue.folder.id,
		text               : workspace_vue.folder.text,
		icon               : $('#id_icon_folder').val(),
		parent             : workspace_vue.folder.parent,
		passphrase         : get_passphrase(),
		workspace_id       : $('#workspaces-select').val(),
		csrfmiddlewaretoken: getCookie('csrftoken'),
	}

	$.post(
		'/workspace/savefolder/',
		data,

		function(response){
			$('#btn-add-folder').html(txt);
			$('#btn-add-folder').prop('disabled', false);
			if (response.status){
				notify('success', gettext('Success'), gettext('Folder saved !'));

				if (!data.id){
					folders.push(response.folder);
				} else {
					for (var i in folders){
						if (folders[i].id === data.id)
							folders[i] = data;
					}
				}

				$('#tree').jstree(true).settings.core.data = folders;
				$('#tree').jstree(true).refresh()

			} else {
				notify('error', gettext('Error'), response.error);
			}

			$('#modal-add-folder').modal('hide');
		}
	)
})

$('.gen_pass').on('click', function(e){
	e.stopPropagation();
})

$('#button-export').on('click', function(){
	if (!get_passphrase())
		return;

	$.post(
		'/workspace/export/',
		{
			passphrase: get_passphrase(),
			workspace_id: $('#workspaces-select').val(),
			csrfmiddlewaretoken: getCookie('csrftoken')
		},

		function(response){
			
		}
	)
})

$('#add_users_share').on('click', function(){
	if (!get_passphrase())
		return;

	var btn  = this;
	var text = $(btn).html();
	$(btn).html("<i class='fa fa-spinner fa-spin'></i>");
	$(btn).prop('disabled', true);

	var users   = $('#share_users').val();
	var teams   = $('#share_teams').val();
	var read    = $('#read').is(':checked');
	var write   = $('#write').is(':checked');

	var right = 1;
	if (write)
		right = 2;

	if (!users && !teams){
		$(btn).html(text);
		notify('error', gettext('Erreur'), gettext('Please select at least one user'))
		return false;
	}

	$.post(
		'/workspace/share/',
		{
			right              : right,
			teams              : JSON.stringify(teams),
			users              : JSON.stringify(users),
			passphrase         : get_passphrase(),
			workspace_id       : $('#workspaces-select').val(),
			csrfmiddlewaretoken: getCookie('csrftoken')
		},

		function(response){
			$(btn).html(text);
			$(btn).prop('disabled', false);

			if (!response.status){
				notify('error', gettext('Error'), response.error);
			} else {
				$('#share_users').val("").trigger('change');
				$('#share_teams').val("").trigger('change');

				notify("success", "Success", "Workspace shared !");
				$('#table_share').dataTable().fnDraw();
			}
		}
	)	
})

$('#modal-share-workspace').on('shown.bs.modal', function() {
	var tables = $.fn.dataTable.fnTables(true);
	for (var i in tables){
		if (tables[i].id === 'table_share')
			return;
	}

	$('#write').on('change', function(){
		if (!$(this).is(':checked') && $('#delete').is(':checked'))
			$('#delete').click();
	})

	$('#delete').on('change', function(){
		if ($(this).is(':checked') && !$('#write').is(':checked'))
			$('#write').click();
	})

	$('#table_share').DataTable({
		bProcessing: true,
		bPaginate: true,
		aaSorting: [[1, "desc"]],
		aoColumns: [
			{mData: "pk", name: "pk", defaultContent: "", bVisible: false, aTargets: [0], sClass: "center", bSortable: false},
			{mData: "user", name: "user", defaultContent: "", bVisible: true, aTargets: [1], sClass: "center", bSortable: false, sWidth: "80%"},
			{mData: "right", name: "right", defaultContent: "", bVisible: true, aTargets: [2], sClass: "center", bSortable: false, sWidth: "5%", mRender: function(data, type, row){
				if (parseInt(data) <= 2)
					return "<i class='fa fa-check'></i>"
				else
					return "<i class='fa fa-times'></i>"
			}},
			{mData: "right", name: "right", defaultContent: "", bVisible: true, aTargets: [3], sClass: "center", bSortable: false, sWidth: "5%", mRender: function(data, type, row){
				if (parseInt(data) > 1)
					return "<i class='fa fa-check'></i>"
				else
					return "<i class='fa fa-times'></i>"
			}},
			{mData: "action", name: "action", defaultContent: "", bVisible: true, aTargets: [4], sClass: "center", bSortable: false, sWidth: "5%", mRender: function(data, type, row){
  					return "<button href='#' class='btn btn-xs btn-flat btn-danger btn-delete'><i class='fa fa-trash'></i></button>"
			}}
		],
		sAjaxSource: "/workspace/share/get/",
		sDom: '<"top"l<"clear">>rt<"bottom"ip<"clear">>',
        oLanguage: {
            sLengthMenu: '_MENU_',
            oPaginate  :{
                sNext    : '',
                sPrevious: ''
            }
        },
	    bServerSide  : true,
	    sServerMethod: "POST",
	    fnServerData : function(sSource, aoData, fnCallback){
	      aoData.push({
	        name : 'csrfmiddlewaretoken',
	        value: getCookie('csrftoken')
	      });

	      aoData.push({
	        name : 'workspace_id',
	        value: $('#workspaces-select').val()
	      });

	      $.ajax({
			type   : "POST",
			url    : sSource, 
			data   : aoData, 
			success: function(data, callback){
	            if (typeof(data) === 'string')
	              window.location.href = window.location.href;
	            else
	              fnCallback(data)
	        }
	      })
	    },

	    fnCreatedRow: function( nRow, aData, iDataIndex ) {
	    	$(nRow).find(".btn-delete").click(function(e){
	    		e.preventDefault();
	    		e.stopPropagation();

	    		$.post(
	    			'/workspace/share/delete/',
	    			{
						csrfmiddlewaretoken: getCookie('csrftoken'),
						shared_id          : aData['pk']
	    			},

	    			function(response){
	    				if (!response.status){
	    					notify("error", gettext("Error"), response.error);
	    				} else {
	    					notify("success", gettext("Success"), gettext("User revoked"));
	    					$('#table_share').dataTable().fnDraw();
	    				}
	    			}
	    		)
	    	});
	    }
	})
});

Vue.config.delimiters = ['${', '}'];
workspace_vue = new Vue({
	el: ".tl-content-body",
	data: {
		search_tree     : "",
		search_workspace: "",
		workspace_name  : "",
		folder_edit     : false,
		folder          : false,
		length_pass     : 8,
		number_pass     : true,
		uppercase_pass  : true,
		symbols_pass    : true,
		rights          : 2,

		key: {
			id          : "",
			name        : "",
			login       : "",
			password    : "",
			uri         : "",
			ipv4        : "",
			ipv6        : "",
			os          : "",
			informations: "",
		},

		folder: {
			id    : "",
			text  : "",
			icon  : "",
			parent: "",
		}
	},

	mounted: function(){
		get_workspaces();
	},

	watch: {
		search_tree: function(s){
			$('#tree').jstree(true).search(s);
		},

		search_workspace: function(s){
			$('#keys').dataTable().fnFilter(s);
			// $('#files').dataTable().fnFilter(s);
		}
	},

	methods: {
		date_format: function(data){
			var m = new moment(data);
			return m.format('DD/MM/YYYY HH:mm:ss');
		},

		showpass: function(){
			$('#id_password').showPassword();

			setTimeout(function(){
				$('#id_password').hidePassword();
			}, 2000);
		},

		import_xml_keepass: function(e){
			e.stopPropagation();

			var passphrase = get_passphrase();
			if (!passphrase)
				return;

			var self = this;

			var txt = $('#btn-import-file').html();
			$('#btn-import-file').html('<i class="fa fa-spinner fa-spin"></i>');
			$('#btn-import-file').prop('disabled', true);

			var workspace_id = $('#workspaces-select').val();

			var data = new FormData($('#import-keepass-form').get()[0]);

			data.append('workspace_id', workspace_id);
			data.append('passphrase', passphrase);

			$.ajax({
				type: 'POST',
				url: '/workspace/import/',
				data: data,
				dataType: 'json',
				processData: false,
				contentType: false
			}).done(function(response){
				$('#btn-import-file').html(txt);
				$('#btn-import-file').prop('disabled', false);

				if (!response.status){
					notify('error', gettext('Error'), response.error);
					return;
				}

				notify('success', gettext('Success'), gettext('KeePass successfully imported'))

				$('#modal-import-keepass').modal('hide');
				$('#workspaces-select').trigger('change')
			})

			return;
		},

		generatepass: function(e){
			e.stopPropagation();
			var self = this;

			$.post('/generatepass/', {
				csrfmiddlewaretoken: getCookie('csrftoken'),
				length             : self.length_pass,
				number             : self.number_pass,
				symbols            : self.symbols_pass,
				uppercase          : self.uppercase_pass,
			}, 
			function(response){
				self.key.password = response.password;
			})
		},

		add_folder_root: function(){
			workspace_vue.folder_edit = false;
			workspace_vue.folder = {
				id    : "",
				text  : "",
				icon  : "",
				parent: "#"
			}

			$('#id_icon_folder').select2({
				templateResult   : formatIcon,
				templateSelection: formatIcon
			})

			$('#modal-add-folder').modal('show');
		},

		delete_workspace: function(){

			var notice = new PNotify({
				title: gettext('Confirmation'),
				text: gettext('All keys will be lost !'),
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
				var txt = $('#btn-delete-workspace').html();
				$('#btn-delete-workspace').html('<i class="fa fa-spinner fa-spin"></i>');
				$('#btn-delete-workspace').prop('disabled', true);

				$.post(
					'/workspace/delete/',
					{
						csrfmiddlewaretoken: getCookie('csrftoken'),
						workspace_id       : $('#workspaces-select').val()
					},

					function(response){
						$('#btn-delete-workspace').html(txt);
						$('#btn-delete-workspace').prop('disabled', false);

						if (response.status){
							notify('success', gettext('Success'), gettext('Workspace successfully deleted !'))
							get_workspaces();
						} else {
							notify('error', 'Error', 'An error occured.')
						} 
					}
				)
			});
		},

		get_tree: function(workspace_id){
			var self = this;

			var passphrase = get_passphrase();
			if (!passphrase)
				return;

			$.post(
				'/workspace/tree/', {
					csrfmiddlewaretoken: getCookie('csrftoken'),
					workspace_id       : workspace_id,
					passphrase         : passphrase
				},

				function(response){
					if (!response.status){
						localStorage.clear();

						setTimeout(function(){
							self.get_tree($('#workspaces-select').val());
						}, 1000);
					} else {
						folders = JSON.parse(response.folders);
						self.rights = response.rights;
						self.init_tree();
						self.init_rights();
					}
				}
			)
		},

		init_rights: function(){
			var self = this;

			if (self.rights < 2){
				$('#dropdown-tool').hide();
				$('#btn-add-key').hide();
			} else {
				$('#dropdown-tool').show();
				$('#btn-add-key').show();
			}
		},

		init_tree: function(){
			var self = this;

			$('#tree').jstree({
				core: {
					data          : folders,
					multiple      : false,
					check_callback: true
				},
				contextmenu: {
					items: function(item){
						return {
							rename: {
								label : "Rename",
								icon  : "fa fa-edit",
								action: function(elem){
									workspace_vue.folder_edit = true;
									workspace_vue.folder = {
										id    : item.id,
										text  : item.text,
										icon  : item.icon,
										parent: item.parents[0]
									}

									$('#id_icon_folder').select2({
										templateResult   : formatIcon,
										templateSelection: formatIcon
									})

									$('#id_icon_folder').val(item.icon).trigger('change');

									$('#modal-add-folder').modal('show');
								}
							},
							add: {
								label : "Add folder",
								icon  : "fa fa-plus",
								action: function(elem){
									workspace_vue.folder_edit = false;
									workspace_vue.folder = {
										id    : "",
										text  : "",
										icon  : "",
										parent: item.id
									}

									$('#id_icon_folder').select2({
										templateResult   : formatIcon,
										templateSelection: formatIcon
									})

									$('#modal-add-folder').modal('show');
								}
							},
							delete: {
								label : "Delete",
								icon  : "fa fa-trash",
								action: function(elem){
									var tmp = {
										id    : item.id,
										text  : item.text,
										icon  : item.icon,
										parent: item.parents[0]
									}

									var notice = new PNotify({
										title: gettext('Confirmation'),
										text: gettext('All keys will be lost !'),
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
										var data = {
											folder_id          : item.id,
											csrfmiddlewaretoken: getCookie('csrftoken'),
											workspace_id       : $('#workspaces-select').val(),
											passphrase         : get_passphrase(),
											user               : $('#id_user').val()
										}

										$.post('/workspace/delfolder/', 
											data,

											function(response){
												if (response.status){
													notify('success', gettext('Success'), gettext('Folder successfully deleted !'))

													var new_folders = [];
													for (var folder of folders){
														if (folder.id !== response.folder && folder.parent != response.folder)
															new_folders.push(folder)
													}

													folders = new_folders;

													$('#tree').jstree(true).settings.core.data = folders;
													$('#tree').jstree(true).refresh()
												} else {
													notify('error', gettext('Error'), response.error);
												}
											}
										)
									});
								}
							}
						}
					}
				},
			    plugins: ["contextmenu", "dnd", "types", "search"]
			});

			$('#tree').on('loaded.jstree', function(){
				var jsonNodes = $('#tree').jstree(true).get_json();
				$('#tree').jstree(true).select_node(jsonNodes[0]);
			})

			$(document).on('dnd_stop.vakata', function (e, elem) {
				var ref       = $('#tree').jstree(true);
				var folder_id = ref.get_node(elem.data.nodes[0]).id;
				var parent_id = ref.get_node(elem.data.nodes[0]).parent; // '#' = no parent!

				$.post('/workspace/movefolder/', {
					csrfmiddlewaretoken: getCookie('csrftoken'),
					passphrase         : get_passphrase(),
					workspace_id       : $('#workspaces-select').val(),
					parent_id          : parent_id,
					folder_id          : folder_id
				}, function(response){
					if (response.status){
						for (var i in folders){
							if (folders[i].id === folder_id)
								folders[i].parent = parent_id
						}
					} else {
						notify('error', gettext('Error'), response.error)
					}
				})
			}); 

			$('#tree').on('changed.jstree', function(e, data){
				var node = data.node;
				if (!node)
					return;

				$('#btn-add-key').show();
				self.get_keys(node.id);
				self.folder = node.id;
			})

			$("#tree").on('open_node.jstree', function (event, data) {
				if (data.instance.get_icon(data.node) === "fa fa-folder-o")	
				    data.instance.set_icon(data.node,'fa fa-folder-open-o');
			});
			$("#tree").on('close_node.jstree', function (event, data) {
				if (data.instance.get_icon(data.node) === "fa fa-folder-open-o")	
				    data.instance.set_icon(data.node,'fa fa-folder-o');
			});
		},

		form_save_workspace: function(){
			var self = this;

			if (self.workspace_name === "")
				return;

			var txt = $('#btn-create-workspace').html();
			$('#btn-create-workspace').html('<i class="fa fa-spinner fa-spin"></i>');
			$('#btn-create-workspace').prop('disabled', true);

			$.post(
				'/workspace/new/', {
					csrfmiddlewaretoken: getCookie('csrftoken'),
					name               : self.workspace_name
				},

				function(response){
					$('#btn-create-workspace').html(txt);
					$('#btn-create-workspace').prop('disabled', false);

					if (response.status){

						notify('success', gettext("Success"), gettext("Workspace successfully created"));
						var workspace = JSON.parse(response.workspace);

						$('#workspaces-select').append(new Option(workspace.name, workspace.id))
						$('#modal-add-workspace').modal('hide');

						workspace_vue.workspace_name = "";

						$('#workspaces-select').trigger('change');
					} else {
						notify('error', gettext('Error'), response.error);
						$('#modal-add-workspace').modal('hide');
					}
				}, 'json'
			)
		},

		get_keys: function(folder_id){
			var passphrase = get_passphrase();
			if (!passphrase)
				return;

			$.post(
				'/workspace/keys/', {
					workspace_id       : $('#workspaces-select').val(),
					csrfmiddlewaretoken: getCookie('csrftoken'),
					passphrase         : passphrase,
					folder_id          : folder_id
				},

				function(response){
					$("#keys").dataTable().fnClearTable();
					if (response.keys.length){
						var keys = response.keys;
						for (var key of keys)
							$("#keys").dataTable().fnAddData(key);
					}
				}
			)
		}
	}
})

keys_table = $('#keys').DataTable({
	sDom: '<"top"<"clear">>rt<"bottom"l<"clear">>',
    oLanguage: {
        sLengthMenu: '_MENU_',
        oPaginate  :{
            sNext    : '',
            sPrevious: ''
        }
    },
	bPaginate  : false,
	aaSorting  : [[2, "asc"]],
	aoColumns  : [
      {mData: "id", name: "id", width: "0%", defaultContent: "", bVisible: false, aTargets: [0], sClass: "center", bSortable: false},
      {mData: "name", name: "name", width: "10%", defaultContent: "", bVisible: true, aTargets: [1], sClass: "center", bSortable: true},
      {mData: "login", name: "login", width: "10%", defaultContent: "", bVisible: true, aTargets: [2], sClass: "center", bSortable: true},
      {mData: "password", name: "password", width: "15%", defaultContent: "", bVisible: true, aTargets: [3], sClass: "center", bSortable: false, mRender: function(data, type, row){
      	return "<span class='passwd'>***********</span><button class='btn btn-success btn-xs btn-copy btn-flat'><i class='fa fa-copy'></i></button>";
      }},
      {mData: "uri", name: "uri", width: "30%", defaultContent: "", bVisible: true, aTargets: [4], sClass: "center", bSortable: true, render: function(data, type, row){
      	return data + "<a class='btn btn-warning btn-xs btn-link btn-flat' href='" + data + "' target='_blank'><i class='fa fa-external-link'></i></a>";
      }},
      {mData: "ipv4", name: "ipv4", width: "10%", defaultContent: "", bVisible: true, aTargets: [5], sClass: "center", bSortable: true},
      {mData: "ipv6", name: "ipv6", width: "10%", defaultContent: "", bVisible: true, aTargets: [6], sClass: "center", bSortable: true},
      {mData: "os", name: "os", width: "10%", defaultContent: "", bVisible: true, aTargets: [7], sClass: "center", bSortable: true},
      {mData: "informations", name: "informations", width: "", defaultContent: "", bVisible: false, aTargets: [8], sClass: "center", bSortable: false},
      {mData: "action", name: "action", width: "5%", defaultContent: "", bVisible: true, aTargets: [9], sClass: "center", bSortable: false, mRender: function(data, type, row){
      	if (workspace_vue.rights < 2)
      		return "";

  		return "<button href='#' class='btn btn-xs btn-flat btn-info btn-edit'><i class='fa fa-edit'></i></button>&nbsp;&nbsp;<button href='#' data-id='" + row.id + "' class='btn btn-xs btn-flat bg-navy btn-delete'><i class='fa fa-trash'></i></button>"
      }},
      {mData: "folder", name: "folder", defaultContent: "", bVisible: false, aTargets: [9], sClass: "center", bSortable: false, 'sWidth': "1%"},
    ],
    fnCreatedRow: function( nRow, aData, iDataIndex ) {
    	$(nRow).find('.passwd').click(function(e){
    		// Showing password for 3 seconds
    		e.preventDefault();
    		e.stopPropagation();

    		if (!get_passphrase())
				return;

    		var span = this;
    		var text = $(span).text();
    		$(span).html('<i class="fa fa-spinner fa-spin"></i>');

    		var data = {
				key_id             : aData.id,
				folder_id          : workspace_vue.folder,
				passphrase         : get_passphrase(),
				workspace_id       : $('#workspaces-select').val(),
				csrfmiddlewaretoken: getCookie('csrftoken'),
			}

    		$.post(
    			'/workspace/getpasswd',
    			data,

    			function(response){
    				$(span).text(text);
    				if (!response.status){
    					notify('error', gettext("Error"), response.error);
    					return;
    				}

    				$(span).text(response.data);
		    		setTimeout(function(){
		    			$(span).text(text);
		    		}, 3000);
    			}
    		)
    	});

    	$(nRow).find(".btn-copy").click(function(e){
    		// Copying password to buffer
    		e.preventDefault();
    		e.stopPropagation();

    		if (!get_passphrase())
				return;

    		var span = this;
    		var text = $(span).html();
    		console.log(text)
    		$(span).html('<i class="fa fa-spinner fa-spin"></i>');

    		var data = {
				key_id             : aData.id,
				folder_id          : workspace_vue.folder,
				passphrase         : get_passphrase(),
				workspace_id       : $('#workspaces-select').val(),
				csrfmiddlewaretoken: getCookie('csrftoken'),
			}

    		$.post(
    			'/workspace/getpasswd',
    			data,

    			function(response){
    				$(span).html(text);
    				if (!response.status){
    					notify('error', gettext("Error"), response.error);
    					return;
    				}

    				copy(response.data);
    			}
    		)			
    	})

    	$(nRow).find(".btn-edit").click(function(e){
    		e.preventDefault();
    		e.stopPropagation();

    		if (workspace_vue.rights < 2)
	      		return "";

    		if (!get_passphrase())
				return;

			var span = this;
    		var text = $(span).html();
    		$(span).html('<i class="fa fa-spinner fa-spin"></i>');

			var data = {
				key_id             : aData.id,
				folder_id          : workspace_vue.folder,
				passphrase         : get_passphrase(),
				workspace_id       : $('#workspaces-select').val(),
				csrfmiddlewaretoken: getCookie('csrftoken'),
			}

    		$.post(
    			'/workspace/getpasswd',
    			data,

    			function(response){
    				$(span).html(text);
    				if (!response.status){
    					notify('error', gettext("Error"), response.error);
    					return;
    				}

					workspace_vue.key = {
						id          : aData.id,
						name        : aData.name,
						login       : aData.login,
						password    : response.data,
						uri         : aData.uri,
						ipv4        : aData.ipv4,
						ipv6        : aData.ipv6,
						os          : aData.os,
						informations: aData.informations,
						folder      : aData.folder,
					}

					$('#os').val(aData.os).trigger('change');
					$('#modal-add-key').modal('show');
    			}
    		)			

    	})

    	$(nRow).find('.btn-delete').click(function(e){
			var self = this;

			e.preventDefault();
			e.stopPropagation();

			if (workspace_vue.rights < 2)
	      		return "";

			(new PNotify({
		        title  : 'Delete',
		        text   : 'Delete selected key ?',
		        icon   : 'fa fa-trash',
		        hide   : false,
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
		    })).get().on('pnotify.confirm', function() {
  				var data = {
					key_id             : aData.id,
					folder_id          : workspace_vue.folder,
					passphrase         : get_passphrase(),
					workspace_id       : $('#workspaces-select').val(),
					csrfmiddlewaretoken: getCookie('csrftoken'),
  				}

  				$.post(
  					'/workspace/delkey/',
  					data,

  					function(response){
  						if (response.status){
  							notify('success', gettext('Success'), gettext("Key deleted !"));
  							var keys_table = $('#keys').dataTable();

  							var nodes = keys_table.fnGetNodes();
							for (var i in nodes){
								var d = keys_table.fnGetData(nodes[i]);
								if (d.id === aData.id){
									var pos = keys_table.fnGetPosition(nodes[i]);
									keys_table.fnDeleteRow(pos);
									break;
								}
							}

							for (var i in keys){
								if (keys[i].id == aData.id){
									keys.splice(i, 1);
									break;
								}
							}

  						} else {
  							notify('error', gettext('Error'), response.error);
  						}
  					}
  				)
	    	})	    		
    	})

    	$(nRow).click(function(){
    		var table = $('#keys').dataTable();
    		var nodes = table.fnGetNodes();

    		if (table.fnIsOpen(nRow)){
    			table.fnClose(nRow);
    			return false;
    		}

    		for (var node of nodes)
    			table.fnClose(node);

    		if (aData['informations'] === "")
    			return;

		    var sOut = '<b>Information:</b><br/><p>'+aData['informations']+"</p>";
    		table.fnOpen(nRow, sOut, 'details' );
		    return sOut;
    	})
    }
})

$('#import-keepass-form').on('submit', function(e){
	e.stopPropagation();
	e.preventDefault();
})


$('#workspaces-select').on('change', function(){
	var table = $('#keys').dataTable();
	table.fnClearTable();

	// close_websocket();
	workspace_vue.folders = [];
	$('#tree').jstree("destroy").empty();

	var workspace_id = $(this).val();
	if (workspace_id !== null)
		workspace_vue.get_tree(workspace_id);
})
$('#workspaces-select').trigger('change');

$('#form_passphrase').on('submit', function(){
	var text = $("#submit-passphrase").html();
	$("#submit-passphrase").html("<i class='fa fa-spinner fa-spin'></i>");
	$('#error-passphrase').hide();

	$.post(
		'/passphrase/', {
			passphrase         : $('#passphrase').val(),
			csrfmiddlewaretoken: getCookie('csrftoken'),
			workspace_id       : $('#workspaces-select').val()
		},

		function(response){
			$("#passphrase").val("");
			$("#submit-passphrase").html(text);

			if (response.status){
				$('#passphrase-modal').modal('hide');
				localStorage.setItem('passphrase', response.passphrase);
				workspace_vue.get_tree($('#workspaces-select').val());

			} else {
				$('#error-passphrase').html(response.error);
				$('#error-passphrase').show();
			}
		}
	)
});

$('#open-history').on('click', function(){
	if ($(this).data('open') === 'true'){
		$('.tl-history').css('right', '250px');
		$(this).find('i')[0].removeClass('fa-chevron-right');
		$(this).find('i')[0].addClass('fa-chevron-left');
		$(this).data('open', 'false');
	} else {
		$('.tl-history').css('right', '0');
		$(this).find('i')[0].removeClass('fa-chevron-left');
		$(this).find('i')[0].addClass('fa-chevron-right');
		$(this).data('open', 'true');
	}
})

var isResizing = false;
var container  = $('.tl-main'),
	tree       = $('.tl-tree'),
	content    = $('.tl-content'),
	handle     = $('#dragbar');

handle.on('mousedown', function (e) {
    isResizing = true;
    lastDownX = e.clientX;
});

$(document).on('mousemove', function (e) {
    // we don't want to do anything if we aren't resizing.
    if (!isResizing) 
        return;

	var tree_width    = $(tree).width();
	var content_width = $(content).width();

	var new_tree_width = (e.clientX);

	if (new_tree_width < 250)
		new_tree_width = 250;

	var new_content_width = content_width + (new_tree_width - tree_width)


    tree.css('width', new_tree_width);
    content.css('marginLeft', new_tree_width);
}).on('mouseup', function (e) {
    // stop resizing
    isResizing = false;
});


var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));

elems.forEach(function(html) {
  var switchery = new Switchery(html);
});
