//Close Bootstrap Message after 2 seconds 
setTimeout(function () {
    let alertNode = document.querySelector('.alert');
    if (alertNode) {
      let bsAlert = bootstrap.Alert.getOrCreateInstance(alertNode);
      bsAlert.close();
    }
  }, 2000);