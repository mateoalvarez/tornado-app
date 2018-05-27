function visualizeData(button){
    $.ajax({
        url: "/running_applications/visualize?app_name=" + $(button).val(),
        type: "GET"
    })
}
