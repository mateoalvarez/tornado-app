
function downloadData(button){
    $.ajax({
        url: "/running_applications/visualize",
        type: "POST",
        data: {
            application_id:button
        }
    })
}

function visualizeData(button){
    $.ajax({
        url: "/running_applications/visualize?app_name=" + $(button).val(),
        type: "GET"
    })
}
