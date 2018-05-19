var test = ""
var next = 0;
function set_test(val)
{
  test=val
}

function show_test()
{
  var addto = "#field" + next
  var addRemove = "#field" + (next)
  next = next + 1
  var newIn = '<div id="field'+next+'">\n<fieldset>\n<label for="application_prep_stages_ids">\{\{ _("models.application_creation.select.preprocessing") \}\}</label>\n<select class="form-control" id="application" name="application_prep_stages_ids">{% for method in data_prep_methods %}          <option value={{ str(method["id"]) }}>{{ method["template_name"] }}</option>{% end %}</select>    </fieldset><fieldset><input class="text-input" id="{{ \'application_prep_stages_config_1\''+next+' }}" name="{{ \'application_prep_stages_config_\''+next+' }}"></input></fieldset><br></div>'
  var newInput = $(newIn);
  var removeBtn = '<button id="remove' + (next - 1) + '" class="btn btn-danger remove-me" >Remove</button></div></div><div id="field">';
  var removeButton = $(removeBtn);
  $(addto).after(newInput);
  $(addRemove).after(removeButton);
  $("#field" + next).attr('data-source',$(addto).attr('data-source'));
  $("#count").val(next);

  $('.remove-me').click(function(e){
    e.preventDefault();
    var fieldNum = this.id.charAt(this.id.length-1);
    var fieldID = "#field" + fieldNum;
    $(this).remove();
    $(fieldID).remove();
  });
  alert(test);
}


// $(document).ready(function () {
//     //@naresh action dynamic childs
//     var next = 0;
//     $("#add-more-preprocessing").click(function(e){
//         e.preventDefault();
//         var addto = "#field" + next;
//         var addRemove = "#field" + (next);
//         next = next + 1;
//         var data_prep_methods = {{ data_prep_methods|safe }}
//         console.log(data_prep_methods)
//         var newIn = '<div id="field'+next+'">\n<fieldset>\n<label for="application_prep_stages_ids">\{\{ _("models.application_creation.select.preprocessing") \}\}</label>\n<select class="form-control" id="application" name="application_prep_stages_ids">{% for method in data_prep_methods %}          <option value={{ str(method["id"]) }}>{{ method["template_name"] }}</option>{% end %}</select>    </fieldset><fieldset><input class="text-input" id="{{ \'application_prep_stages_config_1\''+next+' }}" name="{{ \'application_prep_stages_config_\''+next+' }}"></input></fieldset><br></div>';
//         var newInput = $(newIn);
//         var removeBtn = '<button id="remove' + (next - 1) + '" class="btn btn-danger remove-me" >Remove</button></div></div><div id="field">';
//         var removeButton = $(removeBtn);
//         $(addto).after(newInput);
//         $(addRemove).after(removeButton);
//         $("#field" + next).attr('data-source',$(addto).attr('data-source'));
//         $("#count").val(next);
//
//             $('.remove-me').click(function(e){
//                 e.preventDefault();
//                 var fieldNum = this.id.charAt(this.id.length-1);
//                 var fieldID = "#field" + fieldNum;
//                 $(this).remove();
//                 $(fieldID).remove();
//             });
//     });
//
// });
