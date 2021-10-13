/* jshint esversion: 6 */
/*
This file includes the business logic and workflow for a user-agent surfing aTLAS.
 */

let scenarioSelector = $("#selector-scenario");
let labSocket;

function openLabSocket() {
    let ws_scheme = window.location.protocol === "https:" ? "wss://" : "ws://";
    labSocket = new WebSocket(ws_scheme + window.location.host + LAB_URL);
    labSocket.onmessage = onLabSocketMessage;
    labSocket.onclose = onLabSocketClose;
}

function onLabSocketClose(closingEvent){
    let socketClosedMsg = 'Lab socket closed unexpectedly!';
    snackMessage(true, socketClosedMsg);
    console.error(socketClosedMsg);
    console.error(closingEvent);
}

function onLabSocketMessage(messageEvent){
    /**
     * @typedef {Object} webSocketMsg
     * @property {string} type
     * @property {string} scenario_run_id
     * @property {string} trust_log
     * @property {string} agents_log
     * @property {string} message
     */
    /** @type {webSocketMsg} */
    let data = JSON.parse(messageEvent.data);
    if (data.type === "scenario_results") {
        $("#trust_log").text(data.trust_log);
        let agents_log = JSON.parse(data.agents_log);
        let agents_log_end = $("#agents_log_end");
        let currentRunId = data.scenario_run_id;
        for (const [key, value] of Object.entries(agents_log)) {
            agents_log_end.before(`<p class="agent_log">Agent '${key}' trust log:</p>`);
            agents_log_end.before(`<pre id="agent_log_${key}" class="agent_log">${value}</pre>`);
        }
        if (inRuntimeState()) {
            $("#c-runtime").addClass("not-displayed");
            $("#c-results").removeClass("not-displayed");
        } else if (inGetResultsState()) {
            showScenarioRunId(currentRunId);
            $("#c-loadingResults").addClass("not-displayed");
            $("#c-results").removeClass("not-displayed");
        }
    } else if (data.type === "scenario_run_id") {
        showScenarioRunId(data.scenario_run_id);
    } else if (data.type === "scenario_result_error") {
        cancelScenarioResults();
        snackMessage(true, data.message);
    } else if (data.type === "error") {
        snackMessage(true, data.message);
    }
}

function startLabRuntime() {
    let scenarioName = scenarioSelector.children("option:selected").val();
    if (scenarioName !== "")
    {
        let scenario = scenarios.filter(scenario => scenario.name === scenarioName)[0];
        let scenarioMessage = {'type': 'run_scenario', 'scenario': scenario};
        waitForSocketConnection(labSocket, function(){
            labSocket.send(JSON.stringify(scenarioMessage));
            openLabRuntimeCard();
        }, function(){
            snackMessage(true, "No socket connection ready");
            openLabSocket();
        });
    }
    else
    {
        errorInTextfield(scenarioSelector);
        snackMessage(true);
    }
}

function getScenarioResult() {
    let scenarioRunIdInput = $("#scenario_run_id_pick");
    let scenarioRunId = scenarioRunIdInput.val();
    if (isValidScenarioRunId(scenarioRunId)) {
        $("#c-pick-results").addClass("not-displayed");
        $("#c-loadingResults").removeClass("not-displayed");
        sendScenarioRunIdForResults(scenarioRunId);
    }
    else
    {
        errorInTextfield(scenarioRunIdInput);
        snackMessage(true);
    }
}

function sendScenarioRunIdForResults(scenarioRunId) {
    waitForSocketConnection(labSocket, function(){
        let scenarioResultMessage = {'type': 'get_scenario_results', 'scenario_run_id': scenarioRunId};
        labSocket.send(JSON.stringify(scenarioResultMessage));
    }, function(){
        snackMessage(true, "No socket connection ready, automatic retry");
        openLabSocket();
        if (inGetResultsState()) {
            sendScenarioRunIdForResults(scenarioRunId);
        }
    });
}

function showScenarioRunId(scenarioRunId) {
    let baseURL = window.location.href.split('#')[0];
    let currentRunUrl = `${baseURL}#${scenarioRunId}`;
    let idCopyField = $("#scenario_run_id_copyField");
    let urlCopyField = $("#scenario_run_url_copyField");
    let idCopyFieldResults = $("#scenario_run_id_copyField_results");
    let urlCopyFieldResults = $("#scenario_run_url_copyField_results");
    idCopyField.val(scenarioRunId);
    idCopyField.parent().addClass("is-dirty");
    urlCopyField.val(currentRunUrl);
    urlCopyField.parent().addClass("is-dirty");
    idCopyFieldResults.val(scenarioRunId);
    idCopyFieldResults.parent().addClass("is-dirty");
    urlCopyFieldResults.val(currentRunUrl);
    urlCopyFieldResults.parent().addClass("is-dirty");
    $("#results_header").text("Results for " + scenarioRunId);
    history.pushState(null, null, '#' + scenarioRunId);
    // 57em is the current maximum for #share-dialog with length 72em
    let newCopyFieldLength = (currentRunUrl.length/2 <= 57) ? currentRunUrl.length/2 : 57;
    $(".trustlab-copy-field").css("width", `${newCopyFieldLength}em`);
}

