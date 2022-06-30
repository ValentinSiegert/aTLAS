/* jshint esversion: 6 */
/*
This file includes miscellaneous JS functions for the trustlab aTLAS.
 */

function snackMessage(isErrorMsg = false, message = "", action = null, actionText = "Got it") {
    const GENERAL_ERROR_MSG = "Something went wrong. Please try again.";
    const GENERAL_SUCCESS_MSG = "Success!";
    if (message === "")
    {
        message = isErrorMsg ? GENERAL_ERROR_MSG: GENERAL_SUCCESS_MSG;
    }
    /**
     * @typedef {Object} snackBarMDL
     * @property {Object} MaterialSnackbar
     * @property {function} showSnackbar
     */
    /** @type {snackBarMDL} */
    let snack = document.querySelector("#snack");
    let snack_icon = $("#snack_icon");
    let snack_action = $("#snack_action");
    if (isErrorMsg)
    {
        snack_icon.text("cancel");
        snack_icon.css("color", "#FE2B36");
        snack_action.css("color", "#FE2B36");
    }
    else
    {
        snack_icon.text("check_circle");
        snack_icon.css("color", "#29EB36");
        snack_action.css("color", "#29EB36");
    }
    let data = {
      message: message,
      timeout: 3000,
      actionHandler: action,
      actionText: actionText
    };
    snack.MaterialSnackbar.showSnackbar(data);
}

function errorInTextfield(selector, message = "")
{
    if (message !== "")
    {
        selector.parent().children("span.mdl-selectfield__error").text(message);
    }
    selector.parent().addClass("is-invalid is-dirty");
}

function copy_text_to_clipboard(input_id)
{
    let copyText = document.getElementById(input_id);
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
}

// got original function from https://stackoverflow.com/a/21394730
function waitForSocketConnection(socket, callback, error_callback, waitCounter=0){
    setTimeout(
        function () {
            if (socket.readyState === 1) {
                if (callback !== null){
                    callback();
                }
            } else if (waitCounter > 9) {
                if (error_callback !== null) {
                    error_callback();
                }
            } else {
                waitCounter++;
                waitForSocketConnection(socket, callback, waitCounter);
            }
        }, 5); // wait 5 milliseconds for the connection...
}

function removeUrlFragement() {
    if(window.location.hash) {
        history.pushState(null, null, '#');
    }
}

// Thanks to https://stackoverflow.com/a/2648463
String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

let aboutDialog = $("#about-dialog")[0];
$("#btn-about-dialog").click(function() {
    aboutDialog.showModal();
    /* Or dialog.show(); to show the dialog without a backdrop. */
  });
$("#close-about-dialog").click(function() {
    aboutDialog.close();
  });

// unused functions, kept for potential re-usage

// function ajaxFunc(url, method, data, successHandler, dataType = "json", contentType = "application/json") {
//         $.ajax({
//             url: url,
//             method: method,
//             beforeSend: function (xhr, settings) {
//                 if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
//                     xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
//                 }
//                 return true;
//             },
//             dataType: dataType,
//             contentType: contentType,
//             data: data,
//             success: function (result) {
//                 successHandler(result);
//             },
//             error: function () {
//                 snackMessage(true);
//             }
//         });
// }
//
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         let cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             let cookie = jQuery.trim(cookies[i]);
//             // Does this cookie string begin with the name we want?
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
