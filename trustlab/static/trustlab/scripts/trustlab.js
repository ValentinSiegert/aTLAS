/* jshint esversion: 6 */
/*
This file includes the business logic and workflow for a user-agent surfing aTLAS.
 */

let scenarioSelector = $("#selector-scenario");
let labSocket;

function openLabSocket() {
    labSocket = new WebSocket('ws://' + window.location.host + LAB_URL);
    labSocket.onmessage = onLabSocketMessage;
    labSocket.onclose = onLabSocketClose;
}

function onLabSocketClose(closingEvent){
    console.error('Lab socket closed unexpectedly!');
}

function onLabSocketMessage(messageEvent){
    let data = JSON.parse(messageEvent.data);
    if (data.status === 200)
    {
        $("#trust_log").text(data.trust_log);
        let agents_log = JSON.parse(data.agents_log);
        let agents_log_end = $("#agents_log_end");
        for (const [key, value] of Object.entries(agents_log)) {
            agents_log_end.before(`<p class="agent_log">Agent '${key}' trust log:</p>`);
            agents_log_end.before(`<pre id="agent_log_${key}" class="agent_log">${value}</pre>`);
        }
    }
    $("#c-runtime").addClass("not-displayed");
    $("#c-results").removeClass("not-displayed");
}

function openSpecifyScenarioCard() {
    $("#c-start").addClass("not-displayed");
    $("#c-scenario").removeClass("not-displayed");
}

function openSpecifyScenarioCardFromResults() {
    $(".agent_log").remove();
    $("#c-results").addClass("not-displayed");
    $("#c-scenario").removeClass("not-displayed");
}

function startLabRuntime() {
    let scenarioName = scenarioSelector.children("option:selected").val();
    if (scenarioName !== "")
    {
        let scenario = scenarios.filter(scenario => scenario.name === scenarioName)[0];
        // old ajax call
        // ajaxFunc(INDEX_URL,"PUT", JSON.stringify(scenario), openLabRuntimeCard, "html");
        if (labSocket.readyState === 1){
            labSocket.send(JSON.stringify(scenario));
            openLabRuntimeCard();
        }
        else
        {
            snackMessage(true, "No socket connection ready");
            openLabSocket();
        }
    }
    else
    {
        errorInTextfield(scenarioSelector);
        snackMessage(true);
    }
}

function openLabRuntimeCard() {
    $("#c-scenario").addClass("not-displayed");
    $("#c-runtime").removeClass("not-displayed");
    // setTimeout(function(){
    //     $("#c-runtime").addClass("not-displayed");
    //     $("#c-results").removeClass("not-displayed");
    // }, 2000);
}

function showScenarioDescription() {
    let value = scenarioSelector.children("option:selected").val();
    $(".scenario-ul:not(.not-displayed)").addClass("not-displayed");
    $(".scenario-ul[data-scenario='"+value+"']").removeClass("not-displayed");
}


//OnClick Events
$("#btn-specify-scenario").click(openSpecifyScenarioCard);
$("#btn-run-scenario").click(startLabRuntime);
$("#btn-specify-scenario2").click(openSpecifyScenarioCardFromResults);
scenarioSelector.change(showScenarioDescription);

$( document ).ready(function() {
    openLabSocket();
});



