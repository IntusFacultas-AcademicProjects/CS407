
// modal related functions
var showSuccessMessage = function(message) {
    /*
        Shows success message DOM element for UX.
    */
    $.confirm({
        title: 'Success!',
        closeIcon: true, 
        content: message,
        type: 'green',
        typeAnimated: true,
        autoClose:'close|3000',
        buttons: {
            close: {
                text: 'Close',
                btnClass: 'btn-green',
                action: function () {
                },
            }
        }
    });
};

var showErrorMessage = function(message) {
    $.confirm({
        title: 'Error',
        closeIcon: true, 
        content: message,
        type: 'red',
        typeAnimated: true,
        backgroundDismiss: true,
        autoClose: 'close|3000',
        buttons: {
            close: {
                text: 'Close',
                btnClass: 'btn-red',
                action: function(){
                }
            }
        }
    });
};

var formHandle = function(e) {
    /*
        Simulates form submittal on enter press.
    */
    if(e.keyCode === 13){
        app.signInForm();
    }
};

var changeHandle = function(e) {
    if (e.keyCode === 13) {
        app.changeQuestion();
    }
}