function clearScenarioRunId() {
    let idCopyField = $("#scenario_run_id_copyField");
    let urlCopyField = $("#scenario_run_url_copyField");
    let idCopyFieldResults = $("#scenario_run_id_copyField_results");
    let urlCopyFieldResults = $("#scenario_run_url_copyField_results");
    idCopyField.val("");
    idCopyField.parent().removeClass("is-dirty");
    urlCopyField.val("");
    urlCopyField.parent().removeClass("is-dirty");
    idCopyFieldResults.val("");
    idCopyFieldResults.parent().removeClass("is-dirty");
    urlCopyFieldResults.val("");
    urlCopyFieldResults.parent().removeClass("is-dirty");
    $("#results_header").text("Results");
    removeUrlFragement();
}

function openSpecifyScenarioCard() {
    $("#c-start").addClass("not-displayed");
    $("#c-scenario").removeClass("not-displayed");
}

function openPickScenarioResultsCard() {
    $("#c-start").addClass("not-displayed");
    $("#c-pick-results").removeClass("not-displayed");
}

function openSpecifyScenarioCardFromResults() {
    $(".agent_log").remove();
    clearScenarioRunId();
    $("#c-results").addClass("not-displayed");
    $("#c-scenario").removeClass("not-displayed");
}

function openPickScenarioResultsCardFromResults() {
    $(".agent_log").remove();
    clearScenarioRunId();
    $("#c-results").addClass("not-displayed");
    $("#c-pick-results").removeClass("not-displayed");
}

function openLabRuntimeCard() {
    $("#c-scenario").addClass("not-displayed");
    $("#c-runtime").removeClass("not-displayed");
}

function showScenarioDescription() {
    let value = scenarioSelector.children("option:selected").val();
    let scenarioDetails = $('#scenario-details');
    if (scenarioDetails.hasClass("not-displayed")) {
        scenarioDetails.removeClass("not-displayed");
    } else if (value === "" && !scenarioDetails.hasClass("not-displayed")){
        scenarioDetails.addClass("not-displayed");
    }
    $(".scenario-ul:not(.not-displayed)").addClass("not-displayed");
    $(".scenario-ul[data-scenario='"+value+"']").removeClass("not-displayed");
}

function cancelScenarioResults() {
    $("#c-loadingResults").addClass("not-displayed");
    $("#c-start").removeClass("not-displayed");
    removeUrlFragement();
}

function cancelSpecifyScenario() {
    $("#c-scenario").addClass("not-displayed");
    $("#c-start").removeClass("not-displayed");
}

function cancelPickResults() {
    $("#c-pick-results").addClass("not-displayed");
    $("#c-start").removeClass("not-displayed");
}

function inGetResultsState() {
    return !$("#c-loadingResults").hasClass("not-displayed");
}

function inRuntimeState() {
    return !$("#c-runtime").hasClass("not-displayed");
}

function isValidScenarioRunId(scenarioRunId) {
    let idPattern = /^scenarioRun_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}_[0-9]{3}$/;
    return idPattern.test(scenarioRunId);
}


//OnClick Events
$("#btn-specify-scenario").click(openSpecifyScenarioCard);
$("#btn-pick-results").click(openPickScenarioResultsCard);
$("#btn-pick-results2").click(openPickScenarioResultsCardFromResults);
$("#btn-run-scenario").click(startLabRuntime);
$("#btn-get-results").click(getScenarioResult);
$("#btn-specify-scenario2").click(openSpecifyScenarioCardFromResults);
$("#btn-cancel-scenario-results").click(cancelScenarioResults);
$("#btn-cancel-pick").click(cancelPickResults);
$("#btn-cancel-specify").click(cancelSpecifyScenario);
let shareDialog = $("#share-dialog")[0];
$(".btn-share-results").click(function() {
    shareDialog.showModal();
    /* Or dialog.show(); to show the dialog without a backdrop. */
  });
$("#close-share-dialog").click(function() {
    shareDialog.close();
  });
let aboutDialog = $("#about-dialog")[0];
$("#btn-about-dialog").click(function() {
    aboutDialog.showModal();
    /* Or dialog.show(); to show the dialog without a backdrop. */
  });
$("#close-about-dialog").click(function() {
    aboutDialog.close();
  });
scenarioSelector.change(showScenarioDescription);

// using r function for correct ready state
// explained at http://stackoverflow.com/a/30319853/1214237
function r(f){/in/.test(document.readyState)?setTimeout('r('+f+')',9):f()} // jshint ignore:line
r(function(){
    // dynamic URL changes for deploy with enabled ProxyPass
    $("#header-index-anchor").attr("href", window.location.pathname);
    if (scenario_load_error) {
        snackMessage(true, scenario_load_error);
    }
    openLabSocket();
    if(window.location.hash) {
        let scenarioRunId = window.location.hash.substring(1);
        if (isValidScenarioRunId(scenarioRunId)) {
            $("#c-start").addClass("not-displayed");
            $("#c-loadingResults").removeClass("not-displayed");
            sendScenarioRunIdForResults(scenarioRunId);
        } else {
            snackMessage(true, 'Given Scenario ID in URL hash is invalid or not found.');
        }
    }
});



