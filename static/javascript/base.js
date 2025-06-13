//Close Bootstrap Message after a few seconds 
setTimeout(function () {
    let alertNode = document.querySelector('.alert');
    if (alertNode) {
      let bsAlert = bootstrap.Alert.getOrCreateInstance(alertNode);
      bsAlert.close();
    }
  }, 4000);