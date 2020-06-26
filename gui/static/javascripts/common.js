
function get_passphrase(first){
  var passphrase = localStorage.getItem('passphrase');
  if (passphrase === null){

    // window.location.href = window.location.href;
    /*$('#passphrase-modal').modal('show');
    $('#error-passphrase').hide();*/
    return false;
  }

  return passphrase;
}