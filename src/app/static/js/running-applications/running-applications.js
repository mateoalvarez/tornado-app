
function downloadData(button){
    console.log(" downloadData -> aqui veo " + $(button).val())
    $.ajax({
        url: "/running_applications/visualize",
        type: "POST",
        data: {
            app_name:$('button').val()
        }
    })
}

function visualizeData(button){
    console.log(" visualizeData -> aqui veo " + $(button).val())
    $.ajax({
        url: "/running_applications/visualize?app_name=" + $(button).val(),
        type: "GET"
    })
}
